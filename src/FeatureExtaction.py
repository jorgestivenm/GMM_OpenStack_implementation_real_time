
import configparser
import glob
import os
import sys

from cicflowmeter.sniffer import create_sniffer
from shared import localstore, parentdir

# root_folder = os.path.abspath(os.path.dirname(
#     os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(root_folder)


config = configparser.ConfigParser()

capturedir = parentdir + '/captures'


def FeatureExtraction():
    input_interface = None
    output_mode = 'flow'
    url_model = None
    while True:
        config.read(localstore)
        count = int(config['SNIFFER']['Count'])
        for filepath in glob.glob(os.path.join(capturedir, '*.pcap')):
            try:
                input_file = filepath
                if input_file != os.path.join(
                    capturedir, f'capture_{count}.pcap'
                    ) and input_file != os.path.join(
                        capturedir, f'capture_{count + 1}.pcap'
                        ):
                    output = filepath.replace(
                        'captures', 'features'
                        ).replace('capture', 'flow').replace('.pcap', '.csv')
                    sniffer = create_sniffer(
                            input_file,
                            input_interface,
                            output_mode,
                            output,
                            url_model,
                        )
                    sniffer.start()

                    try:
                        sniffer.join()
                    except KeyboardInterrupt:
                        sniffer.stop()
                    finally:
                        sniffer.join()
                    os.remove(filepath)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    FeatureExtraction()
