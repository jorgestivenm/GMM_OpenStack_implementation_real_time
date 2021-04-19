import configparser
import os
import sys
import time

from pylibpcap.base import Sniff
# root_folder = os.path.abspath(
#   os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(root_folder)
from shared import iface, localstore, parentdir

config = configparser.ConfigParser()


def SniffAndSave(timeout=10):
    config.read(localstore)
    count = int(config['SNIFFER']['Count'])
    sniffobj = Sniff(
        iface, count=-1, promisc=1,
        out_file=f"{parentdir}/captures/capture_{count}.pcap")
    tic = time.time()
    start = True
    while True:
        try:
            if start:
                StartSniff(sniffobj)
                start = False
            toc = time.time()
            if toc - tic >= timeout:
                tic = time.time()
                sniffobj.close()
                count += 1
                sniffobj = Sniff(
                    iface, count=-1, promisc=1,
                    out_file=f"{parentdir}/captures/capture_{count}.pcap")
                start = True
                config['SNIFFER']['Count'] = str(count)
                f = open(localstore, 'w')
                config.write(f)
                f.close()
                # stats = sniffobj.stats()
                # print(stats.capture_cnt, " packets captured")
                # print(stats.ps_recv, " packets received by filter")
                # print(stats.ps_drop, "  packets dropped by kernel")
                # print(stats.ps_ifdrop, "  packets dropped by iface")
        except Exception as e:
            print(e)


def StartSniff(sniffer):
    sniffer.capture()


if __name__ == '__main__':
    SniffAndSave(timeout=60)
