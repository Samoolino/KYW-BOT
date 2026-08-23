# KYW-BOT

Non-custodial arbitrage engine with live public market-data ingestion.

## Current state

- `mode: live-data` is enabled in `config.yaml`.
- CCXT provides the unified CEX market-data layer. CCXT currently documents 100+ supported crypto exchanges and a common API shape for markets, tickers, order books, balances and orders. Public market-data methods do not require account credentials. citeturn0search8turn0search16
- A configurable 0x DEX aggregation quote adapter is included for read-only pricing. 0x v2 uses an API key and supports EVM chains through its unified API. citeturn1search0turn1search3
- EVM JSON-RPC health checks are included. The Alchemy endpoint shown in the supplied screenshot matches the documented `eth_blockNumber` POST pattern. citeturn0search0
- A local FastAPI dashboard exposes quotes, opportunities and RPC health.
- **Order execution remains disabled.** No private keys, seed phrases or withdrawal credentials belong in this repository.

## Why CCXT?

Yes: CCXT is the recommended integration layer for a large CEX set. It gives the engine one normalized interface while retaining exchange-specific APIs as a fallback when a venue does not expose a required unified method. CCXT's exchange list changes over time, so the engine validates configured IDs against the installed package at runtime. citeturn0search16turn0search11

For higher-frequency WebSocket market data, CCXT Pro is the separate streaming package. citeturn0search19

## Run live market data

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill RPC URLs locally; do not commit .env
python -m arb_engine
```

Dashboard:

```bash
uvicorn arb_engine.api:app --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000` locally.

## Secrets

The RPC URL visible in the supplied screenshot contains an Alchemy API key. Treat that key as exposed: revoke/rotate it if it is active. The repository only contains placeholders; the real value must be supplied through local secret storage/environment variables.

Never commit:

- wallet seed phrases
- private keys
- CEX API secrets
- DEX API keys
- `.env`

## Execution boundary

The next production layer should be a separately audited execution/signing service. The market-data/strategy process must not receive raw private keys. Keep execution disabled until the complete system has been independently tested, reviewed, and authorized by the account owner.
