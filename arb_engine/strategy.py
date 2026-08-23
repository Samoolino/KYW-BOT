from itertools import permutations
from .models import Opportunity
class Detector:
    def __init__(self,cfg): self.cfg=cfg
    def find(self,quotes,notional):
        out=[]
        for b,s in permutations(quotes,2):
            if b.ask>=s.bid or b.age_ms>self.cfg['max_quote_age_ms'] or s.age_ms>self.cfg['max_quote_age_ms']: continue
            q=min(notional/b.ask,b.ask_size,s.bid_size)
            gross=(s.bid-b.ask)*q
            fees=b.ask*q*b.fee_bps/10000+s.bid*q*s.fee_bps/10000
            gas=b.gas_usd+s.gas_usd
            slip=b.ask*q*min(self.cfg['max_slippage_bps'],25)/10000
            net=gross-fees-gas-slip
            if net>=self.cfg['min_net_profit_usd']:
                out.append(Opportunity(b.symbol,b.venue,s.venue,b.ask,s.bid,q,gross,fees,gas,slip,net))
        return sorted(out,key=lambda x:x.net_profit_usd,reverse=True)
