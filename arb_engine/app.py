import asyncio,logging,yaml
from .market import SimMarket
from .models import Portfolio,Side
from .strategy import Detector
from .risk import Risk
from .execution import PaperExecutor
log=logging.getLogger(__name__)
async def run():
    c=yaml.safe_load(open('config.yaml'))
    if c['mode']!='paper': raise RuntimeError('Only paper mode is enabled')
    symbol=f"{c['strategy']['quote_asset']}/{c['strategy']['base_asset']}"
    markets=[SimMarket(v,i*1.7) for i,v in enumerate(c['venues'])]
    d=Detector(c['strategy']); r=Risk(c['risk']); e=PaperExecutor(); p=Portfolio()
    while True:
        quotes=await asyncio.gather(*(m.quote(symbol) for m in markets))
        ops=d.find(quotes,c['strategy']['trade_notional_usd'])
        if ops:
            o=ops[0]; ok,why=r.approve(o,p)
            log.info('opportunity %s -> %s net=$%.4f edge=%.2fbps %s',o.buy_venue,o.sell_venue,o.net_profit_usd,o.edge_bps,why)
            if ok:
                r.mark(); p.open_trades+=1
                try:
                    await asyncio.gather(e.execute(o.buy_venue,Side.BUY,o.symbol,o.quantity,o.buy_price),e.execute(o.sell_venue,Side.SELL,o.symbol,o.quantity,o.sell_price))
                    p.pnl+=o.net_profit_usd
                finally: p.open_trades-=1
        await asyncio.sleep(c['poll_interval_seconds'])
