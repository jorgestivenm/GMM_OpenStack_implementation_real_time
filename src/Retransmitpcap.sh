#!/bin/bash
PCAP_FILES="/home/steven/Documents/UdeA/maestria/Tesis/Implementación/my_project/my_environment/code/implementation/pcap/WWPC_A_*.pcap"

IFACE="virbr1"

echo "Changing the MTU for $IFACE to 15000"
sudo ifconfig virbr1 mtu 15000 up
echo "Initializing the pcap retransmition - $(date '+%Y-%m-%d %H:%M:%S')"
for filename in $PCAP_FILES; do

  echo "Sending pkts from $filename"
  sudo tcpreplay -d 1 --intf1=$IFACE $filename

done
echo "Finishing the pcap retransmition - $(date '+%Y-%m-%d %H:%M:%S')"
