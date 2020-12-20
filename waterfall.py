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
    if loan.default == False:
        if loan.mp >= .8:
            loan.cv = loan.pv
        else:
            loan.cv = loan.pv * loan.mp
    else:
        loan.cv = loan.pv*loan.rv

def sort_loan_mp(loans):
    def myFunc(e):
        return e.mp
    loans.sort(key=myFunc) #from lowerest to highest
    return loans

def sort_loan_rating(loans):
    ccc = np.array([loan for loan in loans if 'C' in loan.rating])
    # def myFunc(e):
    #     return len(e)
    pass

def total_notional(loans):
    return np.sum([loan.pv for loan in loans])

def CCC_ratio(loans):
    ccc = np.array([loan for loan in loans if 'C' in loan.rating])
    if total_notional(loans) != 0:
        return total_notional(ccc)/total_notional(loans)
    else:
        return 1

def CEA(loans,benchmark = 0.075 ):
    '''
    :param loans: array of the entire loan collateral objects
    '''
    ccc_r = CCC_ratio(loans)
    cea = 0.
    if ccc_r > benchmark:
        ccc = sort_loan_mp([loan for loan in loans if 'C' in loan.rating])
        benchmark = total_notional(loans)*benchmark
        ccc_pool,i = 0.,0
        while ccc_pool < benchmark:
            cea += (ccc[i].mp-ccc[i].cv/ccc[i].pv) * (ccc[i].pv)
            ccc_pool += loans[i].pv
            i+=1
    # if cea !=0.:
    #     print(cea)
    return cea

def oc_ratio(collateral,liabilities):
    '''
    :param loans: array of loan objects, with attribute rating, market value
                  carrying value,
    :param liabilities: sorted from the most senior tranche to the lower,
                        AAA,AA,A,BBB,BB,B, then equity
    :return: array of OC ratios for testing on each tranche.
    '''
    loans = collateral.loans
    adjusted_cv = np.sum(list(map(lambda x: x.cv,loans))) - CEA(loans) + collateral.p_reserve
    unpaid_ns = np.array([i.unpaid_n for i in liabilities])
    unpaid_ns_paripassu = np.cumsum(unpaid_ns[:-1]) #excluding equity
    return adjusted_cv/unpaid_ns_paripassu, unpaid_ns_paripassu



