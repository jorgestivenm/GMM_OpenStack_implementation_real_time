import logging
import os

from dotenv import load_dotenv

load_dotenv()

parentdir = os.path.dirname(os.path.abspath('__file__'))
iface = os.getenv('IFACE')
localstore = parentdir + "/localstore.txt"

controller = os.getenv('CTRL')
controller_port = os.getenv('CTRL_PORT')
sw_table = int(os.getenv('TABLE'))
dpid_sw = int(os.getenv('SW'))
targets = os.getenv('TARGETS')
hard_timeout = int(os.getenv('HARD_T'))
idle_timeout = int(os.getenv('IDLE_T'))
threshold_pkts_attack = int(os.getenv('MIN_TROUGH_DETECTION_ATTACK_NUMBER'))
threshold_pkts_benign = int(os.getenv('TROUGHPUT_THRESHOLD_BENIGN'))
repeated_threshold = int(os.getenv('REPEATED_THRESHOLD'))
# Logger config
logs_directory = os.path.dirname(
    os.path.realpath(__file__)) + os.getenv('LOG_FILES_DIRECTORY')
logging.basicConfig(
    filename=logs_directory+'/gmm_detection.log', level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("gmm_detection")
