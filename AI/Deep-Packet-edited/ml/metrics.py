import multiprocessing
from pathlib import Path

import datasets
import numpy as np
import torch
import pandas as pd
from torch.nn import functional as F
from torch.utils.data import DataLoader

from ml.dataset import dataset_collate_function


def confusion_matrix(data_path, model, num_class):
    data_path = Path(data_path)
    model.eval()

    cm = np.zeros((num_class, num_class), dtype=float)

    dataset_dict = datasets.load_dataset(str(data_path.absolute()), cache_dir="huggingface")
    # dataset_dict = datasets.load_from_disk(str(data_path.absolute()))

    # print(dataset_dict)

    dataset = dataset_dict[list(dataset_dict.keys())[0]]
    try:
        num_workers = multiprocessing.cpu_count()
    except:
        num_workers = 1
    dataloader = DataLoader(
        dataset,
        batch_size=1024,
        num_workers=num_workers,
        collate_fn=dataset_collate_function,
    )
    for batch in dataloader:
        x = batch["feature"].float().to(model.device)
        y = batch["label"].long()
        y_hat = torch.argmax(F.log_softmax(model(x), dim=1), dim=1)

        for i in range(len(y)):
            cm[y[i], y_hat[i]] += 1

    return cm


def get_precision(cm, i):
    tp = cm[i, i]
    tp_fp = cm[:, i].sum()

    return tp / tp_fp


def get_recall(cm, i):
    tp = cm[i, i]
    p = cm[i, :].sum()

    return tp / p


def get_false_positive(cm, i):
    fp = cm[:, i].sum() - cm[i, i]
    return fp


def get_true_positive(cm, i):
    tp = cm[i, i]
    return tp


def get_true_negative(cm, i):
    # Sum of all elements in the confusion matrix except for the i-th row and i-th column
    tn = cm.sum() - cm[i, :].sum() - cm[:, i].sum() + cm[i, i]
    return tn


def get_false_negative(cm, i):
    # Sum of the i-th row (excluding the i-th element)
    fn = cm[i, :].sum() - cm[i, i]
    return fn


def get_classification_report(cm, labels=None):
    rows = []
    for i in range(cm.shape[0]):
        precision = get_precision(cm, i)
        recall = get_recall(cm, i)
        true_positive = get_true_positive(cm, i)
        false_positive = get_false_positive(cm, i)
        false_negative = get_false_negative(cm, i)
        true_negative = get_true_negative(cm, i)
        if labels:
            label = labels[i]
        else:
            label = i

        row = {"label": label,
               "precision": precision,
               "recall": recall,
               "true positive": true_positive,
               "false positive": false_positive,
               "true negative": true_negative,
               "false negative": false_negative,
               }
        rows.append(row)

        # print("Current row: ")
        # print(row)

    return pd.DataFrame(rows)
