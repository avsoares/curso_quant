%matplotlib
import pandas as pd
from datetime import datetime
import numpy as np
from arctic import Arctic
import numpy as np
import matplotlib.pyplot as plt
import datetime


store = Arctic('localhost')

library = store['MinStore.BVSP']
library_backtest = store['Backtest.Simples']

rewrite = 0

date_sum_volume = datetime.date(2017, 9, 1)
num_ativos = 30

if rewrite == 1 or not 'sum_volume' in library_backtest.list_symbols():
    lista_ativos = library.list_symbols()
    lista_dados_volume = pd.DataFrame([])
    for ativo in lista_ativos:
        if not ativo[-1] in ['L', 'B'] :
            print(ativo)
            dados_volume = library.read(ativo).data.volume.to_frame().rename(columns={'volume': ativo})
            dados_volume = dados_volume[dados_volume.index.date < date_sum_volume]
            lista_dados_volume = lista_dados_volume.join(dados_volume, how='outer')
    sum_volume = lista_dados_volume.sum()
    library_backtest.write('sum_volume', sum_volume)

sum_volume = library_backtest.read('sum_volume').data
lista_ativos = list(sum_volume.sort_values(ascending=False).iloc[:num_ativos].index)


#Testando um simples estratégia de médias móveis para o ativo ABEV3

pd_result = pd.DataFrame([])

ma_len = 120
num_std = 1.5
exposicao = 1000
custo = 0.05 / 100 * 0

for ativo in lista_ativos:
    print(ativo)
    pd_dados_raw = library.read(ativo).data #import de dados
    pd_dados_raw = pd_dados_raw[pd_dados_raw.index.date > date_sum_volume]
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
    pd_dados[ativo] = pd_dados['notional_reais'] + pd_dados['notional_equity'] #calculo do notional total
    pd_result = pd_result.join(pd_dados[ativo].to_frame(), how='outer')

pd_result = pd_result.fillna(method='ffill')
pd_result = pd_result.fillna(value=0)
pd_result['total'] = pd_result.sum(axis=1)
pd_result['total'].plot()

resultado_end_day = pd_result['total'].groupby(pd_result.index.date).last()
resultadoFinanceiro_strategy = round(resultado_end_day.iloc[-1], 2)  # Resultado financeiro total

resultado_per_day = resultado_end_day - resultado_end_day.shift(1)
sharpe_strategy = round((resultado_per_day.mean() / resultado_per_day.std()) * (252 ** 0.5), 2) # Sharpe da estrategia

# Cálculo de drawdown
arr_total = pd_result['total'].values
max_value = 0
min_value = 0
drawdown = 0
time_drowdown = 0
max_time_underwater = 0
max_time_underwater_date = 0
underwater = 0
for i in range(len(arr_total)):
    underwater += 1
    if arr_total[i] > max_value:
        if underwater > max_time_underwater:
            max_time_underwater = underwater
            max_time_underwater_date = i
        underwater = 0
        max_value = arr_total[i]
        min_value = arr_total[i]
    elif arr_total[i] < min_value:
        min_value = arr_total[i]
        if min_value - max_value < drawdown:
            drawdown = min_value - max_value
            time_drowdown = i
print('Drawdown máx de: ', drawdown, ' Na data de: ', pd_result.index[time_drowdown])
print('Periodo maximo de underwater entre: ', pd_result.index[max_time_underwater_date-max_time_underwater], pd_result.index[max_time_underwater_date])
