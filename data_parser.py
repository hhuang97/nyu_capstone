import pandas as pd
import pickle
import numpy as np
import yfinance as yf

_RAW_DATA_FILE = 'data/CLO_Data.xlsx'
_PICKLED_DATA_FILE = 'data/all_data.p'
_STRESS_2016 = 'data/stress_2018.p'
_STRESS_2020 = 'data/stress_2020.p'
_VIX = 'data/vix.p'
_CDX_IG = 'data/cdx_ig.p'
_STOCKS_IG = 'data/stock_ig.p'


def process_data():
    main_df = pd.read_excel(_RAW_DATA_FILE, sheet_name='Sheet1')
    main_df = main_df.set_index('Date')
    with open(_PICKLED_DATA_FILE, 'wb') as f:
        pickle.dump(main_df, f)
    stress_2016 = main_df[(main_df.index > '2018-1-1') & (main_df.index < '2018-12-31')]
    stress_2020 = main_df[(main_df.index > '2020-3-1') & (main_df.index < '2020-10-31')]
    with open(_STRESS_2016, 'wb') as f:
        pickle.dump(stress_2016, f)
    with open(_STRESS_2020, 'wb') as f:
        pickle.dump(stress_2020, f)


def get_2018_data():
    with open(_STRESS_2016, 'rb') as f:
        df_2016 = pickle.load(f)
    return df_2016


def get_2020_data():
    with open(_STRESS_2020, 'rb') as f:
        df_2020 = pickle.load(f)
    return df_2020


def get_all_data():
    with open(_PICKLED_DATA_FILE, 'rb') as f:
        df_all = pickle.load(f)
    return df_all

def cdx_process():
    # df = pd.read_excel('data/CDX HY Series 35.xlsx', sheet_name='Worksheet')
    df = pd.read_excel('data/CDX IG Series 35.xlsx', sheet_name='Worksheet')
    #df['Spread'] = df['Spread (bp)'].apply(lambda x: np.nan if str(x).strip() == 'N.A.' else float(x))
    #exclude na terms
    df_cdx_ig = df[df['Spread (bp)']!='N.A.']
    df_vix = pd.read_excel('data/VIX.xlsx', sheet_name='Sheet1')
    df_cdx_ig = df_cdx_ig.set_index(df_cdx_ig.columns[2])
    df_vix = df_vix.set_index(df_vix.columns[0])

    with open(_VIX,'wb') as f:
        pickle.dump(df_vix,f)

    with open(_CDX_IG,'wb') as f:
        pickle.dump(df_cdx_ig,f)

def get_vix():
    with open(_VIX,'rb') as f:
        df_vix = pickle.load(f)
    return df_vix

def get_cdx_ig():
    with open(_CDX_IG,'rb') as f:
        df_cdx_ig = pickle.load(f)
    return df_cdx_ig

def write_cdx_stocks(cdx_func, filepath):
    df = cdx_func()
    symbols = df.index
    stocks = {}
    for _sym in symbols:
        sym = _sym.strip()
        try:
            stock_data = yf.Ticker(sym)
            stock_df = stock_data.history(period='10y', interval='1d', auto_adjust=False)
            stocks[sym] = stock_df
        except:
            print(sym)
    with open(filepath, 'wb') as f:
        pickle.dump(stocks, f)


def get_stocks_ig():  # map of symbol -> df
    # no data for ABXCN, CNQCN, COXENT, ENBCN, TRPCN
    with open(_STOCKS_IG,'rb') as f:
        res = pickle.load(f)
    return res

if __name__ == '__main__':
    # process_data()
    # x = get_2018_data()
    # y = get_2020_data()
    # z = get_all_data()
    write_cdx_stocks(get_cdx_ig, _STOCKS_IG)
    cdx_process()
    cdxig = get_cdx_ig()
    vix = get_vix()
    print('done')
