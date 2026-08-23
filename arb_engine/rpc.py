"""Read-only JSON-RPC health checks.

The screenshot supplied an Alchemy Ethereum endpoint. The endpoint shape is
supported here through ETH_RPC_URL; the API key must be supplied by the user
via a local secret store/environment and is never committed to Git.
"""

import httpx


async def eth_block_number(rpc_url: str):
    if not rpc_url:
        return {"ok": False, "error": "RPC URL not configured"}
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(rpc_url, json=payload)
            response.raise_for_status()
            data = response.json()
        result = data.get("result")
        if not result:
            return {"ok": False, "error": str(data)}
        return {"ok": True, "block": int(result, 16), "hex": result}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
