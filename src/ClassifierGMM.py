import sys

import numpy as np
from sklearn import metrics, mixture
from sklearn.preprocessing import StandardScaler

sys.path.append('/home/steven/Documents/UdeA/maestria/Tesis/Implementación/my_project/my_environment/code/')
import time
from collections import Counter
from itertools import repeat

import gmm_adapt as MAP
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from tools import (choosebestclassmatch, clean_Data, clean_Data2,
                   estandar_data, pred)


class ClassifierGMM():

    def __init__(self, gmm_attack, gmm_benign, standarscaler, pcatransformation):
        self.attack_model = gmm_attack
        self.benign_model = gmm_benign
        self.scaler = standarscaler
        self.pca = pcatransformation


    def preprocess(self, file):
        # Reading CSV file
        data = pd.read_csv(file)

        # subset of data with not relevant columns
        metadata = data[['src_ip','dst_ip','src_port','dst_port','protocol','timestamp']]

        # Deleting column D_puerto
        data = data.drop(columns=['src_ip','dst_ip','src_port','dst_port','protocol','timestamp'])
                                    
        # Clean data
        data_clean = clean_Data2(data)
        return data_clean, metadata

    def predict(self,data):
        predicted_labels = pred(data, self.attack_model, self.benign_model)
        return predicted_labels
        
    # def train(self):

    def standardize(self,data):
        std_data = self.scaler.transform(data)
        return std_data

        
    def pcatransformation(self, data):
        pca_data =  pd.DataFrame(pca.transform(data))
        return pca_data
