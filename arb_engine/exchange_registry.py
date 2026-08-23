"""CCXT venue registry.

CCXT provides a unified interface to 100+ crypto/prediction-market venues.
Only the exchanges listed in config.yaml are instantiated by the app.
"""

DEFAULT_CEXES = [
    "binance", "bybit", "okx", "kraken", "coinbase", "kucoin", "gateio",
    "mexc", "bitget", "htx", "bitfinex", "bitstamp", "gemini", "cryptocom",
    "bitmart", "coinex", "whitebit", "poloniex", "woo", "backpack",
    "hyperliquid", "bingx", "bitmex", "deribit", "phemex", "lbank",
    "bitrue", "digifinex", "coinw", "xt", "ascendex", "bitrget",
]


def supported_exchange_ids(ccxt_module):
    return sorted(getattr(ccxt_module, "exchanges", []))
