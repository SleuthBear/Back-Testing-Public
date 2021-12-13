import trendlines

class QAV():

    def __init__(self, tkiv1 = True, tkiv2 = True, pricebook = True, pricebook2 = True,
          cfshare = True, yieldpe = True, yieldbd = True, recordpe = True,
          upturn = True, upturn = True, equity = True, threepointbuy = True,
          pricetarget = True, epsgrowth = True, fciv2 = True):

        self.use_tkiv1 = tkiv1
        self.use_tkiv2 = tkiv2
        self.use_pricebook = pricebook
        self.use_pricebook2 = pricebook2
        self.use_cfshare = cfshare
        self.use_yieldpe = yieldpe
        self.useyeildbd = yieldbd
        self.use_recordpe = recordpe
        self.use_upturn = upturn
        self.use_equity = equity
        self.use_threepointbuy = threepointbuy
        self.use_pricetarget = pricetarget
        self.use_epsgrowth = epsgrowth
        self.use_fciv2 = fciv2
        
    def record_low_pe(self, d):
        i = -10
        count = 1
        curr_EPS = d.EarningsperShare[1]
        NEW_PE = d.PE[1]
        # Loop over all the data backwards until the 6 most recent PEs are 
        # found or until we find a PE smaller than our current  number
        while count < PE_COUNT:
            #Step back 6 months
            try:
                if d.EarningsperShare[i] and d.EarningsperShare[i] != curr_EPS:
                    count += 1
                    curr_EPS = d.EarningsperShare[i]
                    NEW_PE = ((d.close[i])/(curr_EPS))
                # find if this PE < current PE
                if NEW_PE < d.PE[1] and NEW_PE > 0:
                    return 0
                # If there is an index error, we msut be at the end of the
                # dataset without finding a smaller PE, so we accept our PE
                # as the smallest
            except IndexError:
                return 1
            i -= 10
            
        # If we haven't found a smaller PE in the 6 most recent PEs
        # then we must have the smallest from the last 6.
        return 1

    def old_upturn(self, d):
        # We track recent periods by equity
        curr_equity = d.Equity[1]
        i = 0
        while d.Equity[-i] == curr_equity or not d.Equity[-i]:
            i += 1
        return trendlines.three_point_TL(d, i)) > 0
    
    def cons_incr_equity(self, d):
        i = -10
        count = 1
        curr_equity = d.Equity[1]
        # Loop over all the data backwards until the 6 most recent PEs are 
        # found or until we find a PE smaller than our current  number
        while count < EQUITY_COUNT:
            #Step back 6 months
            try:
                if d.Equity[i] > curr_equity:
                    return 0
                if d.Equity[i] and d.Equity[i] != curr_equity:
                    count += 1
                    curr_equity = d.Equity[i]
            except IndexError:
                return 1
            i -= 1       
        return 1


    def calculate_QAV(self, d):
        score = 0
        num_items = 0
        
        # Price<=TKIV1?
        if self.use_tkiv1:
            TKIV1 = d.EarningsperShare[1]/0.195
            if d.close[1] <= TKIV1:
                score += 1
            num_items += 1
        
        # Price<= TKIV2?
        if self.use_tkiv2 and d.EPSfrcst[1]:
            TKIV2 = d.EPSfrcst[1]/0.061
            if d.close <= TKIV2:
                score += 1
            num_items += 1
            
        # Price<Book?
        if self.use_pricebook:
            if d.close[1] < d.BookValue[1]:
                score += 1
            num_items += 1        

        # Price <= book+30%?
        if self.use_pricebook2:
            if d.close[1] < d.BookValue[1]*1.3:
                score += 1
            num_items += 1

        
        # Record low of last 6 PEs?
        if self.use_recordpe:
            if self.record_low_PE():
                score += 1
            num_items += 1

        
        # Consistantly Increasing Equity?
        if self.use_equity:
            if self.cons_incr_equity():
                score += 1
            num_items += 1

        # Yield - PE > 1?
        if self.use_yieldpe:
            if d.NetYield[1]:
                if d.NetYield[1] - d.PE[1] > 1:
                    score += 1
                    num_items += 1

        # Yield > bank debt?
        if self.use_yieldbd:
            if d.NetYield[1]:
                if d.NetYield[1] > BANK_DEBT:
                    score += 1
            num_items += 1
        
        # Is FCIV>2*share price? (called FCIV but is actually TKIV2)
        if self.use_FCIV2 and d.EPSfrcst[1]:
            TKIV2 = d.EPSfrcst[1]/0.061
            if TKIV2 > d.close[1]*2:
                score += 1
            num_items += 1

        # CF/Share<=7 [ASK]
        if self.use_cfshare and d.OperatingCashFlowPerShare[1]:
            if (d.close[1]/(d.OperatingCashFlowPerShare[1])) <= 7:
                score += 2  
            num_items += 1
            
        # Is price below 1 day price target? (instead of SDIV) [ASK]
        if self.use_pricetarget and d.PriceTarget[1]:
            if d.close[1] < d.PriceTarget[1]:
                score += 1
            num_items += 1
        
        # 3-point-uptrend?
        # Because we won't buy unless it is a 3-point uptrend anyway, we can
        # simply assume this is true to avoid extra calculations
        if self.use_threepointbuy:
            score += 1
            num_items += 1
            
        # New 3-point upturn?
        if self.use_upturn and self.use_threepointbuy:
            if not self.old_upturn():
                score += 1
                #print("Recent Upturn PASSED")
            num_items += 1
                
        # Growth/PE > 1.5
        if (self.use_EPSgrowth and d.FEPS[1] and d.PE[1] and 
            d.EarningsperShare[1]):
            EPSgrowth = ((d.FEPS[1] - d.EarningsperShare[1])
                         / d.EarningsperShare[1])
            if (EPSgrowth*100)/d.PE[1] > 1.5:
                score += 1
                #print("Growth/PE > 1.5 PASSED")
            num_items += 1

        quality = score/num_items
        return quality, quality/d.PricetoOperatingCashFlow[1]
