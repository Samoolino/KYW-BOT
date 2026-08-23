"""Read-only DEX aggregation quotes through 0x Swap API v2.

The adapter only requests indicative/firm quote data; it never submits the
returned transaction. API credentials are read from the environment.
"""

import os
import httpx


class ZeroXQuoteClient:
    def __init__(self, api_key=None, base_url="https://api.0x.org"):
        self.api_key = api_key or os.getenv("ZEROEX_API_KEY")
        self.base_url = base_url.rstrip("/")

    async def price(self, chain_id: int, sell_token: str, buy_token: str,
                    sell_amount_base_units: int, taker: str):
        if not self.api_key:
            raise RuntimeError("ZEROEX_API_KEY is not configured")
        params = {
            "chainId": str(chain_id),
            "sellToken": sell_token,
            "buyToken": buy_token,
            "sellAmount": str(sell_amount_base_units),
            "taker": taker,
        }
        headers = {"0x-api-key": self.api_key, "0x-version": "v2"}
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(
                f"{self.base_url}/swap/allowance-holder/price",
                params=params,
                headers=headers,
            )
            r.raise_for_status()
            return r.json()
