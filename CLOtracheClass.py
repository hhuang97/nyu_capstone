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
        # one-time payment, run this function every 6 month,
        # use received interest to pay down the interest waterfall
        self.age+= self.payperiod
        test_results, unpaid_paripassu_p = oc_ratio(self.loans,self.tranches)#check oc ratio test.

        i=0
        #check if have enough cash reserve from loan collateral
        #check if the senior coverage test is in compliance
        while (self.loans.i_reserve >0) and (i <len(self.tranches)):
            # for the most senior tranche AAA, we don't need to check oc test
            scheduled_interest = self.tranches[i].unpaid_n * self.tranches[i].cp

            if i>1 and test_results[i-1] < self.ocbar[i-1]:
                j = 0 #starting from AAA
                required_principal_payment =  unpaid_paripassu_p[i-1] - \
                    test_results[i-1]*unpaid_paripassu_p[i-1]/self.ocbar[i-1]

                while (required_principal_payment >0) and (required_principal_payment <= self.loans.i_reserve):
                    if j == i:
                        break
                    else: #be able to pass the test
                        k =min(required_principal_payment, self.tranches[j].unpaid_n)
                        self.tranches[j].pay_notional(k)
                        self.loans.i_reserve -= k
                        required_principal_payment -= k

                    j+=1

            if self.loans.i_reserve <= scheduled_interest:
                self.loans.i_reserve = 0. # then the while loop breaks
                self.tranches[i].pay_interest(self.loans.i_reserve)
            else:
                self.loans.i_reserve -= scheduled_interest
                self.tranches[i].pay_interest(scheduled_interest)

            i+=1


    def pay_clo_principal(self):
        #TODO: not finished
        j = 0
        while self.loans.p_reserve > 0 and j < len(self.tranches):
            k = min(self.tranches[j].unpaid_n, self.loans.p_reserve, self.tranches[j].note)
            self.tranches[j].pay_notional(k)
            self.loans.p_reserve -= k
            j += 1




