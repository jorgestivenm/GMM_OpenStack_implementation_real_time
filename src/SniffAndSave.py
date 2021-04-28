import configparser
import os
import sys
import time

from cicflowmeter.sniffer import create_sniffer
from shared import iface, localstore, parentdir

config = configparser.ConfigParser()


def SniffAndSave(timeout=10):
    config.read(localstore)
    count = int(config['SNIFFER']['Count'])
    input_interface = iface
    output_mode = 'flow'
    url_model = None
    output = f"{parentdir}/features/flow_{count}.csv"
    input_file = None
    sniffobj = create_sniffer(
            input_file,
            input_interface,
            output_mode,
            output,
            url_model,
        )
    tic = time.time()
    start = True
    while True:
        try:
            if start:
                StartSniff(sniffobj)
                start = False
            toc = time.time()
            if toc - tic >= timeout:
                logger.info("Timeout, Stoping the current sniffer")
                tic = time.time()
                sniffobj.stop()
                count += 1
                sniffobj = create_sniffer(
                        input_file,
                        input_interface,
                        output_mode,
                        f"{parentdir}/features/flow_{count}.csv",
                        url_model,
                    )
                start = True
                config['SNIFFER']['Count'] = str(count)
                f = open(localstore, 'w')
                config.write(f)
                f.close()
        except Exception as e:
            print(e)


def StartSniff(sniffer):
    sniffer.start()
    logger.info("Stating a new Sniffer")


if __name__ == '__main__':
    SniffAndSave(timeout=60)
