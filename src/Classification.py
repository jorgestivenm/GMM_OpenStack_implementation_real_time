import configparser
import glob
import os
import sys
import time

import requests
from shared import (controller, controller_port, dpid_sw, hard_timeout,
                    idle_timeout, localstore, logger, parentdir, sw_table)

from src.ClassifierGMM import ClassifierGMM

config = configparser.ConfigParser()

featuresdir = parentdir + '/features'
gmm_attack = parentdir + '/ml/mlmodels/Attack_G9.pickle'
gmm_benign = parentdir + '/ml/mlmodels/Benign_G9.pickle'
pca = parentdir + '/ml/pca/pca.pickle'
scaler = parentdir + '/ml/standardize/scaler.pickle'
get_flows_stats = f'/stats/flow/{dpid_sw}'
add_flow_entry = f'/stats/flowentry/add'


def classificator():
    GmmClassifier = ClassifierGMM(
        gmm_attack=gmm_attack, gmm_benign=gmm_benign,
        standarscaler=scaler, pcatransformation=pca)
    while True:
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
                    time.sleep(1)
                    logger.info(f'analyzing the file:{input_file}')
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
                            logger.ifo(f"Drop flow with SRC={src_ip} and DST={dst_ip}")
                            match = '"ipv4_dst": "{}", "eth_type": 2048, "ipv4_src": "{}", "eth_type": 2048'.format( dst_ip, src_ip)
                            match = ('{%s}' %match)
                            pload = '"dpid": {}, "cookie": 1, "cookie_mask":1, "table_id": {}, "idle_timeout": {}, "hard_timeout": {}, "priority": 10, "match": {}, "actions": []'.format(dpid_sw, sw_table, idle_timeout, hard_timeout, match)
                            pload = ('{%s}' %(pload))
                            r = requests.post(url, data=pload)
                        r = requests.get(
                            f'http://{controller}:{controller_port}{get_flows_stats}'
                            )
                    os.remove(filepath)
            except Exception as e:
                logger.error(e)
                number_lines = sum(1 for row in (open(input_file)))
                if number_lines == 0:
                    os.remove(filepath)
