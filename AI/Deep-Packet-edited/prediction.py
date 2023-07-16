import os
import sys
from pathlib import Path
from collections import Counter

import multiprocessing

import click
import datasets
from datasets import Dataset, DatasetDict
import psutil
import numpy as np
import pandas as pd
import gzip
import json
import csv

from joblib import Parallel, delayed
from scapy.compat import raw
from scapy.layers.inet import IP, UDP, TCP
from scapy.layers.l2 import Ether
from scapy.packet import Padding
from scipy import sparse

from ml.utils import load_application_classification_cnn_model, load_traffic_classification_cnn_model
import torch
from torch.utils.data import DataLoader

from pyspark.sql import SparkSession

from utils import should_omit_packet, read_pcap, ID_TO_APP, ID_TO_TRAFFIC


def remove_ether_header(packet):
    if Ether in packet:
        return packet[Ether].payload

    return packet


def mask_ip(packet):
    if IP in packet:
        packet[IP].src = "0.0.0.0"
        packet[IP].dst = "0.0.0.0"

    return packet


def pad_udp(packet):
    if UDP in packet:
        # get layers after udp
        layer_after = packet[UDP].payload.copy()

        # build a padding layer
        pad = Padding()
        pad.load = "\x00" * 12

        layer_before = packet.copy()
        layer_before[UDP].remove_payload()
        packet = layer_before / pad / layer_after

        return packet

    return packet


def packet_to_sparse_array(packet, max_length=1500):
    arr = np.frombuffer(raw(packet), dtype=np.uint8)[0:max_length] / 255
    if len(arr) < max_length:
        pad_width = max_length - len(arr)
        arr = np.pad(arr, pad_width=(0, pad_width), constant_values=0)

    arr = sparse.csr_matrix(arr)
    return arr


def transform_packet(packet):
    if should_omit_packet(packet):
        return None

    # extract the 5 tuple
    if IP in packet:
        src_ip = None
        src_port = None
        dst_ip = None
        dst_port = None
        protocol = None

        if packet.haslayer(IP):
            ip_layer = packet[IP]
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            protocol = ip_layer.proto

            if packet.haslayer(TCP):
                tcp_layer = packet[TCP]
                src_port = tcp_layer.sport
                dst_port = tcp_layer.dport
            elif packet.haslayer(UDP):
                udp_layer = packet[UDP]
                src_port = udp_layer.sport
                dst_port = udp_layer.dport
    else:
        return None

    packet = remove_ether_header(packet)
    packet = pad_udp(packet)
    packet = mask_ip(packet)

    arr = packet_to_sparse_array(packet)
    five_tuple_list = [src_ip, src_port, dst_ip, dst_port, protocol]

    return five_tuple_list, arr


def transform_pcap(path, output_path: Path = None, output_batch_size=10000):
    if Path(str(output_path.absolute()) + "_SUCCESS").exists():
        print(output_path, "Done")
        return

    print("Processing", path)

    rows = []
    five_tuple_rows = []
    batch_index = 0
    for i, packet in enumerate(read_pcap(path)):
        result = transform_packet(packet)
        if result is not None:
            five_tuple, arr = result
            five_tuple_rows.append(five_tuple)
            row = {
                "feature": arr.todense().tolist()[0],
            }
            rows.append(row)

    # initialise local spark
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    memory_gb = psutil.virtual_memory().available // 1024 // 1024 // 1024
    spark = (
        SparkSession.builder.master("local[*]")
        .config("spark.driver.memory", f"{memory_gb}g")
        .config("spark.driver.host", "127.0.0.1")
        .getOrCreate()
    )

    df = spark.createDataFrame(pd.DataFrame(rows))
    # print(df.show())
    df = df.toPandas()
    # print("type: ")
    # print(type(df))

    return df, five_tuple_rows


def custom_collate_function(batch):
    feature = torch.stack([torch.tensor([data["feature"]]) for data in batch])
    label = "TESTING"
    transformed_batch = {"feature": feature, "label": label}
    return transformed_batch


