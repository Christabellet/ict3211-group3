# Python CICFlowMeter Feature Extractor

This python script is designed to use subprocess to run CICFlowMeter with java to extract flow data from pcap files. Before the extraction of flow data, it converts pcapng to pcap using tshark(if any) to ensure compatibility with CICFlowMeter.

## Requirements
- Python 3.x
- Java (JDK or JRE)
- tshark (part of the Wireshark distribution)

Note: Ensure that Java and tshark are added to your system's PATH.

## How to use

1. Place your pcap/pcapng files in the `./dataset/` directory.
2. Run `python <filename.py>` to start the extraction process.

## Script Overview

The script follows these steps:
1. Walks through the `./dataset/` directory and its subdirectories.
2. Converts any `.pcapng` files found to `.pcap` files using tshark.
3. Uses CICFlowMeter to extract features from the `.pcap` files.

### Function `convert_pcapng_to_pcap(filepath, filename, output_directory=".")`
Takes a `.pcapng` file and converts it to a `.pcap` file using tshark. The resulting file is saved to the `output_directory` with the same name as the input file, but with a `.pcap` extension.

### Function `extract_features(filename, output_directory="output")`
Takes a `.pcap` file and extracts features using CICFlowMeter. The resulting file is saved to the `output_directory`.

## Logging
CICFlowMeter can auto-detect pcap files within a directory but stops when an error occurs. As such, error files are ignored as it makes up a small percentage of the dataset

The script provides basic verbose output of the extraction process. Each file is reported as it completes, or if it encounters an error during processing.

There is no custom logging implemented in this python file but CICFlowMeter logs all files received and processed.


# Network Traffic Labeller

This Python script processes CSV files generated from network traffic and categorizes them based on their traffic type such as Email, Chat, Streaming, File Transfer, VoIP, P2P. VPN based categories are also handled.

The script focuses on some specific applications and services such as Firefox, Chrome, SMTP, POP3S, IMAPS, ICQ, AIM, Facebook, Hangouts, Vimeo, YouTube, Skype, FTPS, SFTP, uTorrent, Transmission (BitTorrent).

## Requirements
- Python 3.x
- Pandas

## How to use

1. Place your CSV files in the `./output/` directory.
2. Run `python <filename.py>` to start the data processing.

## Script Overview

The script works as follows:
1. Walks through the `./output/` directory and its subdirectories.
2. Reads each CSV file and extracts selected network traffic features.
3. Categorizes the CSV files based on filenames.
4. Appends a new column 'Label' to each dataframe with the category as its value.
5. Combines all dataframes and saves to a new CSV file 'compiled.csv'.
