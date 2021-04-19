"""
Created on Wed Aug 26 18:59:48 2020

@author: steven
"""
import numpy as np
import pandas as pd
from six.moves import cPickle as pickle


# Delete rows with values equal to Nan and columns equal to zero
def clean_Data(data0):
    for sc in data0.axes[1]:
        if (sc != 'Label'):
            # data0 = data0.drop(data0.loc[data0[sc] == 'Infinity'].index)
            # data0 = data0.dropna(axis=1, how="all")
            data0 = data0[~data0.isin([np.nan, np.inf, -np.inf]).any(1)]
            # indexnan = data0[sc].index[data0[sc].apply(np.isnan)]
            # indexinf = data0[sc].index[data0[sc].apply(np.isinf)]
            # data0 = data0.drop(indexnan, inplace=False)
            # data0 = data0.drop(indexinf, inplace=False)
            # print(f'nan for {sc}: {indexnan}')
            # print(f'inf for {sc}: {indexinf}')
            # print('-----------------------')
            # data0 = pd.DataFrame(data0)
            if data0[sc].dtypes == 'object':
                data0[sc] = data0[sc].astype(float)
            if ((data0[sc] == 0).all()):
                data0 = data0.drop(columns=sc)
    return data0


def clean_Data2(data0):
    for sc in data0.axes[1]:
        if (sc != "Label"):
            data0 = data0[~data0.isin([np.nan, np.inf, -np.inf]).any(1)]
            if data0[sc].dtypes == 'object':
                try:
                    data0[sc] = data0[sc].astype(float)
                except Exception as e:
                    data0[sc] = pd.to_numeric(data0[sc], errors='coerce')
                    print(f'Error: {e}')
    # data0 = data0.loc[:, (data0 != 0).any(axis=0)]

    return data0


# standardize data
def estandar_data(data00):
    data_num_std = pd.DataFrame({})
    for i, sc in enumerate(data00.axes[1]):
        if sc != 'Label':
            mean = np.mean(data00[str(sc)])
            std = np.std(data00[str(sc)])
            data_num_std[str(sc)] = ((data00[str(sc)] - mean) / std)
        else:
            data_num_std[str(sc)] = data00[str(sc)]
    return data_num_std


# Classifier
def choosebestclassmatch(obj, modelA, modelB):
    prob_a = modelA.score(obj)
    prob_b = modelB.score(obj)
    # print('\n Score: ', prob_a, prob_b)
    a = [prob_a, prob_b]
    classi = np.argmax(a)
    return classi


# pred function
def pred(dataf, gmmA, gmmB):
    predict = []
    for i in range(len(dataf)):
        # print('\nsanple # %f' %i)
        set_t = dataf.iloc[i, :].values.reshape(1, -1)
        pred = choosebestclassmatch(set_t, gmmA, gmmB)
        predict.append(pred)
    return predict


def save_pickle(data, file_save):
    """
    Guarda el modelo entrenado para que sea utilizado
    posteriormente en la predicción de nuevos datos.

    :param data: modelo que será guardado.
    :type data: Datos a guardar
    :param file_save: Path donde será almacenado el modelo .pickle
    :type file_save: str
    """
    try:
        f = open(file_save, 'wb')
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        f.close()
    except Exception as e:
        print(f'Unable to save data to {file_save} -> {e}')


def read_pickle(file):
    with open(file, 'rb') as f:
        object_file = pickle.load(f)
    return object_file
