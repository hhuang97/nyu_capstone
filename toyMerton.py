from data_parser import get_all_data, get_2018_data, get_2020_data, get_vix, get_cdx_ig, get_cdx_hy
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.stats import norm
from scipy.linalg import cholesky
from CLOtracheClass import clotranche, clo
from LoanClass import loan, collateral
from waterfall import CEA, CCC_ratio, carrying_value, sort_loan_mp, \
    sort_loan_rating, total_notional, oc_ratio
from collateral_default import default_rate, default_indicators,equity_cov

import math
from CDX_IG import cdx_ig_names, cdx_hy_names

#  simulate loan collateral; simulate tranche; simulate clo;
# - (if data are unknown) assign rating to each loan, sort loans w.r.t their spread DONE
#  - start with 4 tranches, AAA,AA,A,equity:  DONE
# ----- https://www.stout.com/en/insights/article/primer-valuation-clo-equity-financial-reporting
# ----- https://services.sbcera.org/sirepub/cache/2/retkovizcy4dcex344yjp345/8537612062020023548742.PDF
# use Gaussian Copula to simulate default times for each loan, one path Done

# function that builds interest/principal reserves, assumption (mini clo)
# - for simplicity, we'll assume the legal maturity is 5yrs
# - reinvestment period ends after 2 years,
# i.e., build reserve for 2 yrs before amortization period
# - equity investor doesn't call the clo. add a call function to clo object. done

#TODO: simulate time series for market price from


#TODO: Merton's model,

#self, issuer, spread, pv, rating, prepay=0.15,rec = 0.06

total_n = 5.*10**7
avg_libor_spread = 320. * 10**(-4)
libor =0.25/100.


# For simulation purpose
def assign_rating_notional(df, total_notional=total_n, ccc_ratio = 7.5/100.):
    n = len(df.index)
    ccc_num = math.ceil(n*ccc_ratio)
    ccc_notional = [total_notional * ccc_ratio/ccc_num] * ccc_num
    non_ccc_notional = [total_notional *(1-ccc_ratio)/(n-ccc_num)] * (n-ccc_num)
    loans_pvs = np.array(ccc_notional + non_ccc_notional)
    ratings = np.array(['CCC'] * ccc_num + ['B'] * (n-ccc_num))
    return ratings, loans_pvs

def assign_loan_spread(df,avg_libor = avg_libor_spread):
    df = df.sort_values(by = 'Spread (bp)', ascending = False)
    n = len(df.index)
    loan_libor_spreads = df['Spread (bp)']/sum(df['Spread (bp)']) *(n*avg_libor)
    return loan_libor_spreads


def libor_spreads(spreads): # maybe just assume constant for now
    pass


def create_loan_collateral(df):
    df = df.sort_values(by='Spread (bp)',ascending=False) # from lowest to highest
    ratings,pvs = assign_rating_notional(df)
    libor_spreads  = assign_loan_spread(df)
    loans = np.array([loan(df.index[i],libor_spreads[i],pvs[i],ratings[i]) \
                      for i in range(len(df.index))])

    # default simulator?
    return loans

def create_tranches(i,tranche_cps):
    if i==4: #AAA,AA,BBB,Equity
        # % of capital, 32
        aaa,aa = clotranche('AAA',32*10**6),clotranche('AA',7.7*10**6)
        bbb,equity = clotranche('A',6.05*10**6),clotranche('Equity',4.25*10**6)
        tranches = np.array([aaa,aa,bbb,equity])
        for i in range(4):
            tranches[i].set_cp(tranche_cps[i])
        return tranches

#self,tranches, loans, oc_benchmark, maturity = 5.,payperiod = 1./4):

def create_clo(i=4,tranche_cps=[0.0218,0.0335,0.0601,0.]):
    df = get_cdx_hy()
    collaterals = collateral(create_loan_collateral(df))
    tranches = create_tranches(i,tranche_cps) #1.02 for AAA and AA, 1.07 for A
    miniclo = clo(tranches,collaterals,np.array([1.2,1.07]))
    return miniclo


def gaussian_copula_di(clo):
    df_hy = get_cdx_hy()
    df_hy = df_hy.sort_values(by='Spread (bp)', ascending=False)
    n = len(df_hy.index)
    di = default_indicators(np.eye(n),df_hy,df = False)
    i=0
    for loan in clo.collateral.loans:
        loan.default_t = di[i]
        i+=1
    return clo



def reinvestment_period(clo,yr=2.):
    '''
    :param yr: the length of reinvestment period.
    assume all loans have quarterly payment.
    '''
    while clo.age <=yr:
        clo.default_flag() #check which loans default
        clo.collateral.build_reserve() #collect interest payment
        clo.pay_clo_interest()
    return clo

def amortization_period(clo,mat=5.):
    while clo.age <= mat:
        clo.default_flag()
        clo.collateral.build_reserve()
        clo.pay_clo_interest()
        clo.pay_clo_principal()
    return clo

def life_cycle(clo,yr = 2., mat =5.):
    clo = reinvestment_period(clo)
    return amortization_period(clo)



if __name__ == '__main__':
    clo01 = create_clo()
    clo01 = gaussian_copula_di(clo01) # default_time added
    clofinal = life_cycle(clo01)
    clofinal.callclo()
    equity_earned = clofinal.equity_yield()








