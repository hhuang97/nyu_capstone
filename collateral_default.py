from data_parser import get_all_data, get_2018_data, get_2020_data, get_vix, get_cdx_ig
from data_parser import get_ticker_df
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.stats import norm
from scipy.linalg import cholesky
from CDX_IG import cdx_ig_names

def default_rate(df,R=.06):
    #assume constant lambda, spread ~ lambda(1-R)
    df['lambda'] = df['Spread (bp)']/(1-R)/100
    return df

def default_indicators(cov,R=.06,df = True):
    '''
    :param cov: equity covariance between stock price
    :param R: recovery rate.
    :return: dataframe with an extra column, simulated default time.
    '''
    ig = get_cdx_ig()
    n=len(ig.index)
    ig = default_rate(ig,R)
    u = norm.cdf(np.random.multivariate_normal(np.zeros(n),cov)) #uniformly distributed r.v.
    default_ts = np.array([-np.log(1-u[i])/ig['lambda'][i] for i in range(n)])
    ig['default_ts'] = default_ts
    if df == True:
        return ig
    else:
        return default_ts

def equity_cov(tickers,startdate,enddate):
    #TODO: need stock movement for components under CDX - output covariance matrix
    list(map(lambda x: get_ticker_df(x,startdate,enddate), tickers))
    pass

if __name__ == '__main__':
    #ig0 = get_cdx_ig()
    #n = len(ig0.index) # no correlation
    #ig = default_indicators(np.eye(n)) #missing covariance matrix


