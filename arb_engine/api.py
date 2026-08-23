import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .app import LiveDataEngine, load_config

config = load_config()
engine = LiveDataEngine(config)
app = FastAPI(title="KYW-BOT Arbitrage Monitor", version="0.2.0")


@app.get("/api/health")
async def health():
    return {
        "ok": True,
        "mode": config.get("mode"),
        "execution": config.get("execution", {}),
    }


@app.get("/api/snapshot")
async def snapshot():
    if not engine.last["quotes"]:
        await engine.cycle()
    return engine.last


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return HTMLResponse("""
<!doctype html>
<html>
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>KYW-BOT Live Monitor</title>
<style>
body{font-family:system-ui,sans-serif;max-width:1200px;margin:30px auto;padding:0 18px;background:#0d1117;color:#e6edf3}
.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:16px;margin:12px 0}
table{width:100%;border-collapse:collapse}th,td{padding:8px;border-bottom:1px solid #30363d;text-align:left}
.badge{padding:4px 8px;border-radius:8px;background:#21262d}small{color:#8b949e}
</style></head>
<body>
<h1>KYW-BOT</h1>
<p><span class="badge">LIVE MARKET DATA</span> <span class="badge">ORDER EXECUTION DISABLED</span></p>
<div id="app">Loading…</div>
<script>
async function refresh(){
 const r=await fetch('/api/snapshot'); const d=await r.json();
 let html='<div class="card"><b>RPC</b><table><tr><th>Chain</th><th>Status</th><th>Block</th></tr>';
 for(const [k,v] of Object.entries(d.rpc||{})) html+=`<tr><td>${k}</td><td>${v.ok?'OK':'ERROR'}</td><td>${v.block??v.error??''}</td></tr>`;
 html+='</table></div><div class="card"><b>Top opportunities</b><table><tr><th>Buy</th><th>Sell</th><th>Qty</th><th>Net USD</th><th>Edge bps</th></tr>';
 for(const o of d.opportunities||[]) html+=`<tr><td>${o.buy_venue}</td><td>${o.sell_venue}</td><td>${o.quantity.toFixed(6)}</td><td>${o.net_profit_usd.toFixed(4)}</td><td>${o.edge_bps.toFixed(2)}</td></tr>`;
 html+='</table></div><div class="card"><b>Quotes</b><table><tr><th>Venue</th><th>Bid</th><th>Ask</th><th>Age ms</th></tr>';
 for(const q of d.quotes||[]) html+=`<tr><td>${q.venue}</td><td>${q.bid}</td><td>${q.ask}</td><td>${q.age_ms.toFixed(0)}</td></tr>`;
 html+='</table></div>'; document.getElementById('app').innerHTML=html;
}
refresh(); setInterval(refresh,5000);
</script></body></html>
""")
