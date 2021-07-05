#!/usr/bin/env bash
trap "set +x; sleep 1; set -x" DEBUG
#========================== CONSTANT VALUES ===============================
#==========================================================================
PROJECT_DIR="$(pwd)"
PARENT_DIR="$(dirname $PROJECT_DIR)";
CURRENT_GROUP="$(id -g -n)"
DEF_IFACE=$(awk '$2 == 00000000 { print $1 }' /proc/net/route)

USAGE="
NAME
	$(basename "$0") - UTILS 

OPTIONS:

    -h |--help  show this help text

    -i |--install=[APP INSTALLATION]

"


create_Main_serviceFile()
{
PYTHON_BIN="$(which python3.8)"
echo "[Unit]
Description=DMDOS
After=network.target

[Service]
WorkingDirectory=${PROJECT_DIR}
EnvironmentFile=${PROJECT_DIR}/.env
ExecStart=${PYTHON_BIN} run.py
Restart=on-failure
    RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=DMDOS
User=${USER}

[Install]
WantedBy=multi-user.target" > ./utils/systemd/dmdos.service 
}

create_Main_envFile()
{
echo "IFACE=${DEF_IFACE}
CTRL='192.168.100.129'
CTRL_PORT=8080
TABLE=60
SW=1
TARGETS='192.168.100.232,192.168.100.249'
HARD_T=3600
IDLE_T=1800
LOG_FILES_DIRECTORY='/logs'
MIN_TROUGH_DETECTION_ATTACK_NUMBER=500
TROUGHPUT_THRESHOLD_BENIGN=10000
REPEATED_THRESHOLD=5
TENANT_ID=38abe714f498458daf6c2233d72459f6
SERVER1=8fa29bb1-6254-4d53-a0a3-ef02b731725e
SERVER2=2f55e8c8-80f2-4568-8d53-7169d110bee7
NOVA_URL=http://192.168.100.110:8774/v2.1/" > $PROJECT_DIR/.env

}

install_project()
{
echo "******PYTHON3"
if ! hash python3 2>/dev/null; then
    sudo apt install python3 python3-dev -y
    sudo apt install gcc gcc-c++ kernel-devel make -y
    sudo apt install build-essential -y
fi
python3 --version
echo "python3 installed"

echo "******PYTHON-PIP"
if ! hash pip3 2>/dev/null; then
    sudo apt install libpq-dev python3-pip -y 
fi
pip3 --version
echo "pip3 installed"

# PYTHON MODULES 
echo "******PYTHON MODULES REQUIRED"
pip3 install --user -r requirements.txt


echo "================ Enabling DMDOS process management =================="
if [ ! -f /etc/systemd/system/dmdos.service ]; then
    if [ ! -d ./utils/systemd ]; then
        mkdir ./utils/systemd
    fi
    $(create_Main_serviceFile)
    sudo cp ./utils/systemd/dmdos.service /etc/systemd/system
    sudo systemctl daemon-reload
    sudo systemctl enable dmdos.service
    sudo systemctl start dmdos.service
fi


#Reloading environment
. ~/.bashrc

#Finishing and cleaning
sudo apt -y autoremove
mkdir ${PROJECT_DIR}/captures
mkdir ${PROJECT_DIR}/features
mkdir ${PROJECT_DIR}/logs
touch ${PROJECT_DIR}/logs/gmm_detection.log
$(create_Main_envFile)
}



#================================= MAIN THREAD===================================
#================================================================================
while [ "$1" != "" ]; do
    case $1 in
        
        -i|--install)
            install_project
            exit
            ;;
        -h | --help) 
            echo "$USAGE"
            exit
            ;;
                        
        *)  echo "$USAGE"
            exit 1
            ;;
    esac
    shift
done

# # install tcpreplay

# #modifying the utils.py from cicflowmeter
# """
# def get_statistics(alist: list):
#     """Get summary statistics of a list"""
#     iat = dict()

#     if len(alist) > 1:
#         iat["total"] = sum(alist)
#         iat["max"] = max(alist)
#         iat["min"] = min(alist)
#         alist2 =[]
#         for i in alist:
#             alist2.append(int(i))
#         iat["mean"] = numpy.mean(alist2)
#         iat["std"] = numpy.sqrt(numpy.var(alist2))
#     else:
#         iat["total"] = 0
#         iat["max"] = 0
#         iat["min"] = 0
#         iat["mean"] = 0
#         iat["std"] = 0

#     return iat
# """

# #modifying the flow_bytes.py from cicflowmeter.features

# """
#     def get_min_forward_header_bytes(self) -> int:
#         """Calculates the amount of header bytes in the header sent in the opposite direction as the flow.

#         Returns:
#             int: The amount of bytes.

#         """
#         def header_size(packets):
#             hz = []
#             for packet, direction in packets:
#                 if direction == PacketDirection.FORWARD:
#                     hz.append(self._header_size(packet))
#             return hz

#         packets = self.feature.packets

#         v  = header_size(packets)
#         if not v :
#             return 0
#         else:
#             return min(v)
# """

# sudo ovs-vsctl -- set Bridge br-int mirrors=@m2  -- --id=@qvo5c67a4bc-c9 get Port qvo5c67a4bc-c9  -- --id=@qvoa570fe19-8b get Port qvoa570fe19-8b  -- --id=@m2 create Mirror name=mirrortolb select-dst-port=@qvo5c67a4bc-c9 select-src-port=@qvo5c67a4bc-c9 output-port=@qvoa570fe19-8b

# curl -i   -H "Content-Type: application/json"   -d '
# {   "auth": {
#        "identity": {
#             "methods": ["password"],
#             "password": {
#                 "user": {
#                     "name": "admin",
#                     "domain": { "id": "default" },
#                     "password": "admin"
#                 }
#             }
#         },
#        "scope": {
#             "project": {
#                 "name": "admin",
#                 "domain": { "id": "default" }
#             }
#         }
#     }
# }'   "http://localhost:5000/v3/auth/tokens" ; echo

# OS_TOKEN=

# tenant_id=38abe714f498458daf6c2233d72459f6
# web1=8fa29bb1-6254-4d53-a0a3-ef02b731725e
# web2=2f55e8c8-80f2-4568-8d53-7169d110bee7
# start server server POST

# http://192.168.100.110:8774/v2.1/%(tenant_id)s/servers/{server_id}/action
# {
#     "os-start" : null | 
# }

# stop server 

# http://192.168.100.110:8774/v2.1/%(tenant_id)s/servers/{server_id}/action
# {
#     "os-stop" : null
# }

# curl -i -H "Content-Type: application/json" -H "X-Auth-Token: $OS_TOKEN" -d '
# {
#     "os-start" : null
# } ' "http://192.168.100.110:8774/v2.1/38abe714f498458daf6c2233d72459f6/servers/8fa29bb1-6254-4d53-a0a3-ef02b731725e/action"