@click.command()
@click.option(
    "-s",
    "--source",
    help="path to the directory containing raw pcap files",
    required=True,
)
@click.option(
    "-t",
    "--target",
    help="path to the directory for persisting preprocessed files",
    required=True,
)
@click.option("-n", "--njob", default=-1, help="num of executors", type=int)
def main(source, target, njob):
    data_dir_path = Path(source)
    target_dir_path = Path(target)
    target_dir_path.mkdir(parents=True, exist_ok=True)

    if njob == 1:
        for pcap_path in sorted(data_dir_path.iterdir()):
            transformed = transform_pcap(
                pcap_path, target_dir_path / (pcap_path.name + ".transformed")
            )
    else:
        transformed = zip(*Parallel(n_jobs=njob)(
            delayed(transform_pcap)(
                pcap_path, target_dir_path / (pcap_path.name + ".transformed")
            )
            for pcap_path in sorted(data_dir_path.iterdir())
        ))

    # print(type(transformed))
    # print(transformed)
    df, five_tuple = transformed

    # model path
    application_classification_cnn_model_path = 'model/new_application_classification.cnn.model'
    app_model = load_application_classification_cnn_model(
        application_classification_cnn_model_path,
        gpu=False)

    traffic_classification_cnn_model_path = 'model/new_traffic_classification.cnn.model'
    traffic_model = load_traffic_classification_cnn_model(
        traffic_classification_cnn_model_path,
        gpu=False)

    print(app_model.eval())
    print("App model loaded in")

    print(traffic_model.eval())
    print("Traffic model loaded in")
    # print(df)
    # print(type(df))

    # for item in df:
    #     print(item[0])
    #     print(type(item[0]))
    #     print(item[1])
    #     print(type(item[1]))

    dataset = Dataset.from_pandas(df)

    try:
        num_workers = multiprocessing.cpu_count()
    except:
        num_workers = 1
    dataloader = DataLoader(
        dataset,
        batch_size=2048,
        num_workers=num_workers,
        collate_fn=custom_collate_function,
    )

    print("length of dataloader")
    print(len(dataloader))

    total_preds_app = []
    total_preds_traffic = []

    for batch in dataloader:
        x_app = batch["feature"].float().to(app_model.device)
        x_traffic = batch["feature"].float().to(traffic_model.device)

        with torch.no_grad():

            y_pred_app = app_model(x_app)
            y_pred_traffic = traffic_model(x_traffic)

            # for k = 1
            _, preds_app = torch.max(y_pred_app, 1)
            _, preds_traffic = torch.max(y_pred_traffic, 1)

            # for k = 3
            # test, preds = torch.topk(y_pred, k=3)

            # print("preds before numpy")
            # print(preds)

            preds_app = preds_app.cpu().numpy()
            preds_app = preds_app.tolist()

            preds_traffic = preds_traffic.cpu().numpy()
            preds_traffic = preds_traffic.tolist()

            # for k = 1
            total_preds_app = total_preds_app + preds_app
            total_preds_traffic = total_preds_traffic + preds_traffic

    print(len(total_preds_app))
    # print(total_preds)
    count_dict_app = Counter(total_preds_app)
    for label_app, count_app in count_dict_app.items():
        print("App Label: ", label_app, " Count: ", count_app)

    print(len(total_preds_traffic))
    count_dict_traffic = Counter(total_preds_traffic)
    for label_traffic, count_traffic in count_dict_traffic.items():
        print("Traffic Label: ", label_traffic, " Count: ", count_traffic)

    for i, row in enumerate(five_tuple):
        row.append(ID_TO_APP.get(total_preds_app[i]))
        row.append(ID_TO_TRAFFIC.get(total_preds_traffic[i]))

    # print(five_tuple)

    with open(target_dir_path / "output.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Source IP', 'Source Port', 'Destination IP', 'Destination Port', 'Protocol', 'App Label', 'Traffic Label'])
        writer.writerows(five_tuple)
    print("written to file")


if __name__ == "__main__":
    main()
