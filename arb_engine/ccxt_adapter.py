"""Public market-data adapter for CCXT.

No API credentials are required for public ticker/order-book reads.
Private credentials are deliberately not loaded by this adapter.
"""

import asyncio
from datetime import datetime, timezone

import ccxt.async_support as ccxt

from .models import Quote


class CCXTMarket:
    def __init__(self, exchange_id: str, timeout_ms: int = 5000):
        if exchange_id not in ccxt.exchanges:
            raise ValueError(f"Unsupported CCXT exchange id: {exchange_id}")
        self.exchange_id = exchange_id
        cls = getattr(ccxt, exchange_id)
        self.exchange = cls({"enableRateLimit": True, "timeout": timeout_ms})

    async def quote(self, symbol: str) -> Quote:
        ticker = await self.exchange.fetch_ticker(symbol)
        bid = ticker.get("bid")
        ask = ticker.get("ask")
        if not bid or not ask:
            raise RuntimeError(f"{self.exchange_id}: ticker has no bid/ask for {symbol}")

        info = ticker.get("info") or {}
        return Quote(
            venue=self.exchange_id,
            symbol=symbol,
            bid=float(bid),
            ask=float(ask),
            bid_size=float(ticker.get("bidVolume") or 0),
            ask_size=float(ticker.get("askVolume") or 0),
            fee_bps=0.0,
            gas_usd=0.0,
            timestamp=datetime.now(timezone.utc),
        )

    async def close(self):
        await self.exchange.close()


async def collect_quotes(exchange_ids: list[str], symbol: str):
    clients = [CCXTMarket(x) for x in exchange_ids]
    try:
        results = await asyncio.gather(
            *(c.quote(symbol) for c in clients),
            return_exceptions=True,
        )
        return [r for r in results if isinstance(r, Quote)]
    finally:
        await asyncio.gather(*(c.close() for c in clients), return_exceptions=True)
