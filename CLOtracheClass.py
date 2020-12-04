from waterfall import CEA, CCC_ratio, carrying_value, sort_loan_mp, \
    sort_loan_rating, total_notional, oc_ratio
import numpy as np


class clotranche(object):
    def __init__(self, trancheclass, unpaid_notional):
        self.trclass = trancheclass
        self.note = unpaid_notional/10. # assume semi-annual payment
        self.unpaid_n = unpaid_notional
        self.paid_i = 0.
        self.cp = 0. #this should be the value we need to solve.

    def pay_interest(self,interest_in):
        self.paid_i+=interest_in

    def pay_notional(self, principal_in):
        if self.unpaid_n - principal_in >=0.:
            self.unpaid_n -= principal_in
        else:
            self.unpaid_n = 0.

    def set_cp(self,coupon):
        self.cp = coupon


class clo(object):
    def __init__(self,tranches, loans, oc_benchmark, maturity = 5.,payperiod = 1./2):
        self.tranches = tranches #order: the most senior tranche to equity.
        self.loans = loans
        self.mat = maturity
        self.payperiod = payperiod # assume semi-annual payment
        self.age = 0.
        self.ocbar = oc_benchmark #raio between asset and liability, if lower than the bench

    def default_happen(self,default_events):
        self.loans.default_adjust(default_events)

    def pay_clo_interest(self):
        #TODO: not finished 
        self.age+= self.payperiod
        #check oc ratio test.
        test_results = oc_ratio(self.loans,self.tranches)
        for i in range(len(self.tranches)-1):
            if test_results[i] < self.ocbar[i]:
                # breach the test, pay

    def pay_clo_principal(self):
        #TODO: not finished
        for tranche in self.tranches:
            tranche.pay_notional(min(tranche.unpaid_n,tranche.note,self.loans.total_notional))






