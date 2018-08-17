%matplotlib
import pandas as pd
from datetime import datetime
import numpy as np
from arctic import Arctic
import numpy as np
import matplotlib.pyplot as plt
import datetime
import seaborn as sb


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


variavel1 = np.arange(60, 60 * 4.1, 60)
variavel2 = np.arange(1, 2.6, 0.5)

ma_len = 120
num_std = 1.5
exposicao = 1000
custo = 0.05 / 100 * 0

#IMPORT DE DADOS
print('Importando dados')
pd_dados_raw = pd.DataFrame([])
for ativo in lista_ativos:
    pd_import_raw = library.read(ativo).data.close.to_frame() #import de dados
    pd_import_raw = pd_import_raw[pd_import_raw.index.date > date_sum_volume]
    pd_dados_raw = pd_dados_raw.join(pd_import_raw.rename(columns={'close' : ativo}), how='outer')
pd_dados_raw = pd_dados_raw.fillna(method='ffill')


matrix_sharpe = np.zeros((len(variavel1), len(variavel2)))
matrix_resultado_financeiro = np.zeros((len(variavel1), len(variavel2)))
matrix_drawdown = np.zeros((len(variavel1), len(variavel2)))

print('Iniciando backtest')
for idx_1 in range(len(variavel1)):
    for idx_2 in range(len(variavel2)):
        ma_len = int(variavel1[idx_1])
        num_std = variavel2[idx_2]

        pd_result = pd.DataFrame([])

        for ativo in lista_ativos:
            pd_dados = pd_dados_raw[ativo].to_frame().rename(columns={ativo : 'close'})
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
                    drawdown = round(min_value - max_value, 2)
                    time_drowdown = i

        matrix_sharpe[idx_1, idx_2] = sharpe_strategy
        matrix_resultado_financeiro[idx_1, idx_2] = resultadoFinanceiro_strategy
        matrix_drawdown[idx_1, idx_2] = drawdown
        print('\nResultado para os parametros ', variavel1[idx_1], variavel2[idx_2])
        print('Sharpe: ', sharpe_strategy, ' Profit: ', resultadoFinanceiro_strategy, ' Drawdown: ', drawdown)

pd_sharpe = pd.DataFrame(matrix_sharpe, index=variavel1, columns=variavel2)
pd_resultado_financeiro = pd.DataFrame(matrix_resultado_financeiro, index=variavel1, columns=variavel2)
pd_drawdown = pd.DataFrame(matrix_drawdown, index=variavel1, columns=variavel2)

sb.heatmap(pd_sharpe)
