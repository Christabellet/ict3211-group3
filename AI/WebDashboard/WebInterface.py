from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import csv
from werkzeug.utils import secure_filename
#from prediction import deep_packet_predict


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
    

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    return "PCAP" # To remove
    
    # # Process the uploaded file and save the processed data as a new CSV file
    # processed_filename = deep_packet_predict(os.path.join(app.config['UPLOAD_FOLDER'], filename), app.config['PROCESSED_FOLDER'])

    # # Read the CSV file into a list of dictionaries
    # csv_data = []
    # with open(processed_filename, 'r') as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     for row in reader:
    #         csv_data.append(row)

    # # Redirect to the route that displays the contents of the processed CSV file
    # return render_template('display.html', data=csv_data)


if __name__ == '__main__':
    # Create the upload folder if it does not exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Create the processed folder if it does not exist
    if not os.path.exists(PROCESSED_FOLDER):
        os.makedirs(PROCESSED_FOLDER)

    app.run(debug=True)