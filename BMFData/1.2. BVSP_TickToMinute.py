import pdb
from arctic import Arctic
import pandas as pd
import datetime
from arctic.date import string_to_daterange
import numpy as np
from pymongo import MongoClient

reinserir = 1
atualizar = 1

store = Arctic('localhost')

if not 'MinStore.BVSP' in store.list_libraries():
    store.initialize_library('MinStore.BVSP')
library2 = store['MinStore.BVSP']
all_libs = np.array(sorted(store.list_libraries()))
all_libs = [i for i in all_libs if i[10:16] == 'BVSP_2']

Ativos = []
for lib_ in all_libs:
    library = store[lib_]
    Ativos = Ativos + library.list_symbols()
Ativos = sorted(np.unique(Ativos))

if atualizar == 1:
    if reinserir == 0:
        all_libs = all_libs[-2:]

# 1065
for i in range(0, len(Ativos)):
#for i in range(800, 1065):
    Ati_ = Ativos[i]
    print('Adicionando o ativo:', Ati_)
    data = pd.DataFrame()
    for lib_ in all_libs:
        library = store[lib_]
        mes = int(lib_[-2:])
        ano = int(lib_[-6:-2])
        mes2 = mes + 1 if mes + 1 <=12 else 1
        ano2 = ano if mes2 != 1 else ano + 1
        rng = [datetime.date(ano, mes, 1), datetime.date(ano2, mes2, 1)]
        date_range = string_to_daterange("%s-%s" % (rng[0].strftime("%Y%m%d%H%M%z"), rng[-1].strftime("%Y%m%d%H%M%z")))
        try:
            in_data_raw = library.read(Ati_, date_range=date_range)
            in_data_raw = in_data_raw[in_data_raw.Direct != 1]  # Exclui diretas
            in_data_raw['Fin'] = in_data_raw.Qtd * in_data_raw.Price  # Volume financeiro

            in_data = in_data_raw['Price'].resample('1Min').ohlc()
            in_data['volume'] = in_data_raw['Fin'].resample('1Min', how='sum')
            in_data['volume'].fillna(value=0, inplace=True)
            data = pd.concat([data, in_data]).reset_index().drop_duplicates().set_index('index')
            data.sort_index(inplace=True)
        except:
            print("Erro ao extrair o ativo!")
    try:
        data = data[data.volume > 0]
        if reinserir != 1:
            data_old = library2.read(Ati_).data
            data = pd.concat([data, data_old]).reset_index().drop_duplicates().set_index('index')
            data.sort_index(inplace=True)
        library2.write(Ati_, data)
    except:
        try:
            data = data[data.volume > 0]
            library2.write(Ati_, data)
        except:
            print("ERRO ATIVO")
