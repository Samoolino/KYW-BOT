import asyncio
import logging
import os
from pathlib import Path

import yaml

from .ccxt_adapter import collect_quotes
from .distribution import Allocation, ProfitAllocator
from .models import Portfolio
from .notifications import Notifier
from .risk import Risk
from .rpc import eth_block_number
from .session import ProfitSession
from .strategy import Detector

log = logging.getLogger(__name__)


def load_config(path="config.yaml"):
    raw = Path(path).read_text(encoding="utf-8")
    for key, value in os.environ.items():
        raw = raw.replace("${" + key + "}", value)
    return yaml.safe_load(raw)


class LiveDataEngine:
    """Live market-data engine with target-gated session accounting.

    Market data remains live, while execution stays behind its independent
    execution gate. Telegram/email are notification/control-plane services and
    are never the process that keeps the engine alive.
    """

    def __init__(self, config):
        self.c = config
        self.symbol = config["symbol"]
        self.portfolio = Portfolio()
        self.detector = Detector(config["strategy"])
        self.risk = Risk(config["risk"])
        session_cfg = config.get("session", {})
        self.session = ProfitSession(
            target_profit_usd=float(session_cfg.get("target_profit_usd", 10)),
            starter_capital_usd=float(session_cfg.get("starter_capital_usd", 100)),
        )
        harvest = config.get("harvest", {})
        allocations = [
            Allocation(
                name=a["name"],
                percent=float(a["percent"]),
                destination=a["destination"],
            )
            for a in harvest.get("allocations", [])
        ]
        self.allocator = ProfitAllocator(allocations) if allocations else None
        self.notifier = Notifier()
        self.last = {"quotes": [], "opportunities": [], "rpc": {}, "session": {}}

    def start_session(self):
        self.session.start()
        self.notifier.alert(
            "KYW-BOT session started",
            f"Target ${self.session.target_profit_usd:.2f}; starter capital ${self.session.starter_capital_usd:.2f}.",
        )

    def record_realized_profit(self, amount_usd: float):
        reached = self.session.record_profit(amount_usd)
        if reached:
            self.notifier.alert(
                "KYW-BOT target reached",
                f"Session target ${self.session.target_profit_usd:.2f} reached. New sessions require explicit restart.",
            )
        return reached

    def harvest_preview(self):
        if not self.allocator:
            return {}
        return self.allocator.allocate_profit(max(0, self.session.realized_profit_usd))

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
            "session": {
                "state": self.session.state.value,
                "target_profit_usd": self.session.target_profit_usd,
                "realized_profit_usd": self.session.realized_profit_usd,
                "target_remaining_usd": self.session.target_remaining_usd,
            },
            "harvest_preview": self.harvest_preview(),
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
        log.info("starting live-data arbitrage engine; execution remains independently gated")
        while True:
            try:
                await self.cycle()
            except Exception:
                log.exception("live-data cycle failed")
                self.notifier.alert("KYW-BOT engine error", "A market-data cycle failed; the worker will continue.")
            await asyncio.sleep(self.c["poll_interval_seconds"])


async def run():
    config = load_config()
    if config.get("mode") != "live-data":
        raise RuntimeError("Set mode: live-data for the live market-data engine")
    await LiveDataEngine(config).run()
