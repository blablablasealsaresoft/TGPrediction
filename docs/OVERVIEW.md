# TGbot Overview

## Repository structure
- `src/` – production code. `src/bot/main.py` wires Telegram handlers; `src/modules/` hosts AI, sniper, execution, database, wallet, and monitoring modules; `src/ops/` contains operational helpers (health probes, broadcast guardrails).
- `scripts/` – operator tooling (bot runner, health check, wallet utilities, migrations). `scripts/run_bot.py` is the canonical entrypoint.
- `importantdocs/` – authoritative documentation set (START_HERE, PRODUCTION_READINESS_REPORT, DEPLOYMENT_CHECKLIST, ENVIRONMENT_VARIABLES, LAUNCH_READY_SUMMARY).
- `requirements/`, `requirements.txt`, `vendor/` – locked dependency management via pip-tools and the vendored wheelhouse.
- `deploy/` – infra assets (systemd unit + guide, logrotate policy).
- `docs/` – user-facing references, overview, and runbooks (this directory).

## Installing dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
./scripts/install_requirements.sh
```
The helper script pins to `requirements/dev.lock` and prefers wheels under `vendor/`.

## Safe developer workflow
1. Copy `ENV_CONFIGURATION.txt` to `.env`, then generate unique credentials (see `importantdocs/ENVIRONMENT_VARIABLES.md`).
2. Run the health check without risking trades:
   ```bash
   ./scripts/health_check.py --network devnet
   ```
3. Launch the bot in **read-only devnet** to exercise Telegram flows with zero broadcast risk:
   ```bash
   python scripts/run_bot.py --network devnet --no-auto-trade --read-only
   ```
4. Inspect logs in `logs/trading_bot.jsonl` (JSON lines) or via the readiness probe at `http://127.0.0.1:8080/live`.

## Production run (guardrails baked in)
- Set `ENV=prod`, `ALLOW_AUTOTRADE=true` (only if auto-trading is desired), `ALLOW_BROADCAST=true`, and `CONFIRM_TOKEN=<unique>` in the secret store.
- Run the health check with `--network mainnet`.
- Start via systemd (preferred) or Docker compose; both routes start the readiness probe on `127.0.0.1:8080` and deny broadcasts unless the confirm token accompanies the request (see `src/ops/broadcast.py`).

## Secrets handling
- `WALLET_ENCRYPTION_KEY`, `TELEGRAM_BOT_TOKEN`, `SOLANA_RPC_URL`, `WALLET_PRIVATE_KEY`, `CONFIRM_TOKEN`, and `DATABASE_URL` are mandatory in all environments.
- Never commit `.env`, `trading_bot.db`, or `logs/` artifacts. Use Vault/SSM/KMS for production secrets as outlined in `importantdocs/ENVIRONMENT_VARIABLES.md`.
- Sample files (e.g., `ENV_CONFIGURATION.txt`) contain placeholder credentials—replace them immediately in any real deployment.

## Safe vs dangerous commands
| Command | Context | Risk |
| ------- | ------- | ---- |
| `./scripts/health_check.py --network devnet` | Configuration validation | ✅ Safe |
| `python scripts/run_bot.py --network devnet --read-only` | Dry-run Telegram flows (no trades) | ✅ Safe |
| `python scripts/run_bot.py --network mainnet` | Starts live trading if broadcast enabled | ⚠️ Dangerous |
| `pytest tests/unit` | Local unit tests (mocks) | ✅ Safe |
| `pytest tests/test_sniper_e2e.py` | Sends live Solana transactions if configured | ⚠️ Dangerous |
| `docker-compose up` | Starts bot inside container; broadcasting blocked unless confirm token supplied | ⚠️ Dangerous in prod |
