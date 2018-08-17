from arctic import Arctic
from datetime import datetime, timedelta
import pandas as pd
import pdb
import numpy as np
from pymongo import MongoClient
import time

# IMPORTANTE.
mk_new = 1  # 0: Update last month / 1: Reset all and adjust

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


store_dvd = Arctic('10.51.0.23')
library_dvd = store_dvd['Dvd']
dvd_all = library_dvd.read('Dvd').data


#dvd_ = pd.read_csv("dvd_.csv", sep=';', decimal=',', index_col=0, parse_dates=True, dayfirst=True)
store = Arctic('10.51.0.23')
library = store['MinStore_adj.BVSP']
library_from = store['MinStore.BVSP']

if mk_new == 1:
    start = time.time()  # Start Time
    client = MongoClient('10.51.0.23', 27017)
    print('Realizando a recriação da BD ajustada')

    client.drop_database('arctic_MinStore_adj')
    client.admin.command('copydb', fromdb='arctic_MinStore', todb='arctic_MinStore_adj')

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#  Corrige todos os ativos
if mk_new == 0:
    start = (datetime.now() + timedelta(-30)).date()
    dvd_aux = dvd_all[dvd_all.index.date >= start].copy()
else:
    dvd_aux = dvd_all.copy()

Ativos_full = dvd_all.stock.unique()

for i in Ativos_full:
    dvd_temp = dvd_all[dvd_all.stock == i].copy()
    dvd_temp = dvd_temp.sort_index()

    if dvd_temp.shape[0] != 0:
        print('Ajustando', i)
        try:
            data_adj = library_from.read(i).data
        except:
            continue

        for j in range(0, len(dvd_temp)):
            fator = dvd_temp.fator.values[j]

            ind_ = data_adj.index < dvd_temp.index[j]
            data_adj.loc[ind_, ['open', 'high', 'low', 'close']] = data_adj.loc[ind_, ['open', 'high', 'low', 'close']].values * fator
        data_adj.fillna(method='ffill', inplace =True)
        library.write(i, data_adj)

end = time.time()
print('Operação realizada em:', end - start, 'segundos')
print('------------------------------------------------')
print('')
