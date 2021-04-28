import os
import sys

from scapy import *
from scapy.all import *
from scapy.utils import RawPcapReader, rdpcap, wrpcap

root_folder = os.path.abspath(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.append(root_folder)

from shared import iface, parentdir


def modifier(pkt):
    try:
        if IP in pkt:
            if pkt[IP].dst == '192.168.10.50':
                pkt[IP].dst = "192.168.100.232"
                del(pkt[IP].chksum)
            elif pkt[IP].src == '192.168.10.50':
                pkt[IP].src = "192.168.100.232"
                del(pkt[IP].chksum)
            send(pkt, iface=iface)
        else:
            sendp(pkt, iface=iface)
    except Exception as e:
        print(e, len(pkt))


if __name__ == '__main__':
    packets = PcapReader('/home/steven/Documents/UdeA/maestria/Tesis/Implementación/my_project/my_environment/code/implementation/Wednesday-WorkingHours.pcap')
    while True:
        pkt = packets.read_packet()
        if pkt is None:
            break
        else:
            modifier(pkt)
# sudo ifconfig enp7s0 mtu 4080 up
