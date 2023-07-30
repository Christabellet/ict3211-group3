import os
import pandas as pd

PATH_TO_CSV = "./output/"




def categorize_filename_traffic(filename):
    filename = filename.lower().replace(".pcap_flow.csv", "")

    prefix_label_dict = {
        # Chat
        "discord2023_chat_1": 0,
        "discord2023_chat_2": 0,
        "discord2023_chat_3": 0,
        "teams_chat": 0,

        # Email
        "email1a": 1,
        "email1b": 1,
        "email2a": 1,
        "email2b": 1,

        # File Transfer
        "discord2023_download_1": 2,
        "discord2023_upload_1": 2,
        "ftps_down_1a": 2,
        "ftps_down_1b": 2,
        "ftps_up_2a": 2,
        "ftps_up_2b": 2,
        "sftp1": 2,
        "sftp_down_3a": 2,
        "sftp_down_3b": 2,
        "sftp_up_2a": 2,
        "sftp_up_2b": 2,
        "sftpdown1": 2,
        "sftpdown2": 2,
        "sftpup1": 2,
        "teams_download_upload_chat": 2,
        "teams_downloads": 2,
        "teams_uploads": 2,

        # Streaming
        "netflix2023_1": 3,
        "netflix2023_2": 3,
        "netflix2023_3": 3,
        "spotify2023_1": 3,
        "spotify2023_2": 3,
        "vimeo2023_1": 3,
        "youtube2023_1": 3,
        "youtube2023_2": 3,

        # VoIP
        "discord2023_audio_1": 4,
        "discord2023_audio_video_1": 4,
        "teams2023_audio_video_1": 4,

        # Gaming
        "csgo2023_1": 5,
        "netflixgame": 5,
        "valorant2023_1": 5
    }
    

    return prefix_label_dict[filename]


def categorize_filename_application(filename):
    filename = filename.lower()
    category_list = ["aim", "facebook", "ftps", "gmail", "hangout", "icq", "scp", "sftp", "skype", "spotify", "vimeo", "voipbuster", "youtube", "netflix"]

    for category in category_list:
        if category in filename:
            return category
    
    return None


def main():
    # Extract selected features from csv
    selected_columns = ['Src IP', 'Src Port', 'Dst IP', 'Dst Port', 'Protocol', 
                        'Flow Duration', 'Flow Byts/s', 'Flow Pkts/s', 'Flow IAT Mean', 'Flow IAT Std', 
                        'Flow IAT Max', 'Flow IAT Min', 'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max', 
                        'Fwd IAT Min', 'Bwd IAT Mean', 'Bwd IAT Std', 'Bwd IAT Max', 'Bwd IAT Min', 
                        'Active Mean', 'Active Std', 'Active Max', 'Active Min', 'Idle Mean', 'Idle Std', 
                        'Idle Max', 'Idle Min']
    
    compiled_data = []
    # Get category of file
    for root, dirs, files in os.walk(PATH_TO_CSV):
        for file in files:           
            filepath = os.path.join(root, file)
            if filepath.endswith('.csv'):
                category = categorize_filename_traffic(file)
                df = pd.read_csv(filepath, usecols=selected_columns)
                df['Label'] = category
                compiled_data.append(df)

    # Combine all dataframes
    df = pd.concat(compiled_data)

    # Write to the compiled CSV
    df.to_csv('compiled.csv', index=False)


if __name__ == "__main__":
    main()