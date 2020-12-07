from data_parser import get_all_data, get_2018_data, get_2020_data, get_vix, get_cdx_ig
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.stats import norm
from scipy.linalg import cholesky

#TODO: building simple cashflow waterfall model
#TODO: loan objects with attribute
      #cv: carrying value,
      #pv: par value, mp: current market price %,
      #rv: value giving by rating %
      #default: default status, true or false,
      #rec: recovery rate, prepay: prepayment rate
      #rating:
      #spread:

    # OC ratio = adjusted carrying value of collateral loan balance/unpaid notional pari-passu .
    # adjusted carrying value = carrying value - excess adjustment

#TODO: data needed: components under HY loans
#TODO: simulation of collateral composition of loans issued by components under CDX.

def carrying_value(loan):
    if loan.defualt == False:
        if loan.mp >= .8:
            loan.cv = loan.pv
        else:
            loan.cv = loan.pv * loan.mp
    else:
        loan.cv = loan.pv*loan.rv

def sort_loan_mp(loans):
    def myFunc(e):
        return e.mp
    return loans.sort(key=myFunc) #from lowerest to highest

def sort_loan_rating(loans):
    ccc = np.array([loan for loan in loans if 'C' in loan.rating])
    # def myFunc(e):
    #     return len(e)
    pass

def total_notional(loans):
    return np.sum([loan.pv for loan in loans])

def CCC_ratio(loans):
    ccc = np.array([loan for loan in loans if 'C' in loan.rating])
    return total_notional(ccc)/total_notional(loans)

def CEA(loans,benchmark = 0.07 ):
    '''
    :param loans: array of the entire loan collateral objects
    '''
    ccc_r = CCC_ratio(loans)
    cea=0.
    if ccc_r > 0.07:
        ccc= sort_loan_mp(np.array([loan for loan in loans if 'C' in loan.rating]))
        benchmark = total_notional(loans)*0.07
        ccc_pool,i = 0.,0
        while ccc_pool < benchmark:
            cea += (loans[i].mp-loans[i].cv/100.) * (loans[i].par)
            ccc_pool += loans[i].par
    return cea

#TODO: array of liabilities objects, attributes:
       # cp: coupon
       # tranche
       # unpaid_n: unpaid notional
       # paid_i: paid interest

def oc_ratio(loans,liabilities):
    '''
    :param loans: array of loan objects, with attribute rating, market value
                  carrying value,
    :param liabilities: sorted from the most senior tranche to the lower,
                        AAA,AA,A,BBB,BB,B, then equity
    :return: array of OC ratios for testing on each tranche.
    '''
    adjusted_cv = np.sum(list(map(carrying_value,loans))) - CEA(loans)
    unpaid_ns = np.array([i.unpaid_n for i in liabilities])
    unpaid_ns_paripassu = np.cumsum(unpaid_ns[:-1]) #excluding equity
    return adjusted_cv/unpaid_ns_paripassu, unpaid_ns_paripassu



