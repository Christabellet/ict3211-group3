import pickle
import numpy as np
import pandas as pd
import datetime
from sklearn import preprocessing

def read_flow_csv(filepath):
    # Load the CSV file
    df = pd.read_csv(filepath)

    # Specify the columns to select
    selected_columns = ['Src IP', 'Src Port', 'Dst IP', 'Dst Port', 'Protocol', 
                        'Flow Duration', 'Flow Byts/s', 'Flow Pkts/s', 'Flow IAT Mean', 'Flow IAT Std', 
                        'Flow IAT Max', 'Flow IAT Min', 'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max', 
                        'Fwd IAT Min', 'Bwd IAT Mean', 'Bwd IAT Std', 'Bwd IAT Max', 'Bwd IAT Min', 
                        'Active Mean', 'Active Std', 'Active Max', 'Active Min', 'Idle Mean', 'Idle Std', 
                        'Idle Max', 'Idle Min']
    
    return df[selected_columns].copy()

def model_processing(df):
    # Remove 5-tuple
    new_df = df.iloc[:, 5:].copy()

    return new_df

def predict_pcap(csvfilepath, filename):
    df = read_flow_csv(csvfilepath)

    # Replace "inf" with numpy.nan
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df.dropna()

    five_tuple = df.iloc[:, :5].copy()
    new_df = df.iloc[:, 5:].copy()
    
    # Normalise values
    x = new_df.copy()
    min_max_scaler = preprocessing.MinMaxScaler()
    x = min_max_scaler.fit_transform(x)

    with open('./flow_predict_src/flow_RF_model.pkl', 'rb') as file:
        model = pickle.load(file)

    y_pred = model.predict(x)

    label_dict = {
        0: "Chat",
        1: "Email",
        2: "File Transfer",
        3: "Streaming",
        4: "VoIP",
        5: "Gaming"
    }

    # Convert labels
    converted_labels = [label_dict[label] for label in y_pred]
    
    five_tuple['Traffic Label'] = converted_labels

    # Get the current date and time
    now = datetime.datetime.now()

    # Format the date and time as a string
    now_str = now.strftime("%Y-%m-%d_%H-%M-%S")

    filename = filename.replace(".pcap", "")

    new_filepath = f"processed/{filename}_{now_str}_result.csv"

    # Rename columns
    column_names = {
        'Src IP': 'Source IP',
        'Src Port': 'Source Port',
        'Dst IP': 'Destination IP',
        'Dst Port': 'Destination Port',
        'Protocol': 'Protocol'
    }

    # Rename the columns
    five_tuple.rename(columns=column_names, inplace=True)

    five_tuple.to_csv(f"{new_filepath}")
    return new_filepath

    
