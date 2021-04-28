import time

import numpy as np
import pandas as pd
from scipy import stats
from shared import parentdir
from sklearn import metrics, mixture
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import src.gmm_adapt as MAP
from src.utils import (choosebestclassmatch, clean_Data2, pred, read_pickle,
                       save_pickle)


class ClassifierGMM():

    def __init__(
            self, gmm_attack='', gmm_benign='', standarscaler='',
            pcatransformation='', data='', action='classification'
            ):

        self.attack_model = read_pickle(gmm_attack)
        self.benign_model = read_pickle(gmm_benign)
        self.scaler = read_pickle(standarscaler)
        self.pca = read_pickle(pcatransformation)
        self.data = data
        self.action = action
        self.performance = {}

    def preprocess(self, file=''):
        if self.action == 'classification':
            # Reading CSV file
            data = pd.read_csv(file)
            # subset of data with not relevant columns
            metadata = data[[
                'src_ip', 'dst_ip', 'src_port', 'dst_port',
                'protocol', 'timestamp'
                ]]
            # Deleting column D_puerto
            data = data.drop(columns=[
                'src_ip', 'dst_ip', 'src_port', 'dst_port',
                'protocol', 'timestamp'
                ])
            if 'flow_duration' in data.columns:
                # Odering columns
                data = data[[
                    'flow_duration', 'tot_fwd_pkts', 'tot_bwd_pkts',
                    'totlen_fwd_pkts', 'totlen_bwd_pkts', 'fwd_pkt_len_max',
                    'fwd_pkt_len_min', 'fwd_pkt_len_mean', 'fwd_pkt_len_std',
                    'bwd_pkt_len_max', 'bwd_pkt_len_min', 'bwd_pkt_len_mean',
                    'bwd_pkt_len_std', 'flow_byts_s', 'flow_pkts_s',
                    'flow_iat_mean', 'flow_iat_std', 'flow_iat_max',
                    'flow_iat_min', 'fwd_iat_tot', 'fwd_iat_mean',
                    'fwd_iat_std', 'fwd_iat_max', 'fwd_iat_min', 'bwd_iat_tot',
                    'bwd_iat_mean', 'bwd_iat_std', 'bwd_iat_max',
                    'bwd_iat_min', 'fwd_psh_flags', 'bwd_psh_flags',
                    'fwd_urg_flags', 'bwd_urg_flags', 'fwd_header_len',
                    'bwd_header_len', 'fwd_pkts_s', 'bwd_pkts_s',
                    'pkt_len_min', 'pkt_len_max', 'pkt_len_mean',
                    'pkt_len_std', 'pkt_len_var', 'fin_flag_cnt',
                    'syn_flag_cnt', 'rst_flag_cnt', 'psh_flag_cnt',
                    'ack_flag_cnt', 'urg_flag_cnt', 'cwe_flag_count',
                    'ece_flag_cnt', 'down_up_ratio', 'pkt_size_avg',
                    'fwd_seg_size_avg', 'bwd_seg_size_avg', 'fwd_byts_b_avg',
                    'fwd_pkts_b_avg', 'fwd_blk_rate_avg', 'bwd_byts_b_avg',
                    'bwd_pkts_b_avg', 'bwd_blk_rate_avg', 'subflow_fwd_pkts',
                    'subflow_fwd_byts', 'subflow_bwd_pkts', 'subflow_bwd_byts',
                    'init_fwd_win_byts', 'init_bwd_win_byts',
                    'fwd_act_data_pkts', 'fwd_seg_size_min', 'active_mean',
                    'active_std', 'active_max', 'active_min', 'idle_mean',
                    'idle_std', 'idle_max', 'idle_min'
                    ]]
                # Rename column names

                new_cols = [
                    'Flow Duration', 'Total Fwd Packets',
                    'Total Backward Packets', 'Total Length of Fwd Packets',
                    'Total Length of Bwd Packets', 'Fwd Packet Length Max',
                    'Fwd Packet Length Min', 'Fwd Packet Length Mean',
                    'Fwd Packet Length Std', 'Bwd Packet Length Max',
                    'Bwd Packet Length Min', 'Bwd Packet Length Mean',
                    'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s',
                    'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max',
                    'Flow IAT Min', 'Fwd IAT Total', 'Fwd IAT Mean',
                    'Fwd IAT Std', 'Fwd IAT Max', 'Fwd IAT Min',
                    'Bwd IAT Total', 'Bwd IAT Mean', 'Bwd IAT Std',
                    'Bwd IAT Max', 'Bwd IAT Min', 'Fwd PSH Flags',
                    'Bwd PSH Flags', 'Fwd URG Flags', 'Bwd URG Flags',
                    'Fwd Header Length', 'Bwd Header Length', 'Fwd Packets/s',
                    'Bwd Packets/s', 'Min Packet Length', 'Max Packet Length',
                    'Packet Length Mean', 'Packet Length Std',
                    'Packet Length Variance', 'FIN Flag Count',
                    'SYN Flag Count', 'RST Flag Count', 'PSH Flag Count',
                    'ACK Flag Count', 'URG Flag Count', 'CWE Flag Count',
                    'ECE Flag Count', 'Down/Up Ratio', 'Average Packet Size',
                    'Avg Fwd Segment Size', 'Avg Bwd Segment Size',
                    'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk',
                    'Fwd Avg Bulk Rate', 'Bwd Avg Bytes/Bulk',
                    'Bwd Avg Packets/Bulk', 'Bwd Avg Bulk Rate',
                    'Subflow Fwd Packets', 'Subflow Fwd Bytes',
                    'Subflow Bwd Packets', 'Subflow Bwd Bytes',
                    'Init_Win_bytes_forward', 'Init_Win_bytes_backward',
                    'act_data_pkt_fwd', 'min_seg_size_forward', 'Active Mean',
                    'Active Std', 'Active Max', 'Active Min', 'Idle Mean',
                    'Idle Std', 'Idle Max', 'Idle Min'
                     ]
                data.set_axis(new_cols, axis=1, inplace=True)
            elif 'Flow Duration' in data.columns:
                data = data.drop(columns=['Destination Port', 'Label'])
            # Clean data
            data_clean = clean_Data2(data)
            return data_clean, metadata
        else:
            data = pd.read_csv(self.data)
            # Deleting column D_puerto
            data_ = data.drop(columns=[
                'Destination Port', 'Source Port', 'Source IP',
                'Destination IP',
                'Protocol', 'Timestamp', 'Flow ID'
                ])

            # Clean data
            data_clean = clean_Data2(data_)
            return data_clean

    def standardize(self, data='', X_train_gmm='', X_test_gmm=''):
        if self.action == 'classification':
            std_data = self.scaler.transform(data)
            return std_data
        else:
            scaler = StandardScaler()
            scaler.fit(X_train_gmm)
            save_pickle(scaler, f'{parentdir}/ml/standardize/scaler.pickle')
            X_train_gmm_s = pd.DataFrame(scaler.transform(X_train_gmm))
            X_test_gmm_s = pd.DataFrame(scaler.transform(X_test_gmm))
            return X_train_gmm_s, X_test_gmm_s

    def pcatransformation(self, data='', X_train_gmm_s='', X_test_gmm_s=''):
        if self.action == 'classification':
            pca_data = pd.DataFrame(self.pca.transform(data))
            return pca_data
        else:
            # Correlation matrix
            corr = X_train_gmm_s.corr()

            # covariance matrix
            mat_cov = X_train_gmm_s.cov()

            # eigen values y eigen vectors
            eig_vals, eig_vecs = np.linalg.eig(mat_cov)

            #  pairs of (autovector, autovalue)
            eig_pairs = [(np.abs(eig_vals[i]), eig_vecs[:, i]) for i in range(
                len(eig_vals))]

            # pairs in in descending order
            eig_pairs.sort(key=lambda x: x[0], reverse=True)

            # variance maximization
            tot = sum(eig_vals)
            var_exp = [(i / tot)*100 for i in sorted(eig_vals, reverse=True)]
            cum_var_exp = np.cumsum(var_exp)

            pca = PCA(n_components=18)
            X_train_s_arr = np.array(X_train_gmm_s)

            principalComponents = pca.fit_transform(X_train_s_arr)
            self.performance['Explained_Variance_PCA'] = np.sum(
                pca.explained_variance_ratio)

            X_train_s_pca = pd.DataFrame(
                data=principalComponents, columns=[
                    'pca1', 'pca2', 'pca3', 'pca4', 'pca5', 'pca6', 'pca7',
                    'pca8', 'pca9', 'pca10', 'pca11', 'pca12', 'pca13',
                    'pca14', 'pca15', 'pca16', 'pca17', 'pca18'
                ]
                )

            X_test_s_pca = pd.DataFrame(
                data=pca.transform(X_test_gmm_s), columns=[
                    'pca1', 'pca2', 'pca3', 'pca4', 'pca5', 'pca6', 'pca7',
                    'pca8', 'pca9', 'pca10', 'pca11', 'pca12', 'pca13',
                    'pca14', 'pca15', 'pca16', 'pca17', 'pca18'
                ]
                )

            save_pickle(pca, f'{parentdir}ml/pca/pca.pickle')
            return X_train_s_pca, X_test_s_pca

    def split_test_train(self, data_clean):
        benign = data_clean['Label'] == 'BENIGN'

        attack = data_clean['Label'].str.contains('DoS')

        data_attack = data_clean[attack]
        data_benign = data_clean[benign]

        data_attack['Label'] = np.zeros(len(data_attack['Label']))
        data_benign['Label'] = np.ones(len(data_benign['Label']))

        nb_samples = [len(data_attack), len(data_benign)]

        if np.argmin(nb_samples) == 0:
            data_benign2 = data_benign[:nb_samples[0]]
            data_attack2 = data_attack
        else:
            data_attack2 = data_attack[:nb_samples[1]]
            data_benign2 = data_benign

        balanced_data = pd.concat([data_attack2, data_benign2])

        # Spliting the dataset into train and test
        # all columns except the last one
        features = balanced_data.loc[:, balanced_data.columns != 'Label']
        target = balanced_data['Label']  # only the last column

        X_train_gmm, X_test_gmm, y_train_gmm, y_test_gmm = train_test_split(
            features, target, test_size=0.3, random_state=109
            )  # 70% training and 30% test
        y_train_gmm = y_train_gmm.astype('int')
        y_test_gmm = y_test_gmm.astype('int')

        return X_train_gmm, X_test_gmm, y_train_gmm, y_test_gmm

    def predict(
            self, data='', attack_gmm_data_model='',
            benign_gmm_data_model='', y_test_gmm=''):
        if self.action == 'classification':
            predicted_labels = pred(data, self.attack_model, self.benign_model)
            return predicted_labels
        else:
            # Geerationg the GMM by each class and performing
            # the proof for Test data

            # for attack test, predict 0 = DDoS, 1 = Benign
            results_by_gaussian = {}
            accuracy_attack = [0]
            gaussians = np.arange(1, 20, 1)
            time_per_gaussian = []
            time_for_predict = []
            for i in gaussians:
                print('Training GMM for %i Gaussians' % i)
                time_init = time.time()
                ngauss = i
                GMM_Attack = mixture.GaussianMixture(
                    n_components=ngauss, covariance_type='diag', max_iter=200,
                    n_init=100, random_state=100)
                GMM_Attack.fit(attack_gmm_data_model)
                GMM_Benign = mixture.GaussianMixture(
                    n_components=ngauss, covariance_type='diag', max_iter=200,
                    n_init=100, random_state=100)
                GMM_Benign.fit(benign_gmm_data_model)
                save_pickle(
                    GMM_Attack, f'{parentdir}/ml/mlmodels/Attack_G{i}.pickle')
                save_pickle(
                    GMM_Benign, f'{parentdir}/ml/mlmodels/Benign_G{i}.pickle')
                time_per_gaussian.append(time.time()-time_init)

                time_init = time.time()
                predict_labels1 = pred(X_test_s_pca, GMM_Attack, GMM_Benign)
                time_for_predict.append(time.time()-time_init)

                acc = metrics.accuracy_score(y_test_gmm, predict_labels1)
                results_by_gaussian['g%is%i' % (i, 1)] = [
                    [y_test_gmm, predict_labels1], acc]
                accuracy_attack.append(acc)
            self.performance['training_time_by_G'] = time_per_gaussian
            self.performance['classification_time_by_G'] = time_for_predict
            self.performance['accuracies_by_G'] = accuracy_attack
            return predict_labels1

    def train(self):
        # preprocessing
        data_clean = self.preprocess()

        # split clases
        X_train_gmm, X_test_gmm, y_train_gmm, y_test_gmm = self.split_test_train(data_clean)

        # standardize the data test and train
        X_train_gmm_s, X_test_gmm_s = standardize(
            X_test_gmm=X_test_gmm, X_train_gmm=X_train_gmm)

        # PCA transformation
        X_train_s_pca, X_test_s_pca = pcatransformation(
            X_train_gmm_s=X_train_gmm_s, X_test_gmm_s=X_test_gmm_s)

        attack_gmm_data_model = X_train_s_pca[
            np.array(y_train_ubm == 0, dtype=bool)]
        benign_gmm_data_model = X_train_s_pca[
            np.array(y_train_ubm == 1, dtype=bool)]

        results_by_gaussian = self.predict(
            attack_gmm_data_model=attack_gmm_data_model,
            benign_gmm_data_model=benign_gmm_data_model, y_test_gmm=y_test_gmm)
        self.evaluate_performance(results_by_gaussian)

    def evaluate_performance(self, results_by_gaussian):
        # Report of Precision, Sensitivity and Confusion Matrix
        print(
            f'Explained Variance PCA='
            '{self.performance["Explained_Variance_PCA"]}')
        labels = ['attack', 'benign']
        i = 0
        for k, v in results_by_gaussian.items():
            print(f'### PERFORMANCE FOR GAUSSIAN # {i + 1} ###')
            print('\nresult by attack_test %s\n' % k)
            print(metrics.classification_report(
                list(v[0][0]), v[0][1], target_names=labels))
            print('\nConfusion Matrix\n', metrics.confusion_matrix(
                list(v[0][0]), v[0][1]))
            print(f'Trainig time={self.performance["training_time_by_G"][i]}')
            print(
                f'Classification time='
                '{self.performance["classification_time_by_G"][i]}')
            i += 1
            print('\n --------------------------------------------------- \n')
