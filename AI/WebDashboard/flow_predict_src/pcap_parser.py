import subprocess
import os


def convert_pcapng_to_pcap(filepath, filename, output_directory="."):
    filename = filename.split(".")[0]
    output =  os.path.join(output_directory, f"{filename}.pcap")
    cmd = f'tshark -F pcap -r "{filepath}" -w {output}'
    subprocess.run(cmd, shell=True)
    return output


def extract_features(filename, output_directory="output"):
    command = (
        'java -Djava.library.path=./CICFlowMeter-4.0/lib/native'
        ' -cp ".\CICFlowMeter-4.0\lib\commons-io-2.5.jar;.\CICFlowMeter-4.0\lib\log4j-core-2.11.0.jar;'
        '.\CICFlowMeter-4.0\lib\slf4j-api-1.7.25.jar;.\CICFlowMeter-4.0\lib\jsr305-1.3.9.jar;'
        '.\CICFlowMeter-4.0\lib\commons-lang3-3.6.jar;.\CICFlowMeter-4.0\lib\commons-math3-3.5.jar;'
        '.\CICFlowMeter-4.0\lib\checker-compat-qual-2.0.0.jar;.\CICFlowMeter-4.0\lib\slf4j-log4j12-1.7.25.jar;'
        '.\CICFlowMeter-4.0\lib\jfreechart-1.5.0.jar;.\CICFlowMeter-4.0\lib\error_prone_annotations-2.1.3.jar;'
        '.\CICFlowMeter-4.0\lib\hamcrest-core-1.3.jar;.\CICFlowMeter-4.0\lib\j2objc-annotations-1.1.jar;'
        '.\CICFlowMeter-4.0\lib\log4j-1.2.17.jar;.\CICFlowMeter-4.0\lib\jnetpcap-1.4.1.jar;'
        '.\CICFlowMeter-4.0\lib\guava-23.6-jre.jar;.\CICFlowMeter-4.0\lib\log4j-api-2.11.0.jar;'
        '.\CICFlowMeter-4.0\lib\animal-sniffer-annotations-1.14.jar;./CICFlowMeter-4.0/lib/tika-core-1.17.jar;'
        '.\CICFlowMeter-4.0\lib\CICFlowMeter-4.0.jar;.\CICFlowMeter-4.0\lib\weka-stable-3.6.14.jar;'
        f'.\CICFlowMeter-4.0\lib\junit-4.12.jar;.\CICFlowMeter-4.0\lib\java-cup-0.11a.jar" cic.cs.unb.ca.ifm.Cmd {filename} {output_directory}'
    )

    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f'{filename} completed successfully')
    except subprocess.CalledProcessError as e:
        print(f'{filename} failed with error {e.returncode}')

def main():
    pass
    #extract_features("C:\Users\Wai Qun\Documents\Github\ICT3211 ITP\ict3211-group3\AI\WebDashboard\uploads\facebook_audio1b.pcap")

if __name__ == "__main__":
    main()
