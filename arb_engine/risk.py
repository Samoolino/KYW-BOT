import time
class Risk:
    def __init__(self,cfg): self.cfg=cfg; self.last=0
    def approve(self,o,p):
        if o.buy_price*o.quantity>self.cfg['max_trade_usd']: return False,'trade limit'
        if o.gas_usd>self.cfg['max_gas_usd']: return False,'gas limit'
        if p.daily_loss>=self.cfg['max_daily_loss_usd']: return False,'daily loss limit'
        if p.open_trades>=self.cfg['max_open_trades']: return False,'open trade limit'
        if time.monotonic()-self.last<self.cfg['cooldown_seconds']: return False,'cooldown'
        return True,'approved'
    def mark(self): self.last=time.monotonic()
