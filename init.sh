#!/usr/bin/env bash
trap "set +x; sleep 1; set -x" DEBUG
#========================== CONSTANT VALUES ===============================
#==========================================================================
PROJECT_DIR="$(pwd)"
PARENT_DIR="$(dirname $PROJECT_DIR)";
CURRENT_GROUP="$(id -g -n)"
SERVER_ADDRESS=127.0.0.1
NAME_DATA_BASE="pme_db"
PASSWORD_DATABASE="ADMpj@01"
USER_DATABASE="pmeadm"
USAGE="
NAME
	$(basename "$0") - UTILS 

OPTIONS:

    -h |--help  show this help text

    -i |--install=[APP INSTALLATION]

    -g |--gui=[INSTALL GRAPHICAL USER INTERFACE]

"


create_pmeMain_serviceFile()
{
PYTHON_BIN="$(which python3.8)"
echo "[Unit]
Description=PME APP
Requires=postgresql.service,rqworker@1.service
After=network.target

[Service]
WorkingDirectory=${PROJECT_DIR}
EnvironmentFile=${PROJECT_DIR}/.env
ExecStart=${PYTHON_BIN} run.py
Restart=on-failure
    RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=pmeapp
User=${USER}

[Install]
WantedBy=multi-user.target" > ./pme_app/use_cases/utils/systemd/pmeapp.service 
}

create_pmeMain_envFile()
{
echo "PYTHON_ENV=production
HTTP_PORT=8181
SECRET_KEY = "MySuperKey"
ROUNDS = 13
UPLOAD_FOLDER = "/uploads"
DATABASE=${NAME_DATA_BASE}
DATABASE_USER=${USER_DATABASE}
HOST="0.0.0.0"
DATABASE_PASSWORD=${PASSWORD_DATABASE}
LOG_FILES_DIRECTORY="/logs"
EMAIL_USER="proyectomineroenergetico@gmail.com"
EMAIL_PASSWORD="proyectomineroenergeticoUdeA2020"" > $PROJECT_DIR/.env

}
create_rq_worker_serviceFile()
{
echo "[Unit]
Description=RQ Worker Number %i
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/working_directory
Environment=LANG=en_US.UTF-8
Environment=LC_ALL=en_US.UTF-8
Environment=LC_LANG=en_US.UTF-8
ExecStart=/path/to/rq worker -c config.py
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
"> ./pme_app/use_cases/utils/systemd/rqworker@.service
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
echo "******Redis Server"
if ! hash redis-server 2>/dev/null; then
    sudo apt install redis-server
fi 
redis-server --version
echo "redis installed"

# PYTHON MODULES 
echo "******PYTHON MODULES REQUIRED"
pip3 install --user -r requirements.txt

# POSTGRES
echo "******POSTGRES"
if ! hash psql 2>/dev/null; then
    sudo apt -y install postgresql postgresql-contrib;
    
    sudo -u postgres createuser --superuser ${USER_DATABASE}
    sudo -u postgres psql -c "ALTER USER ${USER_DATABASE} WITH PASSWORD '${PASSWORD_DATABASE}';"
    sudo service postgresql restart
fi
psql --version   
echo "postgresql installed"

echo "================ Enabling sion process management =================="
if [ ! -f /etc/systemd/system/pmeapp.service ]; then
    if [ ! -d ./pme_app/use_cases/utils/systemd ]; then
        mkdir ./pme_app/use_cases/utils/systemd
    fi
    $(create_pmeMain_serviceFile)
    sudo cp ./pme_app/use_cases/utils/systemd/pmeapp.service /etc/systemd/system
    sudo systemctl daemon-reload
    sudo systemctl enable pmeapp.service
    sudo systemctl start pmeapp.service
fi

echo "================ Enabling rqworker process management =================="
if [ ! -f /etc/systemd/system/rqworker@.service ]; then
    if [ ! -d ./pme_app/use_cases/utils/systemd ]; then
        mkdir ./pme_app/use_cases/utils/systemd
    fi
    $(create_rq_worker_serviceFile)
    sudo cp ./pme_app/use_cases/utils/systemd/rqworker@.service /etc/systemd/system
    sudo systemctl daemon-reload
    sudo systemctl enable rqworker@1.service
    sudo systemctl start rqworker@1.service
fi

#Reloading environment
. ~/.bashrc

#Finishing and cleaning
sudo apt -y autoremove
mkdir ${PROJECT_DIR}/uploads
mkdir ${PROJECT_DIR}/data_files
mkdir ${PROJECT_DIR}/logs
touch ${PROJECT_DIR}/logs/pme.log
}



configure_db()
{
echo "========== SETTING UP SION CONTROLLER DATABASE ========="
sudo -u postgres dropdb --if-exists ${NAME_DATA_BASE}
sudo -u postgres createdb ${NAME_DATA_BASE}

#Create needed tables into sdiot database
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
}



#================================= MAIN THREAD===================================
#================================================================================
while [ "$1" != "" ]; do
    case $1 in
        
        -i|--install)
            install_project
            configure_db
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

# install tcpreplay

#modifying the utils.py from cicflowmeter
"""
def get_statistics(alist: list):
    """Get summary statistics of a list"""
    iat = dict()

    if len(alist) > 1:
        iat["total"] = sum(alist)
        iat["max"] = max(alist)
        iat["min"] = min(alist)
        alist2 =[]
        for i in alist:
            alist2.append(int(i))
        iat["mean"] = numpy.mean(alist2)
        iat["std"] = numpy.sqrt(numpy.var(alist2))
    else:
        iat["total"] = 0
        iat["max"] = 0
        iat["min"] = 0
        iat["mean"] = 0
        iat["std"] = 0

    return iat
"""

#modifying the flow_bytes.py from cicflowmeter.features

"""
    def get_min_forward_header_bytes(self) -> int:
        """Calculates the amount of header bytes in the header sent in the opposite direction as the flow.

        Returns:
            int: The amount of bytes.

        """
        def header_size(packets):
            hz = []
            for packet, direction in packets:
                if direction == PacketDirection.FORWARD:
                    hz.append(self._header_size(packet))
            return hz

        packets = self.feature.packets

        v  = header_size(packets)
        if not v :
            return 0
        else:
            return min(v)
"""