import glob
import os
import sys

from scapy import *
from scapy.all import *
from scapy.utils import PcapReader, RawPcapReader, rdpcap, wrpcap

root_folder = os.path.abspath(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.append(root_folder)

from shared import iface, parentdir

ch_pkt = 0

pcapdir = parentdir + '/pcap'

def modifier(pkt):
    global ch_pkt
    try:
        if (pkt.haslayer(IP) == 1):
            ch_pkt += 1
            pkt[IP].dst = "192.168.100.112"
            del(pkt[IP].chksum)
            send(pkt)
    except Exception as e:
        print(e, len(pkt))


if __name__ == '__main__':
    packets = '/home/steven/Documents/UdeA/maestria/Tesis/Implementación/my_project/my_environment/code/implementation/WWPC_3.pcap'
    
    # map(modifier, packets)
    for filepath in glob(os.path.join(pcapdir, '*.pcap')):
        print(filepath)
        for p in rdpcap(filepath):
            if IP in p:
                print(f' SRC: {p[IP].src} - DST: {p[IP].dst}')
                send(p)
# sudo ifconfig enp7s0 mtu 9200 up
# sudo ifconfig virbr1 mtu 15000 up
