# Hummingbot worker

KYW-BOT uses Hummingbot as the connector/execution runtime and keeps Telegram/email outside the runtime path.

Hummingbot is open-source software and can be self-hosted. The current Hummingbot documentation recommends V2 Controllers for production-grade, modular, long-running strategies and documents Gateway separately for DEX trading.

## Runtime model

- `hummingbot` container: persistent trading worker.
- `gateway` container: DEX middleware where required.
- Vercel/frontend: dashboard and control plane only.
- Telegram: notifications and explicit session commands only.
- Email: notifications only.

The worker uses Docker `restart: unless-stopped`, so losing Telegram, email, or the dashboard does not stop the trading process.

## Session policy

A session has:

1. starter capital
2. target profit
3. explicit start
4. continuous opportunity monitoring while active
5. target-reached terminal state
6. no automatic next session

There is no mathematically guaranteed "no-loss" trading strategy. The target gate controls when a session stops; it does not remove market, liquidity, execution, counterparty, or network risk.

## Harvest allocation

The `ProfitAllocator` calculates how realized profit would be allocated among configured account labels. It does not execute withdrawals or transfer funds. Any real movement of funds must be separately authorized and implemented through the appropriate exchange/wallet controls.

Example allocation:

- API account 1: 50%
- API account 2: 30%
- reserve: 20%

The percentages must total 100%.

## Secrets

Never commit exchange API keys, Telegram tokens, SMTP passwords, wallet seed phrases, or private keys. Hummingbot's own configuration keeps credentials in its protected configuration area; keep those files out of Git.
