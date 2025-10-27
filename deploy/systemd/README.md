# Systemd Deployment Guide

1. **Create dedicated user**
   ```bash
   sudo useradd --system --home /opt/trading-bot --shell /usr/sbin/nologin trader
   sudo mkdir -p /opt/trading-bot
   sudo chown trader:trader /opt/trading-bot
   ```

2. **Deploy code**
   ```bash
   sudo rsync -a --delete {{REPO_ROOT}}/ /opt/trading-bot/
   sudo chown -R trader:trader /opt/trading-bot
   ```

3. **Install dependencies**
   ```bash
   cd /opt/trading-bot
   sudo -u trader python3 -m venv venv
   sudo -u trader ./venv/bin/pip install --upgrade pip
   sudo -u trader ./venv/bin/pip install -r requirements/dev.lock
   ```

4. **Configure secrets**
   ```bash
   sudo cp /opt/trading-bot/ENV_CONFIGURATION.txt /opt/trading-bot/.env
   sudo chown trader:trader /opt/trading-bot/.env
   sudo chmod 600 /opt/trading-bot/.env
   # Edit .env and populate all required variables.
   ```

5. **Install service**
   ```bash
   sudo cp deploy/systemd/trading-bot.service /etc/systemd/system/trading-bot.service
   sudo sed -i "s#{{REPO_ROOT}}#/opt/trading-bot#g" /etc/systemd/system/trading-bot.service
   sudo systemctl daemon-reload
   sudo systemctl enable trading-bot
   sudo systemctl start trading-bot
   ```

6. **Verify**
   ```bash
   sudo systemctl status trading-bot
   sudo journalctl -u trading-bot -f
   ```
