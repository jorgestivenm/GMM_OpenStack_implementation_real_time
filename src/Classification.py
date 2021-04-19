import configparser
import glob
import os
import sys

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
                            featuresdir, f'flow_0.csv'):
                    # logic
                    print(f'analyzing the file:{input_file}')
                    data_clean, metadata = GmmClassifier.preprocess(
                        file=input_file)
                    std_data = GmmClassifier.standardize(data=data_clean)
                    pca_data = GmmClassifier.pcatransformation(data=std_data)
                    predicted_labels = GmmClassifier.predict(data=pca_data)
                    detection = [i for i in range(
                        len(predicted_labels)) if predicted_labels[i] == 0]
                    if len(detection) > 0:
                        print(detection)
                        print(metadata.iloc[detection])
                        data_for_rules = metadata.iloc[detection]
                        print('\ncurrently rules \n')
                        r = requests.get(
                            f'http://{controller}:{ctrl_port}{get_flows_stats}'
                            )
                        print(r.text)
                        print('\ncreating rules to apply in the sw\n')
                        for index, row in df.iterrows():
                            src_ip = row['src_ip']
                            dst_ip = row['dst_ip']
                            src_port = row['src_port']
                            dst_port = row['dst_port']
                            proto = row['protocol']

                            pload = {
                                "dpid": {dpid_sw}, "cookie": 1,
                                "cookie_mask": 1, "table_id": {sw_table},
                                "idle_timeout": {idle_timeout},
                                "hard_timeout": {hard_timeout},
                                "priority": 10, "flags": 1,
                                "match": {
                                    "ipv4_src": src_ip,
                                    "ipv4_dst": dst_ip, "ip_proto": proto
                                    },
                                "actions": []
                                }
                            r = requests.post(
                                f'http://{controller}:{ctrl_port}'
                                f'{add_flow_entry}', data=pload)
                            print(r.text, r.status_code)
                        print('\ncurrently rules\n')
                        r = requests.get(
                            f'http://{controller}:{ctrl_port}{get_flows_stats}'
                            )
                        print(r.text)
                    os.remove(filepath)
            except Exception as e:
                print(e)
