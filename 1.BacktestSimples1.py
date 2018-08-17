%matplotlib
import pandas as pd
from datetime import datetime
import numpy as np
from arctic import Arctic
import numpy as np
import matplotlib.pyplot as plt


store = Arctic('localhost')
store.list_libraries()

library = store['MinStore.BVSP']

#Testando um simples estratégia de médias móveis para o ativo ABEV3

ma_len = 120
num_std = 1.5
exposicao = 1000
custo = 0.05 / 100

ativo = 'ABEV3'
pd_dados_raw = library.read(ativo).data #import de dados
pd_dados = pd_dados_raw.close.to_frame()
pd_dados['MA'] = pd_dados.close.rolling(ma_len).mean().shift(1)   #calculo da ma
pd_dados['MA_Plus'] = pd_dados['MA'] + num_std * pd_dados.close.rolling(ma_len).std().shift(1)  #calculo da ma mais desvio padrao
pd_dados['MA_Minus'] = pd_dados['MA'] - num_std * pd_dados.close.rolling(ma_len).std().shift(1) #calculo da ma menos desvio padrao
pd_dados['position'] = np.nan
pd_dados['position'][pd_dados.close > pd_dados.MA_Plus] = -1 #calculo de quando esta vendido
pd_dados['position'][pd_dados.close < pd_dados.MA_Minus] = 1 #calculo de quando esta comprado
pd_dados['position'] = pd_dados['position'].fillna(method='ffill')
pd_dados['positionQty'] = np.nan
pd_dados['positionQty'][pd_dados.position != pd_dados.position.shift(1)] = pd_dados.position * exposicao /  pd_dados.close   #calculo da quantidade de acoes negociadas
pd_dados['positionQty'] = pd_dados['positionQty'].fillna(method='ffill')
pd_dados['positionQty'] = pd_dados['positionQty'].fillna(value=0)
pd_dados['notional_reais'] = - (pd_dados['positionQty'] - pd_dados['positionQty'].shift(1)) * pd_dados.close  #calculo das movimentacoes financeiras em reais na compra e venda de acoes
pd_dados['custo'] = - abs((pd_dados['positionQty'] - pd_dados['positionQty'].shift(1)) * pd_dados.close) * custo #calculo do custo
pd_dados['notional_reais'] = pd_dados['notional_reais'] + pd_dados['custo']
pd_dados['notional_reais'] = pd_dados['notional_reais'].cumsum()
pd_dados['notional_equity'] = pd_dados['positionQty'] * pd_dados.close   #calculo do notional em acoes
pd_dados['notional_total'] = pd_dados['notional_reais'] + pd_dados['notional_equity'] #calculo do notional total



fig, (ax1, ax2) = plt.subplots(2, sharex=True)
ax1.plot(pd_dados[['MA', 'close', 'MA_Plus', 'MA_Minus']])
ax2.plot(pd_dados[['position']])  #plot da posicao e graficos de preco
plt.show()


pd_dados['notional_total'].plot()  #plot do resultado
plt.show()
