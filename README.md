# KYW-BOT

Non-custodial arbitrage engine.

Default mode is paper simulation. No private keys, seed phrases, withdrawals, or live order execution are included.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m arb_engine
```

Windows: `.venv\Scripts\Activate.ps1`

See `config.yaml` for strategy/risk limits.
