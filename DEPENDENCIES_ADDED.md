# Web API Dependencies Added

The following dependencies have been added to `requirements/base.in` for the Web API:

```
aiohttp-cors==0.7.0    # CORS support for Web API
python-jose==3.3.0     # JWT token handling
passlib==1.7.4         # Password hashing for authentication
```

## Next Steps

You need to regenerate the lock file and rebuild the Docker image:

### Option 1: Rebuild Docker Image (Recommended)

The simplest approach - just rebuild the trading-bot image:

```bash
docker-compose -f docker-compose.prod.yml build trading-bot
docker-compose -f docker-compose.prod.yml up -d trading-bot
```

### Option 2: Regenerate Lock File (For Development)

If you want to update the lock file:

```bash
# Install pip-tools if not already installed
pip install pip-tools

# Regenerate the lock file
pip-compile requirements/base.in -o requirements/dev.lock

# Then rebuild
docker-compose -f docker-compose.prod.yml build trading-bot
docker-compose -f docker-compose.prod.yml up -d trading-bot
```

### Option 3: Quick Fix (Install in Running Container)

Temporary fix for testing:

```bash
docker exec trading-bot-app pip install aiohttp-cors python-jose passlib
docker-compose -f docker-compose.prod.yml restart trading-bot
```

## Verification

After rebuilding, verify the bot starts:

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs -f trading-bot

# Should see:
# ✅ Web API server configured
# ✅ Web API modules injected
# ✅ Web Dashboard API
# 🌐 Web API server started on port 8080
```

Test the API:

```bash
# PowerShell
Invoke-WebRequest -Uri http://localhost:8080/health -UseBasicParsing | Select-Object -ExpandProperty Content

# Or use curl.exe (if available)
curl.exe http://localhost:8080/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "2025-11-12T14:00:00.000Z"}
```

