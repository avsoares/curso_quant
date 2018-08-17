import pdb
import requests
from os import listdir, walk
from os.path import isfile, join
import warnings
import zipfile
import pandas as pd
from datetime import datetime
import numpy as np
from arctic import Arctic, TICK_STORE
from arctic.date import string_to_daterange
from ftplib import FTP
import numpy as np
import os, shutil
from pytz import timezone
import pytz
import gc
import tzlocal
from ftplib import FTP
import numpy as np
import time

download_ = 1
insert_ = 1

# BVSP_Download file
def download(j):
    print("Baixando => ",files[j])
    fhandle = open(files[j], 'wb')
    ftp.retrbinary('RETR ' + files[j], fhandle.write)
    fhandle.close()

#unzip all magic
def unzip(filename, file_path):
    try:
        print("Unzipping %s" % filename)
        with zipfile.ZipFile(file_path + filename, "r") as zipped:
            zipped.extractall(file_path)
    except Exception as e:
        print(e)

#collect all txt files
def list_txt_files(file_path):
    lst = []

    #get all subdirectories
    dirs = walk(file_path)
    i = 0
    for dir in dirs:
        print("Checking "+dir[0])
        filenames = [f for f in listdir(dir[0]) if isfile(join(dir[0], f))]
        for filename_ in filenames:
            if filename_.lower().endswith('.txt'):
                lst.append(filename_)
                print("Collected %s" %i)
                i += 1
    #return unique list
    return list(set(lst))

#collect all txt files
def list_zip_files(file_path):
    lst = []
    #get all subdirectories
    i = 0
    filenames = [f for f in listdir(file_path)]
    for filename_ in filenames:
        if filename_.lower().endswith('.zip'):
            lst.append(filename_)
            i += 1
    #return unique list
    return list(set(lst))


# Paths -------------
BMFData_path = '/media/asoares/DATA/BMFData/'
download_path = BMFData_path + "BMF_Download/"
temp_path = BMFData_path + "BMF_Temp/"
basepath = BMFData_path
unzip_path = BMFData_path + "BMF_Temp/"

downloaded = list_zip_files(download_path)
downloaded = sorted(downloaded)
files = []

# Baixa arquivos faltantes quando comparado ao FTP
if download_ == 1:
    ftp = FTP('ftp.bmf.com.br')
    ftp.login("", "")
    ftp.cwd("MarketData/BMF")
    files_raw = np.array(ftp.nlst())

    temp_files = list_zip_files(temp_path)
    for i in temp_files:
        os.remove(temp_path + i)
    for i in range(files_raw.shape[0]):
        if "NEG_BMF_" in files_raw[i] and not files_raw[i] in downloaded:
            print(files_raw[i])
            files = files + [files_raw[i]]
    for j in range(len(files)):
        download(j)
        shutil.move(basepath + files[j], temp_path)

store = Arctic('localhost')
alreadyin = store.list_libraries()
first_bd_name = 'TickStore.BMF_'

# Insere os arquivos presentes no TempPath
if insert_ == 1:
    temp_files = list_zip_files(temp_path)
    temp_files = sorted(temp_files)

    # 531
    for j in range(0, len(temp_files)):
    #for j in range(500, 541):
        last_bd_name = temp_files[j][8:14]
        bd_name = first_bd_name + last_bd_name

        if bd_name in alreadyin:
            library = store[bd_name]
        else:
            store.initialize_library(bd_name, lib_type=TICK_STORE)
            library = store[bd_name]
            alreadyin = store.list_libraries()

        print(">>> Executando arquivo numero:", j)
        unzip(temp_files[j], unzip_path)
        zip_files = [temp_files[j][:-3] + 'TXT']
        Header = ['Data', 'Simbolo', 'NumNeg', 'Preco', 'Qtd', 'Time', 'IndAnul', 'DtBuyOffer', 'SeqBuyOffer', 'GenBuy', 'CondBuy', 'DtSellOffer', 'SeqSellOffer', 'GenSell', 'CondSell', 'Direto', 'AgBuy', 'AgSell']
        try:
            temp_ = pd.read_csv("BMF_Temp\\" + zip_files[0], sep=';', decimal=',', names=Header)
        except:
            temp_ = pd.read_csv("BMF_Temp\\apphmb\\intraday\\" + zip_files[0], sep=';', decimal=',', names=Header)
        if temp_.shape[0] < 10:
            try:
                os.remove(temp_path + zip_files[0])
            except:
                os.remove(temp_path + "apphmb\\intraday\\" + zip_files[0])
            shutil.move(temp_path + temp_files[j], download_path)
            continue

        if 1 == 1:
            Symbol = temp_.Simbolo.str.strip().iloc[1:-1]
            Price = pd.to_numeric(temp_.Preco).iloc[1:-1]
            Qtd = pd.to_numeric(temp_.Qtd).iloc[1:-1]
            Direct = temp_.Direto.iloc[1:-1]
            AgressivityBuy = temp_.CondBuy.iloc[1:-1]
            AgressivitySell = temp_.CondSell.iloc[1:-1]
            AgentBuy = temp_.AgBuy.iloc[1:-1]
            AgentSell = temp_.AgSell.iloc[1:-1]

            data_temp = temp_.Data.values
            time_temp = temp_.Time.values

            Time = []
            for i in range(1, len(time_temp) - 1):
                try:
                    temporario = [datetime.strptime(data_temp[i] + " " + time_temp[i], '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=pytz.utc)]
                except:
                    temporario = [datetime.strptime(data_temp[i] + " " + time_temp[i], '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)]
                Time += temporario
            Time = np.array(Time)

            data_ = pd.DataFrame({'Symbol': Symbol.values, 'Price': Price.values, 'Qtd': Qtd.values, 'Direct': Direct.values, 'AgressivityBuy': AgressivityBuy.values, 'AgressivitySell': AgressivitySell.values, 'AgentBuy': AgentBuy.values, 'AgentSell': AgentSell.values}, index=Time)
            Ativos = np.unique(data_.Symbol)

        for i in Ativos:
            data_new = data_[data_.Symbol == i].copy()
            del data_new["Symbol"]
            try:
                library.write(i, data_new)
            except:
                print(i, 'já adicionado.')
            del data_new
            gc.collect()


        try:
            os.remove(temp_path + zip_files[0])
        except:
            os.remove(temp_path + "apphmb\\intraday\\" + zip_files[0])

        shutil.move(temp_path + temp_files[j], download_path)
