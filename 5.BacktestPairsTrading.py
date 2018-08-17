%matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels
from statsmodels.tsa.stattools import coint
from arctic import Arctic
from datetime import datetime
import datetime
import seaborn as sb


def sum_volume_symbol():
    if rewrite == 1 or not 'sum_volume' in library_backtest.list_symbols():
        lista_ativos = library.list_symbols()
        lista_dados_volume = pd.DataFrame([])
        for ativo in lista_ativos:
            print(ativo)
            if not ativo[-1] in ['L', 'B'] and ativo != 'IBOV11':
                dados_volume = library.read(ativo).data.volume.to_frame().rename(columns={'volume': ativo})
                dados_volume = dados_volume[dados_volume.index.date < date_sum_volume]
                lista_dados_volume = lista_dados_volume.join(dados_volume, how='outer')
        sum_volume = lista_dados_volume.sum()
        library_backtest.write('sum_volume', sum_volume)

def import_dados():
    sum_volume = library_backtest.read('sum_volume').data
    lista_ativos = list(sum_volume.sort_values(ascending=False).iloc[:num_ativos].index)

    #IMPORT DE DADOS
    print('Importando dados')
    pd_dados_raw = pd.DataFrame([])
    pd_dados_raw_volume = pd.DataFrame([])
    for ativo in lista_ativos:
        pd_import_raw = library.read(ativo).data #import de dados
        pd_dados_raw = pd_dados_raw.join(pd_import_raw.close.to_frame().rename(columns={'close' : ativo}), how='outer')
        pd_dados_raw_volume = pd_dados_raw_volume.join(pd_import_raw.volume.to_frame().rename(columns={'volume' : ativo}), how='outer')
    pd_dados_raw = pd_dados_raw.fillna(method = 'ffill')
    pd_dados_raw_volume = pd_dados_raw_volume.fillna(value=0)
    return pd_dados_raw, pd_dados_raw_volume

def find_pairs(f_data, threshold):
    n = f_data.shape[1]
    score_matrix = np.zeros((n, n))
    pvalue_matrix = np.ones((n, n))
    keys = f_data.keys()
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            S1 = f_data[keys[i]]
            S2 = f_data[keys[j]]
            result = coint(S1, S2)
            score = result[0]
            pvalue = result[1]
            score_matrix[i, j] = score
            pvalue_matrix[i, j] = pvalue
            if pvalue < threshold:
                print(keys[i], keys[j], pvalue)
                pairs.append((keys[i], keys[j]))
    return score_matrix, pvalue_matrix, pairs


store = Arctic('localhost')

library = store['MinStore.BVSP']
library_backtest = store['Backtest.Simples']

rewrite = 0

date_sum_volume = datetime.date(2018, 1, 1)
num_ativos = 30

sum_volume_symbol()
pd_dados_raw, pd_dados_raw_volume = import_dados()


pd_dados_coint = pd_dados_raw[pd_dados_raw.index.date < date_sum_volume]
pd_dados_coint = pd_dados_coint.groupby(pd_dados_coint.index.date).last()
pd_dados_coint = pd_dados_coint.fillna(method='ffill')

scores, pvalues, pairs = find_pairs(pd_dados_coint, 0.02)


sb.heatmap(pd.DataFrame(pvalues, index=pd_dados_coint.columns, columns=pd_dados_coint.columns), annot=True)


pd_dados_pairs = pd_dados_raw
pd_dados_pair_train = pd.DataFrame([])
pd_dados_pair_train_volume = pd.DataFrame([])
for i in range(len(pairs)):
    ativo0 = pairs[i][0]
    ativo1 = pairs[i][1]
    pd_dados_pair_train[ativo0 + '_' + ativo1] = pd_dados_pairs[ativo0] / pd_dados_pairs[ativo1]
    pd_dados_pair_train_volume[ativo0 + '_' + ativo1] = pd_dados_raw_volume[ativo0] * pd_dados_raw_volume[ativo1]

len_mean = 10
len_std = 10
n_std = 1
exposicao = 1000
custo = 0.10 / 100


pd_dados_pair_train_mean = pd_dados_pair_train.rolling(60 * 8 * len_mean).mean().shift(1)
pd_dados_pair_train_std = pd_dados_pair_train.rolling(60 * 8 * len_std).std().shift(1)
pd_dados_pair_train_position = pd_dados_pair_train_volume * 0
pd_dados_pair_train_position[pd_dados_pair_train > pd_dados_pair_train_mean + n_std * pd_dados_pair_train_std] = -1
pd_dados_pair_train_position[pd_dados_pair_train < pd_dados_pair_train_mean - n_std * pd_dados_pair_train_std] = 1
pd_dados_pair_train_position[pd_dados_pair_train_volume==0] = 0
pd_dados_pair_train_position[pd_dados_pair_train_position == 0] = np.nan
pd_dados_pair_train_position = pd_dados_pair_train_position.fillna(method='ffill')
pd_dados_pair_train_position[pd_dados_pair_train_position.index.date < date_sum_volume] = 0

pd_dados_pair_train_positionQty = pd_dados_pair_train_position * exposicao /  pd_dados_pair_train   #calculo da quantidade de acoes negociadas
pd_dados_pair_train_positionQty = pd_dados_pair_train_positionQty.fillna(method='ffill')
pd_dados_pair_train_positionQty = pd_dados_pair_train_positionQty.fillna(value=0)
pd_dados_pair_train_notionalReais = - (pd_dados_pair_train_positionQty - pd_dados_pair_train_positionQty.shift(1)) * pd_dados_pair_train
pd_dados_pair_train_custo = - abs((pd_dados_pair_train_positionQty - pd_dados_pair_train_positionQty.shift(1)) * pd_dados_pair_train) * custo
pd_dados_pair_train_notionalReais = pd_dados_pair_train_notionalReais.cumsum()
pd_dados_pair_train_notionalPairs = pd_dados_pair_train_positionQty * pd_dados_pair_train   #calculo do notional em acoes
pd_dados_pair_train_notionalTotal = pd_dados_pair_train_notionalReais + pd_dados_pair_train_notionalPairs #calculo do notional total
pd_dados_pair_train_notionalTotal['total'] = pd_dados_pair_train_notionalTotal.sum(axis=1)
pd_dados_pair_train_notionalTotal.plot()
