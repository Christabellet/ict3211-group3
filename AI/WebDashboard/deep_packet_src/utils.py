from pathlib import Path

from scapy.layers.dns import DNS
from scapy.layers.inet import TCP
from scapy.packet import Padding
from scapy.utils import PcapReader

# for app identification
PREFIX_TO_APP_ID = {
    # csgo
    "csgo2023_1": 0,
    # discord
    "discord2023_audio_1": 1,
    "discord2023_audio_video_1": 1,
    "discord2023_chat_1": 1,
    "discord2023_chat_2": 1,
    "discord2023_chat_3": 1,
    "discord2023_download_1": 1,
    "discord2023_upload_1": 1,
    # Email, ISCX2016 dataset
    "email1a": 2,
    "email1b": 2,
    "email2a": 2,
    "email2b": 2,
    # FTPS, ISCX2016 dataset
    "ftps_down_1a": 3,
    "ftps_down_1b": 3,
    "ftps_up_2a": 3,
    "ftps_up_2b": 3,
    # Netflix
    "netflix2023_1": 4,
    "netflix2023_2": 4,
    "netflix2023_3": 4,
    "netflixgame": 4,
    # SFTP
    "sftp1": 5,
    "sftp_down_3a": 5,
    "sftp_down_3b": 5,
    "sftp_up_2a": 5,
    "sftp_up_2b": 5,
    "sftpdown1": 5,
    "sftpdown2": 5,
    "sftpup1": 5,
    # Spotify
    "spotify2023_1": 6,
    "spotify2023_2": 6,
    # Teams
    "teams_chat": 7,
    "teams_download_upload_chat": 7,
    "teams_download": 7,
    "teams_upload": 7,
    "teams2023_audio_video_1": 7,
    # Valorant
    "valorant2023_1": 8,
    # Vimeo
    "vimeo2023_1": 9,
    # Youtube
    "youtube2023_1": 10,
    "youtube2023_2": 10,
}

ID_TO_APP = {
    0: "CSGO",
    1: "Discord",
    2: "Email",
    3: "FTPS",
    4: "Netflix",
    5: "SFTP",
    6: "Spotify",
    7: "Teams",
    8: "Valorant",
    9: "Vimeo",
    10: "Youtube"
}

