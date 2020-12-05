
from waterfall import CEA, CCC_ratio, carrying_value, sort_loan_mp, \
    sort_loan_rating, total_notional

class loan(object):
    def __init__(self, issuer, spread, pv, rating, prepay=0.15,rec = 0.06):
        self.issuer = issuer #name
        self.spread = spread/2. #from CDX sheet #assume semi-annual payment
        self.semi_annual_pay = pv/10. #assuming all 5 years maturity for simplicity
        self.cv =  pv #carrying value
        self.pv = pv #par value, dollar amount
        # for our simulation purpose, just set all mp = pv,
        # in other words, assume mp is all constant. only default would change cv.
        #TODO: we can actually simulate the market price by making sure the average is equal
        # to the leveraged loan market price. So we have the time series of loan market price,
        # we need a function to set the new market price, whenever we check for oc ratio.
        self.mp = 1. #mp: current market price %
        # loan.rv = mp #rv: value giving by rating % simplify this.
        self.rating = rating #TODO: missing rating data to calculate CCC ratio.
        self.default = False
        self.rec = rec
        self.prepay = prepay

    def set_cv(self):
        # must run this function after creating a loan object
        self.cv = self.pv if self.mp >= .8 else self.cv = self.pv * self.mp
        #else: #this is correct way, but too much complicated here.
            # if default, then just treat it as cv*rec

    def set_mp(self,new_mp):
        self.mp  = new_mp

    def set_spread(self,new_spread): #changing spread, won't be used.
        self.spread = new_spread

    def set_default(self):
        self.default = True
        self.semi_annual_pay = 0.
        self.cv *= self.rec # if default, just set as the original * recovery rate.
        self.pv = 0.  # easier to set pv as 0, then no interest paid after the loan defaults.

    # def set_rv(self,rv):
    #     self.rv = rv

    def set_rating(self,new_rating): # for downgrading events
        self.rating = new_rating

    #def defualt_rate(self,CDS):


class collateral(object):
    def __init__(self,loans):
        self.loans = loans  #numpy array of loans
        self.ccc_ratio = CCC_ratio(loans)
        self.total_notional = total_notional(loans)
        self.p_reserve = 0. # principal paid by loans and potential recoveries
        self.i_reserve = 0. # received interest later used by interest waterfall payment

    def build_reserve(self):
        #semi-annual payment, assuming all loans are paid at exactly same time
        interest_pay = 0
        notional_pay = 0
        for loan in self.loans:
            if loan.default == False:
                interest_pay += loan.pv*loan.spread
                notional_payment = loan.semi_annual_pay * (1+loan.prepay)
                if loan.pv <= notional_payment:
                    notional_pay += loan.pv
                    loan.pv, loan.cv = 0., 0.
                else:
                    notional_pay += notional_payment
                    loan.pv -= notional_payment
                    loan.set_cv()
        self.p_reserve += notional_pay
        self.i_reserve += interest_pay

    def loan_downgrading(self,dg_file):
        # downgrading_file, dictionary, loan issuer: new rating
        #recalculate ccc_ratio, and cea
        # assume no downgrading happen for simplicity of the model
        pass

    def default_adjust(self,default_events):
        # default_events, dictionary, loan issuer: new default happen
        # readjust oc ratio, total notional set to recovery rate
        for loan in self.loans:
            if loan.issuer in default_events.keys():
                loan.set_default() # loans status change to default,
                                   # carrying value and par value are all scaled down.
                self.p_reserve += loan.cv #potential recoveries
        # adjust carrying value.

    def set_ccc_ratio(self):
        #TODO: loan downgrading, match loan.issuer and change rating
        self.ccc_ratio = CCC_ratio(self.loans)

    def sort_mp(self):
        self.loans = sort_loan_mp(self.loans)

    def set_total_notional(self):
        #TODO: loan payment. and recalculate the total notional. use loan.pay_interest
        self.total_notional = total_notional(self.loans)

