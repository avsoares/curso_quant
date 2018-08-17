%matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from arctic import Arctic
from datetime import datetime
import datetime
import seaborn as sb


def import_dados(lista_ativos):

    print('Importando dados')
    pd_dados_raw = pd.DataFrame([])

    for ativo in lista_ativos:
        pd_import_raw = library.read(ativo).data #import de dados
        pd_dados_raw = pd_dados_raw.join(pd_import_raw.close.to_frame().rename(columns={'close' : ativo}), how='outer')

    pd_dados_raw = pd_dados_raw.fillna(method = 'ffill')

    return pd_dados_raw.groupby(pd_dados_raw.index.date).last()

def build_covariance_matrix(data_close, portfol):

    data_return = np.log( data_close / data_close.shift(1) )
    data_return = data_return.shift(1)

    num_ativos = len(list(portfol.keys()))
    ewma = [(1 - 0.94) * (0.94 ** i) for i in range(72)][::-1]

    pd_portfolio = data_close.copy()
    for ativo in portfol.keys():
        pd_portfolio[ativo] = pd_portfolio[ativo] * portfol[ativo]
    np_portfolio = np.asmatrix(pd_portfolio.values)

    np_dados_return = data_return.values

    list_vars = []
    for i in range(0, data_return.shape[0]):
        if i < 73:
            list_vars += [0]
        else:
            covMat = np.asmatrix(np.zeros((num_ativos, num_ativos)))
            for col1 in range(num_ativos):
                for col2 in range(num_ativos):
                    ret1 = np_dados_return[i-71:i+1, col1]
                    ret2 = np_dados_return[i-71:i+1, col2]
                    covMat[col1, col2] = np.sum((ret1 * ret2) *  ewma)
            np_used = np_portfolio[i, :]
            var_dia = 1.65 * ((np_portfolio[i, :] * covMat *  np_portfolio[i, :].T)[0, 0]) ** 0.5
            list_vars += [var_dia]
    return pd.DataFrame(list_vars, index=data_close.index, columns=[['var']])


store = Arctic('localhost')

library = store['MinStore.BVSP']

portfolio = {'ABEV3' : 2000,
             'PETR4' : -5000,
             'BOVA11' : 1500,
             'ITUB4' : 5000,
             'EZTC3' : -7000}

pd_dados_raw = import_dados(list(portfolio.keys()))

pd_dados_return = np.log( pd_dados_raw / pd_dados_raw.shift(1) )

pd_var = build_covariance_matrix(pd_dados_raw, portfolio)

pd_portfolio = pd_dados_raw.copy()
for ativo in portfolio.keys():
    pd_portfolio[ativo] = pd_portfolio[ativo] * portfolio[ativo]
pd_portfolio_return = (pd_dados_raw / pd_dados_raw.shift(1) - 1) * pd_portfolio

pd_var = -pd_var
pd_var['return'] = pd_portfolio_return.sum(axis=1)

fig, (ax1, ax2) = plt.subplots(2, sharex=True)
ax1.plot(pd_dados_return)
ax2.plot(pd_var)  #plot da posicao e graficos de preco

pd_var = pd_var[(pd_var['var'] < 0).values]
pd_var['dif'] = pd_var['var'].values - pd_var['return'].values
len(pd_var.dif[pd_var.dif > 0].dropna()) / len(pd_var) * 100
