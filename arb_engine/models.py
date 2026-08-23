from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

def now(): return datetime.now(timezone.utc)
class Side(str, Enum): BUY='buy'; SELL='sell'
@dataclass(frozen=True)
class Quote:
    venue:str; symbol:str; bid:float; ask:float; bid_size:float; ask_size:float; fee_bps:float; gas_usd:float; timestamp:datetime
    @property
    def age_ms(self): return max(0,(now()-self.timestamp).total_seconds()*1000)
@dataclass(frozen=True)
class Opportunity:
    symbol:str; buy_venue:str; sell_venue:str; buy_price:float; sell_price:float; quantity:float; gross_profit_usd:float; fees_usd:float; gas_usd:float; slippage_usd:float; net_profit_usd:float
    @property
    def edge_bps(self): return self.net_profit_usd/(self.buy_price*self.quantity)*10000 if self.quantity else 0
@dataclass
class ExecutionResult:
    venue:str; side:Side; symbol:str; quantity:float; price:float; fees_usd:float; message:str
@dataclass
class Portfolio:
    pnl:float=0; daily_loss:float=0; open_trades:int=0
