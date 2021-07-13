import configparser
import glob
import os
import sys
import time

import numpy as np
import requests
from shared import (avoided_ips, controller, controller_port, dpid_sw,
                    hard_timeout, idle_timeout, localstore, logger, nova_url,
                    parentdir, repeated_threshold, sw_table,
                    threshold_pkts_attack, threshold_pkts_benign)

from src.ClassifierGMM import ClassifierGMM

config = configparser.ConfigParser()

featuresdir = parentdir + '/features'
gmm_attack = parentdir + '/ml/mlmodels/Attack_G9.pickle'
gmm_benign = parentdir + '/ml/mlmodels/Benign_G9.pickle'
pca = parentdir + '/ml/pca/pca.pickle'
scaler = parentdir + '/ml/standardize/scaler.pickle'
get_flows_stats = f'/stats/flow/{dpid_sw}'
add_flow_entry = f'/stats/flowentry/add'

lb_working = False
token = False
logger.info(f'{parentdir},{featuresdir}')

def classificator():
    global token
    global lb_working
    GmmClassifier = ClassifierGMM(
        gmm_attack=gmm_attack, gmm_benign=gmm_benign,
        standarscaler=scaler, pcatransformation=pca)
        
    high_throughput = 0
    while True:
        # getting token
        if (not token):
            body_token = """{   
                "auth": {
                    "identity": {
                            "methods": ["password"],
                            "password": {
                                "user": {
                                    "name": "admin",
                                    "domain": { "id": "default" },
                                    "password": "admin"
                                }
                            }
                        },
                    "scope": {
                            "project": {
                                "name": "admin",
                                "domain": { "id": "default" }
                            }
                        }
                    }
                }"""
            r = requests.post(
                "http://192.168.100.110:5000/v3/auth/tokens",
                data=body_token
                )
            headers = r.headers
            token_ok = headers['X-Subject-Token']
            logger.info(f'token : {token_ok}')
            token = True
        config.read(localstore)
        count = int(config['SNIFFER']['Count'])
        for filepath in glob.glob(os.path.join(featuresdir, '*.csv')):
            try:
                input_file = filepath
                if input_file != os.path.join(
                    featuresdir, f'flow_{count}.csv'
                    ) and input_file != os.path.join(
                        featuresdir, f'flow_{count + 1}.csv'
                        ) and input_file != os.path.join(
                            featuresdir, f'flow_0.csv'
                            ):
                    logger.info(f'#### analyzing the file:{input_file} ###\n')
                    data_clean, metadata = GmmClassifier.preprocess(
                        file=input_file)
                    std_data = GmmClassifier.standardize(data=data_clean)
                    pca_data = GmmClassifier.pcatransformation(data=std_data)
                    predicted_labels = GmmClassifier.predict(data=pca_data)
                    detection = [i for i in range(
                        len(predicted_labels)) if predicted_labels[i] == 0]
                    if len(detection) > 0:
                        data_for_rules = metadata.iloc[detection]
                        data_for_rules = data_for_rules.drop_duplicates(
                            subset=['src_ip', 'dst_ip'], keep=False,
                            inplace=False)
                        logger.info('creating rules to apply in the sw')
                        url = f'http://{controller}:{controller_port}{add_flow_entry}'
                        for index, row in data_for_rules.iterrows():
                            src_ip = str(row['src_ip'])
                            dst_ip = str(row['dst_ip'])
                            src_port = row['src_port']
                            dst_port = row['dst_port']
                            proto = row['protocol']
                            if (src_ip in avoided_ips or dst_ip in avoided_ips):
                                pass
                            else:
                                logger.info(f"## Drop flow with SRC={src_ip} and DST={dst_ip} ##")
                                match = '"ipv4_dst": "{}", "eth_type": 2048, "ipv4_src": "{}", "eth_type": 2048'.format( dst_ip, src_ip)
                                match = ('{%s}' %match)
                                pload = '"dpid": {}, "cookie": 1, "cookie_mask":1, "table_id": {}, "idle_timeout": {}, "hard_timeout": {}, "priority": 10, "match": {}, "actions": []'.format(dpid_sw, sw_table, idle_timeout, hard_timeout, match)
                                pload = ('{%s}' %(pload))
                                r = requests.post(url, data=pload)
                        r = requests.get(
                            f'http://{controller}:{controller_port}{get_flows_stats}'
                            )
                    logger.debug(detection)
                    benignData = data_clean.loc[~data_clean.index.isin(
                        detection)]
                    if (len(benignData["Fwd Packets/s"]) == 0):
                        throughput_max = 0.0
                        throughput_min = 0.0
                        throughput_mean = 0.0
                    else:
                        logger.debug(benignData["Fwd Packets/s"])
                        throughput_max = np.max(benignData["Fwd Packets/s"])
                        throughput_min = np.min(benignData["Fwd Packets/s"])
                        throughput_mean = np.mean(benignData["Fwd Packets/s"])
                    throughput_tot = np.sum(benignData["Fwd Packets/s"])

                    attackData = data_clean.iloc[detection]
                    if (len(attackData["Fwd Packets/s"]) == 0):
                        attack_throughput_max = 0.0
                        attack_throughput_min = 0.0
                        attack_throughput_mean = 0.0
                    else:
                        logger.debug(attackData["Fwd Packets/s"])
                        attack_throughput_max = np.max(attackData["Fwd Packets/s"])
                        attack_throughput_min = np.min(attackData["Fwd Packets/s"])
                        attack_throughput_mean = np.mean(attackData["Fwd Packets/s"])
                    attack_throughput_tot = np.sum(attackData["Fwd Packets/s"])
                    logger.info("{:<15} {:<15} {:<15} {:<15}".format(
                        'att_pkt_tot', 'att_pkt_min', 'att_pkt_max',
                        'att_pkt_mean'))
                    logger.info("{:<15} {:<15} {:<15} {:<15}".format(
                        attack_throughput_tot, attack_throughput_min,
                        attack_throughput_max, attack_throughput_mean))
                    logger.info("{:<15} {:<15} {:<15} {:<15}".format(
                        'bng_pkt_tot', 'bng_pkt_min', 'bng_pkt_max',
                        'bng_pkt_mean'))
                    logger.info("{:<15} {:<15} {:<15} {:<15}".format(
                        throughput_tot, throughput_min, throughput_max,
                        throughput_mean))
                    if (attack_throughput_max <= threshold_pkts_attack):
                        if (throughput_mean > threshold_pkts_benign):
                            logger.info("####====high througput====####\n")
                            high_throughput += 1
                            if (high_throughput > repeated_threshold):
                                logger.info("========The NS needs a Loadbalancer======\n")
                                high_throughput = 0
                                if (not lb_working):
                                    body = '{"os-start" : null}'
                                    r = requests.post(
                                        nova_url, data=body, headers={'X-Auth-Token': token_ok}
                                        )
                                    logger.info("the second WEB server has been activated")
                        else:
                            logger.info("High throughput interrupted -> Initial state = 0")
                            high_throughput = 0
                    else:
                        logger.info("High attack througput")
                    os.remove(filepath)
            except Exception as e:
                logger.error(e)
                number_lines = sum(1 for row in (open(input_file)))
                if number_lines == 0:
                    os.remove(filepath)
