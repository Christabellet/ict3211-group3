from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import csv
from collections import Counter
from werkzeug.utils import secure_filename
from deep_packet_src.prediction import deep_packet_predict


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
    # Read the CSV file and calculate the frequency of each talker
    talker_frequency = Counter()
    with open(csv_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            talker_frequency[row['Source IP']] += 1
            talker_frequency[row['Destination IP']] += 1

    # Get the top n talkers
    top_talkers = talker_frequency.most_common(n)
    return top_talkers


def get_top_ips(csv_filename, field_name, n=5):
    # Read the CSV file and calculate the frequency of the given field (e.g., Source IP or Destination IP)
    field_frequency = Counter()
    with open(csv_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            field_frequency[row[field_name]] += 1

    # Get the top n IPs for the given field
    top_ips = field_frequency.most_common(n)
    return top_ips


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
        processed_filename = 'processed/YouTube_Afif_2023-07-24_02-28-24_result_TrafficOnly.csv'
        # Read the CSV file into a list of dictionaries
        csv_data = []
        with open(processed_filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_data.append(row)

        # Get the top 5 talkers, source IPs, and destination IPs from the processed CSV file
        top_talkers = get_top_talkers(processed_filename, n=5)
        top_source_ips = get_top_ips(processed_filename, 'Source IP', n=5)
        top_destination_ips = get_top_ips(processed_filename, 'Destination IP', n=5)

        # Redirect to the route that displays the contents of the processed CSV file
        return render_template('display.html',
                               data=csv_data,
                               filename=filename,
                               top_talkers=top_talkers,
                               top_source_ips=top_source_ips,
                               top_destination_ips=top_destination_ips)


if __name__ == '__main__':
    # Create the upload folder if it does not exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Create the processed folder if it does not exist
    if not os.path.exists(PROCESSED_FOLDER):
        os.makedirs(PROCESSED_FOLDER)

    app.run(debug=True)