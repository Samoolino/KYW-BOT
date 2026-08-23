import asyncio
import logging
import os
from pathlib import Path

import yaml

from .ccxt_adapter import collect_quotes
from .models import Portfolio
from .risk import Risk
from .rpc import eth_block_number
from .strategy import Detector

log = logging.getLogger(__name__)


def load_config(path="config.yaml"):
    raw = Path(path).read_text(encoding="utf-8")
    for key, value in os.environ.items():
        raw = raw.replace("${" + key + "}", value)
    return yaml.safe_load(raw)


class LiveDataEngine:
    """Live public market-data engine.

    It computes opportunities from live CEX quotes but deliberately does not
    submit orders. This keeps the live-data pipeline separate from any future
    user-controlled signing/execution boundary.
    """

    def __init__(self, config):
        self.c = config
        self.symbol = config["symbol"]
        self.portfolio = Portfolio()
        self.detector = Detector(config["strategy"])
        self.risk = Risk(config["risk"])
        self.last = {"quotes": [], "opportunities": [], "rpc": {}}

    async def cycle(self):
        exchange_ids = self.c["cex"]["enabled"]
        quotes = await collect_quotes(exchange_ids, self.symbol)
        opportunities = self.detector.find(
            quotes,
            self.c["strategy"]["trade_notional_usd"],
        )

        rpc = {}
        for chain, url in self.c.get("rpc", {}).items():
            rpc[chain] = await eth_block_number(url)

        self.last = {
            "quotes": [
                {
                    "venue": q.venue,
                    "symbol": q.symbol,
                    "bid": q.bid,
                    "ask": q.ask,
                    "age_ms": q.age_ms,
                }
                for q in quotes
            ],
            "opportunities": [
                {
                    "buy_venue": o.buy_venue,
                    "sell_venue": o.sell_venue,
                    "quantity": o.quantity,
                    "gross_profit_usd": o.gross_profit_usd,
                    "fees_usd": o.fees_usd,
                    "gas_usd": o.gas_usd,
                    "net_profit_usd": o.net_profit_usd,
                    "edge_bps": o.edge_bps,
                }
                for o in opportunities[:20]
            ],
            "rpc": rpc,
            "execution": self.c.get("execution", {}),
        }

        if opportunities:
            best = opportunities[0]
            ok, reason = self.risk.approve(best, self.portfolio)
            log.info(
                "LIVE DATA opportunity %s -> %s net=$%.4f edge=%.2fbps risk=%s (%s)",
                best.buy_venue, best.sell_venue, best.net_profit_usd,
                best.edge_bps, ok, reason,
            )
        else:
            log.info("No executable arbitrage edge detected")

        return self.last

    async def run(self):
        log.info("starting live-data arbitrage engine; order execution is disabled")
        while True:
            try:
                await self.cycle()
            except Exception:
                log.exception("live-data cycle failed")
            await asyncio.sleep(self.c["poll_interval_seconds"])


async def run():
    config = load_config()
    if config.get("mode") != "live-data":
        raise RuntimeError("Set mode: live-data for the live market-data engine")
    await LiveDataEngine(config).run()
