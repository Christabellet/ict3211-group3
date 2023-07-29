import os
import csv
import pandas as pd

from itertools import groupby
from flask import Flask, render_template, request, jsonify, redirect, url_for
from collections import Counter, defaultdict
from werkzeug.utils import secure_filename
from flow_predict_src import pcap_parser, preprocess_predict
from deep_packet_src import prediction


app = Flask(__name__)

# Define the folder to store the uploaded files and the processed files
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

ALLOWED_EXTENSIONS = {'pcap', 'pcapng'}


def check_pcap_or_pcapng(file_path):
    with open(file_path, "rb") as f:
        # Read the first 4 bytes of the file
        magic_number = f.read(4)

    # Compare the magic numbers
    if magic_number == b"\xd4\xc3\xb2\xa1":
        return "PCAP"
    elif magic_number == b"\x0a\x0d\x0d\x0a":
        return "PCAPNG"
    else:
        return False


def get_top_talkers(csv_filename, n=5):
    talkers = defaultdict(lambda: {'Frequency': 0, 'Traffic': '', 'App Label': ''})
    with open(csv_filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            source_ip = row['Source IP']
            destination_ip = row['Destination IP']
            talker_key = f'{source_ip} -> {destination_ip}'
            talkers[talker_key]['Frequency'] += 1
            if talkers[talker_key]['Frequency'] == 1:
                talkers[talker_key]['Traffic'] = row['Traffic Label']
                talkers[talker_key]['App Label'] = row['App Label']
            else:
                # If another row is found for the same talker, keep the most frequent Traffic and App Label
                if row['Traffic Label'] in ['P2P', 'File Transfer']:
                    talkers[talker_key]['Traffic'] = row['Traffic Label']
                if row['App Label']:
                    talkers[talker_key]['App Label'] = row['App Label']

    sorted_talkers = dict(sorted(talkers.items(), key=lambda item: item[1]['Frequency'], reverse=True)[:n])
    return sorted_talkers


def get_top_labels(df, ip_pair):
    # Filter the data for the given IP pair
    ip_pair_data = df[df["IP Pair"] == ip_pair]

    # Get the most common traffic label
    top_traffic_label = ip_pair_data["Traffic Label"].value_counts().idxmax()

    # Get the most common app label, if it exists
    # top_app_label = ip_pair_data["App Label"].value_counts().idxmax()
    if "App Label" in ip_pair_data.columns and not ip_pair_data["App Label"].empty:
        print("App label is not empty")
        top_app_label = ip_pair_data["App Label"].value_counts().idxmax()
    else:
        top_app_label = ""

    return top_traffic_label, top_app_label


def get_top_ip_combinations(csv_filename, n=5):
    # Load the data
    data = pd.read_csv(csv_filename)

    # Create a new column that combines the source and destination IPs
    data["IP Pair"] = data["Source IP"] + " - " + data["Destination IP"]

    # Group the data by the new column and count the occurrences of each pair
    ip_pair_counts = data["IP Pair"].value_counts()

    # Get the top n pairs
    top_ip_pairs = ip_pair_counts.head(n)
    top_ip_pairs = top_ip_pairs.reset_index().rename(columns={"count": "Frequency"})

    # Get the top traffic and app labels for each of the top n IP pairs
    for idx, row in top_ip_pairs.iterrows():
        top_traffic_label, top_app_label = get_top_labels(data, row["IP Pair"])
        top_ip_pairs.loc[idx, "Traffic"] = top_traffic_label
        top_ip_pairs.loc[idx, "App Label"] = top_app_label

    # Convert the DataFrame to a dictionary and return it
    top_talkers = top_ip_pairs.to_dict("records")
    return {talker["IP Pair"]: {"Frequency": talker["Frequency"], "Traffic": talker["Traffic"],
                                "Application": talker["App Label"]} for talker in top_talkers}


def get_label_percentages(csv_filename):
    # Load the data
    data = pd.read_csv(csv_filename)

    # Get the percentage of each traffic label
    traffic_label_percentages = data["Traffic Label"].value_counts(normalize=True).mul(100).round(
        2).to_dict() if "Traffic Label" in data.columns else "N/A"

    # Get the percentage of each app label
    app_label_percentages = data["App Label"].value_counts(normalize=True).mul(100).round(
        2).to_dict() if "App Label" in data.columns else ""

    return traffic_label_percentages, app_label_percentages


@app.route('/')
def index():
    return render_template('homepage.html')


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        uploaded_file  = request.files['file']
        filename = secure_filename(uploaded_file.filename)

        # Save the uploaded file to the specified folder
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(filepath)
    else:
        #abort(400)
        return jsonify({'error': 'No file part'})
        
    if uploaded_file == '':
        return jsonify({'error': 'No selected file'})

    if check_pcap_or_pcapng(filepath) == False:
        return jsonify({'error': 'Invalid file type. Only PCAP files are allowed.'})
    
    pcap_path = filepath
    if check_pcap_or_pcapng(filepath) == "PCAPNG":
        pcap_path = pcap_parser.convert_pcapng_to_pcap(filepath, filename, app.config['UPLOAD_FOLDER'])

    if request.form.get('function') == "flow":
        pcap_parser.extract_features(pcap_path, app.config['UPLOAD_FOLDER'])
        processed_filename = preprocess_predict.predict_pcap(pcap_path + "_Flow.csv", filename)
        # processed_filename = 'processed/SIT-WIFI_captureng_2023-07-29_18-39-10_result.csv'

    elif request.form.get('function') == "packet":
        # Process the uploaded file and save the processed data as a new CSV file
        try:
            processed_filename = prediction.deep_packet_predict(os.path.join(app.config['UPLOAD_FOLDER'], filename), app.config['PROCESSED_FOLDER'])
        except:
            processed_filename = ""
        # processed_filename = 'processed/SIT-WIFI_capture_2023-07-29_18-45-20_result.csv'
    # Read the CSV file into a list of dictionaries
    csv_data = []
    with open(processed_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            csv_data.append(row)

    # Get the top 5 talkers, source IPs, and destination IPs from the processed CSV file
    # top_talkers = get_top_talkers(processed_filename, n=5)
    top_ip_combinations = get_top_ip_combinations(processed_filename, n=5)
    traffic_label_percentages, app_label_percentages = get_label_percentages(processed_filename)

    # Redirect to the route that displays the contents of the processed CSV file
    return render_template('display.html',
                            data=csv_data,
                            filename=filename,
                            top_ip_combinations=top_ip_combinations,
                            app_label_percentages=app_label_percentages, 
                            traffic_label_percentages=traffic_label_percentages)


if __name__ == '__main__':
    # Create the upload folder if it does not exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Create the processed folder if it does not exist
    if not os.path.exists(PROCESSED_FOLDER):
        os.makedirs(PROCESSED_FOLDER)

    app.run(debug=True)