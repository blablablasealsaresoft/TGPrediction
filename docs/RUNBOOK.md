# TGbot Runbook

## Start / stop
- **Dev/Test (read-only devnet)**  
  `python scripts/run_bot.py --network devnet --no-auto-trade --read-only`
- **Production (systemd)**  
  ```bash
  sudo systemctl start trading-bot
  sudo systemctl status trading-bot
  ```
  Stop with `sudo systemctl stop trading-bot`.
- **Docker compose**  
  `docker-compose up -d` (stop with `docker-compose down`).

## Logs & metrics
- Structured logs live in `logs/trading_bot.jsonl` (JSON lines, rotated daily, 7-day retention).  
  Tail locally: `tail -f logs/trading_bot.jsonl`.
- When running under systemd: `sudo journalctl -u trading-bot -f`.
- Readiness & metrics (always bound to `127.0.0.1:8080`):  
  - `curl -s http://127.0.0.1:8080/live`  
  - `curl -s http://127.0.0.1:8080/ready`  
  - `curl -s http://127.0.0.1:8080/metrics` (only if `PROMETHEUS_ENABLED=true`).

## Health check
- Run before every deployment or restart:
  ```bash
  ./scripts/health_check.py --network mainnet
  ```
- Fails if:
  - DB not reachable or schema missing.
  - Solana RPC mismatches `SOLANA_NETWORK`.
  - Telegram token invalid.
  - Disk free <1 GB or system clock drift >2 s.

## Broadcast guardrails
- Production broadcasts require **all**:
  1. `ENV=prod`
  2. `ALLOW_BROADCAST=true`
  3. `CONFIRM_TOKEN` present in the environment.
  4. Callers provide `confirm_token` to `src/ops/broadcast.send()`.
- Without the confirm token, every trade path (manual, sniper, copy, automation) is blocked at the broadcast layer. Use read-only mode (`--read-only` or `READ_ONLY_MODE=true`) for audits.

## Common issues
| Symptom | Resolution |
| ------- | ---------- |
| `Environment validation failed` | Compare `.env` to `importantdocs/ENVIRONMENT_VARIABLES.md`; fill every required variable and ensure numeric/boolean types are correct. |
| Readiness probe returns 503 | Run `scripts/health_check.py --json` for detailed failures (RPC, DB, Telegram, disk, clock). |
| Broadcast denied (prod) | Set `ALLOW_BROADCAST=true` and provide the `confirm_token` argument that matches `CONFIRM_TOKEN`. |
| Telegram commands blocked | Ensure `ADMIN_CHAT_ID` is set and health check passes; invalid tokens cause health check failure. |

## Key rotations & restores
- **Wallet encryption key**: run `scripts/rotate_wallet_key.py --generate-new-key`, back up securely, update secret manager, then restart the service.
- **Database restore**: stop the bot, restore the latest backup (`trading_bot.db` / managed DB snapshot), run `scripts/health_check.py`, then restart.
- **Log retention**: logrotate config (`deploy/logrotate/trading-bot`) keeps 7 compressed daily copies. Deploy via `sudo cp deploy/logrotate/trading-bot /etc/logrotate.d/trading-bot`.