PREFIX_TO_TRAFFIC_ID = {
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
    "teams_download": 2,
    "teams_upload": 2,
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

ID_TO_TRAFFIC = {
    0: "Chat",
    1: "Email",
    2: "File Transfer",
    3: "Streaming",
    4: "Voip",
    5: "Gaming"
}

PREFIX_TO_APP_ID_OLD = {
    # AIM chat
    "aim_chat_3a": 0,
    "aim_chat_3b": 0,
    "aimchat1": 0,
    "aimchat2": 0,
    # Email
    "email1a": 1,
    "email1b": 1,
    "email2a": 1,
    "email2b": 1,
    # Facebook
    "facebook_audio1a": 2,
    "facebook_audio1b": 2,
    "facebook_audio2a": 2,
    "facebook_audio2b": 2,
    "facebook_audio3": 2,
    "facebook_audio4": 2,
    "facebook_chat_4a": 2,
    "facebook_chat_4b": 2,
    "facebook_video1a": 2,
    "facebook_video1b": 2,
    "facebook_video2a": 2,
    "facebook_video2b": 2,
    "facebookchat1": 2,
    "facebookchat2": 2,
    "facebookchat3": 2,
    # FTPS
    "ftps_down_1a": 3,
    "ftps_down_1b": 3,
    "ftps_up_2a": 3,
    "ftps_up_2b": 3,
    # Gmail
    "gmailchat1": 4,
    "gmailchat2": 4,
    "gmailchat3": 4,
    # Hangouts
    "hangout_chat_4b": 5,
    "hangouts_audio1a": 5,
    "hangouts_audio1b": 5,
    "hangouts_audio2a": 5,
    "hangouts_audio2b": 5,
    "hangouts_audio3": 5,
    "hangouts_audio4": 5,
    "hangouts_chat_4a": 5,
    "hangouts_video1b": 5,
    "hangouts_video2a": 5,
    "hangouts_video2b": 5,
    # ICQ
    "icq_chat_3a": 6,
    "icq_chat_3b": 6,
    "icqchat1": 6,
    "icqchat2": 6,
    # Netflix
    "netflix2023_1": 7,
    # SCP
    "scp1": 8,
    "scpdown1": 8,
    "scpdown2": 8,
    "scpdown3": 8,
    "scpdown4": 8,
    "scpdown5": 8,
    "scpdown6": 8,
    "scpup1": 8,
    "scpup2": 8,
    "scpup3": 8,
    "scpup5": 8,
    "scpup6": 8,
    # SFTP
    "sftp1": 9,
    "sftp_down_3a": 9,
    "sftp_down_3b": 9,
    "sftp_up_2a": 9,
    "sftp_up_2b": 9,
    "sftpdown1": 9,
    "sftpdown2": 9,
    "sftpup1": 9,
    # Skype
    "skype_audio1a": 10,
    "skype_audio1b": 10,
    "skype_audio2a": 10,
    "skype_audio2b": 10,
    "skype_audio3": 10,
    "skype_audio4": 10,
    "skype_chat1a": 10,
    "skype_chat1b": 10,
    "skype_file1": 10,
    "skype_file2": 10,
    "skype_file3": 10,
    "skype_file4": 10,
    "skype_file5": 10,
    "skype_file6": 10,
    "skype_file7": 10,
    "skype_file8": 10,
    "skype_video1a": 10,
    "skype_video1b": 10,
    "skype_video2a": 10,
    "skype_video2b": 10,
    # Spotify
    "spotify2023_1": 11,
    "spotify2023_2": 11,
    # Vimeo
    "vimeo2023_1": 12,
    # Voipbuster
    "voipbuster1b": 13,
    "voipbuster2b": 13,
    "voipbuster3b": 13,
    "voipbuster_4a": 13,
    "voipbuster_4b": 13,
    # Youtube
    "youtube2023_1": 14,
    "youtube2023_2": 14,
}

ID_TO_APP_OLD = {
    0: "AIM Chat",
    1: "Email",
    2: "Facebook",
    3: "FTPS",
    4: "Gmail",
    5: "Hangouts",
    6: "ICQ",
    7: "Netflix",
    8: "SCP",
    9: "SFTP",
    10: "Skype",
    11: "Spotify",
    12: "Vimeo",
    13: "Voipbuster",
    14: "Youtube",
}

# for app identification
PREFIX_TO_APP_ID_VNAT = {
    # netflix
    "nonvpn_netflix_capture1": 0,
    "nonvpn_netflix_capture2": 0,
    # RDP
    "nonvpn_rdp_capture1": 1,
    "nonvpn_rdp_capture2": 1,
    "nonvpn_rdp_capture3": 1,
    "nonvpn_rdp_capture4": 1,
    "nonvpn_rdp_capture5": 1,
    # rsync
    "nonvpn_rsync_capture1": 2,
    "nonvpn_rsync_newcapture1": 2,
    # SCP
    "nonvpn_scp_capture1": 3,
    "nonvpn_scp_long_capture1": 3,
    "nonvpn_scp_newcapture1": 3,
    # SFTP
    "nonvpn_sftp_capture1": 4,
    "nonvpn_sftp_capture2": 4,
    "nonvpn_sftp_capture3": 4,
    "nonvpn_sftp_newcapture1": 4,
    "nonvpn_sftp_newcapture2": 4,
    # Skype
    "nonvpn_skype-chat_capture1": 5,
    "nonvpn_skype-chat_capture2": 5,
    "nonvpn_skype-chat_capture3": 5,
    "nonvpn_skype-chat_capture4": 5,
    "nonvpn_skype-chat_capture5": 5,
    "nonvpn_skype-chat_capture6": 5,
    "nonvpn_skype-chat_capture7": 5,
    "nonvpn_skype-chat_capture8": 5,
    "nonvpn_skype-chat_capture9": 5,
    "nonvpn_skype-chat_capture10": 5,
    "nonvpn_skype-chat_capture11": 5,
    "nonvpn_skype-chat_capture12": 5,
    "nonvpn_skype-chat_capture13": 5,
    "nonvpn_skype-chat_capture14": 5,
    "nonvpn_skype-chat_capture15": 5,
    "nonvpn_skype-chat_capture16": 5,
    "nonvpn_skype-chat_capture17": 5,
    "nonvpn_skype-chat_capture18": 5,
    "nonvpn_skype-chat_capture19": 5,
    "nonvpn_skype-chat_capture20": 5,
    "nonvpn_skype-chat_capture21": 5,
    "nonvpn_skype-chat_capture22": 5,
    "nonvpn_skype-chat_capture23": 5,
    "nonvpn_skype-chat_capture24": 5,
    "nonvpn_skype-chat_capture25": 5,
    "nonvpn_skype-chat_capture26": 5,
    "nonvpn_skype-chat_capture27": 5,
    "nonvpn_skype-chat_capture28": 5,
    "nonvpn_skype-chat_capture29": 5,
    "nonvpn_skype-chat_capture30": 5,
    "nonvpn_skype-chat_capture31": 5,
    "nonvpn_skype-chat_capture32": 5,
    "nonvpn_skype-chat_capture33": 5,
    "nonvpn_skype-chat_capture34": 5,
    "nonvpn_skype-chat_capture35": 5,
    "nonvpn_skype-chat_capture36": 5,
    "nonvpn_skype-chat_capture37": 5,
    "nonvpn_skype-chat_capture38": 5,
    "nonvpn_skype-chat_capture39": 5,
    "nonvpn_skype-chat_capture40": 5,
    "nonvpn_skype-chat_capture41": 5,
    "nonvpn_skype-chat_capture42": 5,
    "nonvpn_skype-chat_capture43": 5,
    "nonvpn_skype-chat_capture44": 5,
    "nonvpn_skype-chat_capture45": 5,
    "nonvpn_skype-chat_capture46": 5,
    "nonvpn_skype-chat_capture47": 5,
    "nonvpn_skype-chat_capture48": 5,
    "nonvpn_skype-chat_capture49": 5,
    "nonvpn_skype-chat_capture50": 5,
    "nonvpn_skype-chat_capture51": 5,
    "nonvpn_skype-chat_capture52": 5,
    "nonvpn_skype-chat_capture53": 5,
    "nonvpn_skype-chat_capture54": 5,
    # SSH
    "nonvpn_ssh_capture1": 6,
    "nonvpn_ssh_capture2": 6,
    "nonvpn_ssh_capture3": 6,
    "nonvpn_ssh_capture4": 6,
    "nonvpn_ssh_capture5": 6,
    # Vimeo
    "nonvpn_vimeo_capture1": 7,
    # Zoiper (VOIP)
    "nonvpn_voip_capture1": 8,
    "nonvpn_voip_capture2": 8,
    "nonvpn_voip_capture3": 8,
    # YouTube
    "nonvpn_youtube_capture1": 9,
    "nonvpn_youtube_capture2": 9,
    "nonvpn_youtube_capture3": 9,
    "nonvpn_youtube_capture4": 9,
}

ID_TO_APP_VNAT = {
    0: "Netflix",
    1: "RDP",
    2: "RSYNC",
    3: "SCP",
    4: "SFTP",
    5: "Skype",
    6: "SSH",
    7: "Vimeo",
    8: "Zoiper",
    9: "Youtube",
}

# for traffic identification
PREFIX_TO_TRAFFIC_ID_OLD = {
    # Chat
    "aim_chat_3a": 0,
    "aim_chat_3b": 0,
    "aimchat1": 0,
    "aimchat2": 0,
    "facebook_chat_4a": 0,
    "facebook_chat_4b": 0,
    "facebookchat1": 0,
    "facebookchat2": 0,
    "facebookchat3": 0,
    "gmailchat1": 0,
    "gmailchat2": 0,
    "gmailchat3": 0,
    "hangout_chat_4b": 0,
    "hangouts_chat_4a": 0,
    "icq_chat_3a": 0,
    "icq_chat_3b": 0,
    "icqchat1": 0,
    "icqchat2": 0,
    "skype_chat1a": 0,
    "skype_chat1b": 0,
    # Email
    "email1a": 1,
    "email1b": 1,
    "email2a": 1,
    "email2b": 1,
    # File Transfer
    "ftps_down_1a": 2,
    "ftps_down_1b": 2,
    "ftps_up_2a": 2,
    "ftps_up_2b": 2,
    "scp1": 2,
    "scpdown1": 2,
    "scpdown2": 2,
    "scpdown3": 2,
    "scpdown4": 2,
    "scpdown5": 2,
    "scpdown6": 2,
    "scpup1": 2,
    "scpup2": 2,
    "scpup3": 2,
    "scpup5": 2,
    "scpup6": 2,
    "sftp1": 2,
    "sftp_down_3a": 2,
    "sftp_down_3b": 2,
    "sftp_up_2a": 2,
    "sftp_up_2b": 2,
    "sftpdown1": 2,
    "sftpdown2": 2,
    "sftpup1": 2,
    "skype_file1": 2,
    "skype_file2": 2,
    "skype_file3": 2,
    "skype_file4": 2,
    "skype_file5": 2,
    "skype_file6": 2,
    "skype_file7": 2,
    "skype_file8": 2,
    # Streaming
    "netflix2023_1": 3,
    "netflix2023_2": 3,
    "spotify2023_1": 3,
    "spotify2023_2": 3,
    "vimeo2023_1": 3,
    "youtube2023_1": 3,
    "youtube2023_2": 3,
    # VoIP
    "facebook_audio1a": 4,
    "facebook_audio1b": 4,
    "facebook_audio2a": 4,
    "facebook_audio2b": 4,
    "facebook_audio3": 4,
    "facebook_audio4": 4,
    "facebook_video1a": 4,
    "facebook_video1b": 4,
    "facebook_video2a": 4,
    "facebook_video2b": 4,
    "hangouts_audio1a": 4,
    "hangouts_audio1b": 4,
    "hangouts_audio2a": 4,
    "hangouts_audio2b": 4,
    "hangouts_audio3": 4,
    "hangouts_audio4": 4,
    "hangouts_video1b": 4,
    "hangouts_video2a": 4,
    "hangouts_video2b": 4,
    "skype_audio1a": 4,
    "skype_audio1b": 4,
    "skype_audio2a": 4,
    "skype_audio2b": 4,
    "skype_audio3": 4,
    "skype_audio4": 4,
    "skype_video1a": 4,
    "skype_video1b": 4,
    "skype_video2a": 4,
    "skype_video2b": 4,
    "voipbuster1b": 4,
    "voipbuster2b": 4,
    "voipbuster3b": 4,
    "voipbuster_4a": 4,
    "voipbuster_4b": 4,
    # # VPN: Chat
    # "vpn_aim_chat1a": 5,
    # "vpn_aim_chat1b": 5,
    # "vpn_facebook_chat1a": 5,
    # "vpn_facebook_chat1b": 5,
    # "vpn_hangouts_chat1a": 5,
    # "vpn_hangouts_chat1b": 5,
    # "vpn_icq_chat1a": 5,
    # "vpn_icq_chat1b": 5,
    # "vpn_skype_chat1a": 5,
    # "vpn_skype_chat1b": 5,
    # # VPN: File Transfer
    # "vpn_ftps_a": 6,
    # "vpn_ftps_b": 6,
    # "vpn_sftp_a": 6,
    # "vpn_sftp_b": 6,
    # "vpn_skype_files1a": 6,
    # "vpn_skype_files1b": 6,
    # # VPN: Email
    # "vpn_email2a": 7,
    # "vpn_email2b": 7,
    # # VPN: Streaming
    # "vpn_netflix_a": 8,
    # "vpn_spotify_a": 8,
    # "vpn_vimeo_a": 8,
    # "vpn_vimeo_b": 8,
    # "vpn_youtube_a": 8,
    # # VPN: Torrent
    # "vpn_bittorrent": 9,
    # # VPN VoIP
    # "vpn_facebook_audio2": 10,
    # "vpn_hangouts_audio1": 10,
    # "vpn_hangouts_audio2": 10,
    # "vpn_skype_audio1": 10,
    # "vpn_skype_audio2": 10,
    # "vpn_voipbuster1a": 10,
    # "vpn_voipbuster1b": 10,
}

ID_TO_TRAFFIC_OLD = {
    0: "Chat",
    1: "Email",
    2: "File Transfer",
    3: "Streaming",
    4: "Voip",
    # 5: "VPN: Chat",
    # 6: "VPN: File Transfer",
    # 7: "VPN: Email",
    # 8: "VPN: Streaming",
    # 9: "VPN: Torrent",
    # 10: "VPN: Voip",
}

PREFIX_TO_TRAFFIC_ID_VNAT = {
    # netflix
    "nonvpn_netflix_capture1": 0,
    "nonvpn_netflix_capture2": 0,
    # RDP
    "nonvpn_rdp_capture1": 3,
    "nonvpn_rdp_capture2": 3,
    "nonvpn_rdp_capture3": 3,
    "nonvpn_rdp_capture4": 3,
    "nonvpn_rdp_capture5": 3,
    # rsync
    "nonvpn_rsync_capture1": 4,
    "nonvpn_rsync_newcapture1": 4,
    # SCP
    "nonvpn_scp_capture1": 4,
    "nonvpn_scp_long_capture1": 4,
    "nonvpn_scp_newcapture1": 4,
    # SFTP
    "nonvpn_sftp_capture1": 4,
    "nonvpn_sftp_capture2": 4,
    "nonvpn_sftp_capture3": 4,
    "nonvpn_sftp_newcapture1": 4,
    "nonvpn_sftp_newcapture2": 4,
    # Skype
    "nonvpn_skype-chat_capture1": 2,
    "nonvpn_skype-chat_capture2": 2,
    "nonvpn_skype-chat_capture3": 2,
    "nonvpn_skype-chat_capture4": 2,
    "nonvpn_skype-chat_capture5": 2,
    "nonvpn_skype-chat_capture6": 2,
    "nonvpn_skype-chat_capture7": 2,
    "nonvpn_skype-chat_capture8": 2,
    "nonvpn_skype-chat_capture9": 2,
    "nonvpn_skype-chat_capture10": 2,
    "nonvpn_skype-chat_capture11": 2,
    "nonvpn_skype-chat_capture12": 2,
    "nonvpn_skype-chat_capture13": 2,
    "nonvpn_skype-chat_capture14": 2,
    "nonvpn_skype-chat_capture15": 2,
    "nonvpn_skype-chat_capture16": 2,
    "nonvpn_skype-chat_capture17": 2,
    "nonvpn_skype-chat_capture18": 2,
    "nonvpn_skype-chat_capture19": 2,
    "nonvpn_skype-chat_capture20": 2,
    "nonvpn_skype-chat_capture21": 2,
    "nonvpn_skype-chat_capture22": 2,
    "nonvpn_skype-chat_capture23": 2,
    "nonvpn_skype-chat_capture24": 2,
    "nonvpn_skype-chat_capture25": 2,
    "nonvpn_skype-chat_capture26": 2,
    "nonvpn_skype-chat_capture27": 2,
    "nonvpn_skype-chat_capture28": 2,
    "nonvpn_skype-chat_capture29": 2,
    "nonvpn_skype-chat_capture30": 2,
    "nonvpn_skype-chat_capture31": 2,
    "nonvpn_skype-chat_capture32": 2,
    "nonvpn_skype-chat_capture33": 2,
    "nonvpn_skype-chat_capture34": 2,
    "nonvpn_skype-chat_capture35": 2,
    "nonvpn_skype-chat_capture36": 2,
    "nonvpn_skype-chat_capture37": 2,
    "nonvpn_skype-chat_capture38": 2,
    "nonvpn_skype-chat_capture39": 2,
    "nonvpn_skype-chat_capture40": 2,
    "nonvpn_skype-chat_capture41": 2,
    "nonvpn_skype-chat_capture42": 2,
    "nonvpn_skype-chat_capture43": 2,
    "nonvpn_skype-chat_capture44": 2,
    "nonvpn_skype-chat_capture45": 2,
    "nonvpn_skype-chat_capture46": 2,
    "nonvpn_skype-chat_capture47": 2,
    "nonvpn_skype-chat_capture48": 2,
    "nonvpn_skype-chat_capture49": 2,
    "nonvpn_skype-chat_capture50": 2,
    "nonvpn_skype-chat_capture51": 2,
    "nonvpn_skype-chat_capture52": 2,
    "nonvpn_skype-chat_capture53": 2,
    "nonvpn_skype-chat_capture54": 2,
    # SSH
    "nonvpn_ssh_capture1": 3,
    "nonvpn_ssh_capture2": 3,
    "nonvpn_ssh_capture3": 3,
    "nonvpn_ssh_capture4": 3,
    "nonvpn_ssh_capture5": 3,
    # Vimeo
    "nonvpn_vimeo_capture1": 0,
    # Zoiper (VOIP)
    "nonvpn_voip_capture1": 1,
    "nonvpn_voip_capture2": 1,
    "nonvpn_voip_capture3": 1,
    # YouTube
    "nonvpn_youtube_capture1": 1,
    "nonvpn_youtube_capture2": 1,
    "nonvpn_youtube_capture3": 1,
    "nonvpn_youtube_capture4": 1,
}

ID_TO_TRAFFIC_VNAT = {
    0: "Streaming",
    1: "VoIP",
    2: "Chat",
    3: "Command and Control",
    4: "File Transfer",
    5: "VPN: Streaming",
    6: "VPN: VoIP",
    7: "VPN: Chat",
    8: "VPN: Command and Control",
    9: "VPN: File Transfer",
}


def read_pcap(path: Path):
    packets = PcapReader(str(path))

    return packets


def should_omit_packet(packet):
    # SYN, ACK or FIN flags set to 1 and no payload
    if TCP in packet and (packet.flags & 0x13):
        # not payload or contains only padding
        layers = packet[TCP].payload.layers()
        if not layers or (Padding in layers and len(layers) == 1):
            return True

    # DNS segment
    if DNS in packet:
        return True

    return False
