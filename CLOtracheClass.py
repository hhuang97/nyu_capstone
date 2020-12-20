from waterfall import CEA, CCC_ratio, carrying_value, sort_loan_mp, \
    sort_loan_rating, total_notional, oc_ratio
from data_parser import get_all_data, get_2018_data, get_2020_data, get_vix, get_cdx_ig, get_cdx_hy
import numpy as np


# see CLO primer by s&p
# https://www.capitaliq.com/CIQDotNet/CreditResearch/RenderArticle.aspx?articleId=2103669&SctArtId=460169&from=CM&nsl_code=LIME&sourceObjectId=10701580&sourceRevId=1&fee_ind=N&exp_date=20280921-00:30:27


class clotranche(object):
    def __init__(self, trancheclass, unpaid_notional):
        self.trclass = trancheclass
        self.note = unpaid_notional/12. # assume quarterly payment for 3 years.
        self.unpaid_n = unpaid_notional
        self.paid_i = 0.
        self.cp = 0. #this should be the value we need to solve.
        # For assessing A_j's stochastic process.
        self.currD = 0.
        self.prevD= 0.

    def pay_interest(self,interest_in):
        self.prevD = self.currD #new
        self.currD = 0. #new
        self.paid_i+=interest_in
        self.currD += interest_in #new

    def pay_notional(self, principal_in):
        if self.unpaid_n - principal_in >=0.:
            self.unpaid_n -= principal_in
            self.currD += principal_in #new
        else:
            self.unpaid_n = 0.

    def set_cp(self,coupon):
        self.cp = coupon


class clo(object):
    def __init__(self,tranches, collateral, oc_benchmark, maturity = 5.,payperiod = 1./4):
        self.tranches = tranches #order: the most senior tranche to equity.
        self.collateral = collateral
        self.mat = maturity
        self.payperiod = payperiod # assume semi-annual payment
        self.age = 0.
        self.ocbar = oc_benchmark #raio between asset and liability, if lower than the bench
        self.default_events = {}
        self.default_pv = 0.
    def default_flag(self):
        loans = self.collateral.loans
        default_names = set()
        for loan in loans:
            if (loan.default_t <= self.age) and (loan.issuer not in self.default_events.keys()):
                default_amount = loan.pv * (1 - loan.rec)
                self.default_events[loan.issuer] = (loan.default_t,default_amount)
                print(loan.issuer + ' defaults at year {}:'.format(loan.default_t) + str(default_amount))
                self.default_pv += default_amount
                default_names.add(loan.issuer)
        self.collateral.default_adjust(default_names)

    def report(self):
        cloinfo = 'age:{};'.format(self.age)
        equity_interest = 'equity investor receives interest payment {}'.format(self.tranches[-1].paid_i)
        equity_principal = 'And receive extra notional {}'.format(self.collateral.p_reserve-self.tranches[-1].unpaid_n)

        print(cloinfo)
        print('PnL for all tranches')
        for tranche in self.tranches[:-1]:
            print('{}: unpaid notional: {}; received interest: {}'.\
                  format(tranche.trclass,tranche.unpaid_n,tranche.paid_i))
        print('Equity tranche earns ', self.equity_yield())
        print(equity_interest)
        print(equity_principal)
        print('-------------------------------')
        print('Default Events with total default amount {}:'.format(self.default_pv))
        print(self.default_events)

    def callclo(self):
        #pay back all principal
        final_reserve = self.collateral.p_reserve
        n = len(self.tranches)
        for i in range(n-1):
            if final_reserve > 0 :
                k = min(final_reserve,self.tranches[i].unpaid_n)
                self.tranches[i].pay_notional(k)
                final_reserve -= k
        self.collateral.p_reserve = final_reserve
        self.report()

    def equity_yield(self):
        return self.tranches[-1].paid_i - self.tranches[-1].unpaid_n + self.collateral.p_reserve

    def tranche_asset(self,j): # A_j,
        asset = self.tranches[j].note *12. - self.tranches[j].unpaid_n + self.tranches[j].paid_i
        for tranche in self.tranches[j+1:]:
            asset += tranche.note *12. - tranche.unpaid_n + tranche.paid_i
        return asset

    def pay_clo_interest(self):
        # one-time payment, run this function every 6 month,
        # use received interest to pay down the interest waterfall
        self.age+= self.payperiod
        test_results, unpaid_paripassu_p = oc_ratio(self.collateral,self.tranches)#check oc ratio test.
        i=0
        #check if have enough cash reserve from loan collateral
        #check if the senior coverage test is in compliance
        while (self.collateral.i_reserve >0) and (i <len(self.tranches)):
            # for the most senior tranche AAA, we don't need to check oc test
            scheduled_interest = self.tranches[i].unpaid_n * self.tranches[i].cp
            if ((i>1) and (test_results[i-2] < self.ocbar[i-2])):
                print('! Breach OC test on tranche ' + str(self.tranches[i-1].trclass))
                j = 0 #starting from AAA
                required_principal_payment =  unpaid_paripassu_p[i-2] - \
                    test_results[i-2]*unpaid_paripassu_p[i-2]/self.ocbar[i-2]

                while (required_principal_payment >0) and (required_principal_payment <= self.collateral.i_reserve):
                    if j == i:
                        break
                    else: #be able to pass the test
                        k =min(required_principal_payment, self.tranches[j].unpaid_n)
                        self.tranches[j].pay_notional(k)
                        self.collateral.i_reserve -= k
                        required_principal_payment -= k

                    j+=1

            if self.collateral.i_reserve <= scheduled_interest: # then the while loop breaks
                self.tranches[i].pay_interest(self.collateral.i_reserve)
                self.collateral.i_reserve = 0.
            else:
                self.collateral.i_reserve -= scheduled_interest
                self.tranches[i].pay_interest(scheduled_interest)

            i+=1

        self.tranches[-1].pay_interest(self.collateral.i_reserve)
        self.collateral.i_reserve = 0.


    def pay_clo_principal(self):
        j = 0
        while self.collateral.p_reserve > 0 and j < len(self.tranches):
            k = min(self.tranches[j].unpaid_n, self.collateral.p_reserve, self.tranches[j].note)
            self.tranches[j].pay_notional(k)
            self.collateral.p_reserve -= k
            j += 1



