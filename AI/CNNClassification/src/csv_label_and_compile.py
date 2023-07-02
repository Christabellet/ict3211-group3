import os
import pandas as pd

PATH_TO_CSV = "./output/"

# Web browsing      Firefox and Chrome
# Email             SMTP, POP3S, and IMAPS
# Chat              ICQ, AIM, Facebook, and Hangouts
# Streaming         Vimeo and YouTube
# File Transfer     Skype, FTPS, and SFTP using FileZilla and an external service 
# VoIP              Facebook, Skype, and Hangouts voice calls (duration for 1 hour)
# P2P               uTorrent and Transmission (BitTorrent)
# VPN Web browsing  Firefox and Chrome
# VPN Email         SMTP, POP3S, and IMAPS
# VPN Chat          ICQ, AIM, Facebook, and Hangouts
# VPN Streaming     Vimeo and YouTube
# VPN File Transfer Skype, FTPS, and SFTP using FileZilla and an external service 
# VPN VoIP          Facebook, Skype, and Hangouts voice calls (duration for 1 hour)
# VPN P2P           uTorrent and Transmission (BitTorrent)


def categorize_filename_default(filename):
    filename = filename.lower()
    keywords = {
        #"Web browsing": [],
        "Email": ["email"],
        "Chat": ["aimchat", "aim_chat", "facebook_chat","hangouts_chat", "facebookchat", "gmailchat", "icq_chat", "icqchat", "skype_chat", "hangout_chat"],
        "Streaming": ["youtube", "vimeo", "netflix", "spotify"],
        "File Transfer": ["ftps", "scp", "sftp", "skype_file"],
        "VoIP": ["facebook_audio", "hangouts_audio", "hangouts_video", "skype_video", "facebook_video", "voipbuster", "skype_audio"],
        "P2P": ["bittorrent"],
    }

    result = None
    
    for category, keys in keywords.items():
        if any(key in filename for key in keys):
            result = category
            break

    if "vpn" in filename and result:
        result = "VPN " + result

    return result


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
                category = categorize_filename_default(filepath)
                df = pd.read_csv(filepath, usecols=selected_columns)
                if category is None:
                    continue

                df['Label'] = category
                compiled_data.append(df)

    # Combine all dataframes
    df = pd.concat(compiled_data)

    # Write to the compiled CSV
    df.to_csv('compiled.csv', index=False)

if __name__ == "__main__":
    main()