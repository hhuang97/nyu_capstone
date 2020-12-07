from data_parser import get_all_data, get_2018_data, get_2020_data, get_vix, get_cdx_ig, get_cdx_hy
from data_parser import get_ticker_df
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.stats import norm
from scipy.linalg import cholesky
from CDX_IG import cdx_ig_names, cdx_hy_names

def default_rate(df,R=.06):
    #assume constant lambda, spread ~ lambda(1-R)
    # R is percent value,
    df['lambda'] = df['Spread (bp)']/(1-R)/10000
    return df

def default_indicators(cov,cdxdf, R=.06,df = True):
    '''
    :param cov: equity covariance between stock price
    :param R: recovery rate.
    :return: dataframe with an extra column, simulated default time.
    '''
    n = len(cdxdf.index)
    cdxdf = default_rate(cdxdf,R)
    u = norm.cdf(np.random.multivariate_normal(np.zeros(n),cov)) #uniformly distributed r.v.
    default_ts = np.array([-np.log(1-u[i])/cdxdf['lambda'][i] for i in range(n)])
    cdxdf['default_ts'] = default_ts
    if df == True:
        return cdxdf
    else:
        return default_ts

def equity_cov(tickers,startdate,enddate):
    #TODO: need stock movement for components under CDX - output covariance matrix
    list(map(lambda x: get_ticker_df(x,startdate,enddate), tickers))
    pass

if __name__ == '__main__':
    ig0 = get_cdx_ig()
    hy0 = get_cdx_hy()
    n = len(hy0.index) # no correlation
    ig = default_indicators(np.eye(n),hy0) #missing covariance matrix


