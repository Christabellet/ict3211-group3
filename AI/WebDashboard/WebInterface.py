from itertools import groupby

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import csv
from collections import Counter, defaultdict
from werkzeug.utils import secure_filename


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


def get_top_ip_combinations(csv_filename, n=5):
    ip_combinations = []
    with open(csv_filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            ip_combinations.append((row['Source IP'], row['Destination IP']))

    sorted_combinations = sorted(ip_combinations)
    ip_counts = {key: len(list(group)) for key, group in groupby(sorted_combinations)}

    top_combinations = dict(Counter(ip_counts).most_common(n))
    return top_combinations


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
    
    if check_pcap_or_pcapng(filepath) == "PCAPNG":
        # Convert to PCAP code here

        return "PCAPNG" # To remove
        pass
    
    # Extract flow from PCAP code here
    # return "PCAP" # To remove
    if request.form.get('function') == "flow":
        return "FLOW"

    elif request.form.get('function') == "packet":
        # Process the uploaded file and save the processed data as a new CSV file
        # processed_filename = deep_packet_predict(os.path.join(app.config['UPLOAD_FOLDER'], filename), app.config['PROCESSED_FOLDER'])
        processed_filename = 'processed/netflix_test_2023-07-24_10-37-40_result.csv'
        # Read the CSV file into a list of dictionaries
        csv_data = []
        with open(processed_filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_data.append(row)

        # Get the top 5 talkers, source IPs, and destination IPs from the processed CSV file
        top_talkers = get_top_talkers(processed_filename, n=5)
        top_ip_combinations = get_top_ip_combinations(processed_filename, n=5)

        # Redirect to the route that displays the contents of the processed CSV file
        return render_template('display.html',
                               data=csv_data,
                               filename=filename,
                               top_talkers=top_talkers,
                               top_ip_combinations=top_ip_combinations)


if __name__ == '__main__':
    # Create the upload folder if it does not exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Create the processed folder if it does not exist
    if not os.path.exists(PROCESSED_FOLDER):
        os.makedirs(PROCESSED_FOLDER)

    app.run(debug=True)