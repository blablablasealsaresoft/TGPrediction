# 🚀 Ubuntu Deployment Guide

## **Quick Deploy to Ubuntu Server**

### **1. Upload Files to Ubuntu**

```bash
# On your local machine (Windows), upload to Ubuntu
scp -r C:\Users\ckthe\sol\TGbot user@your-ubuntu-server:/home/user/

# OR use git (recommended)
cd C:\Users\ckthe\sol\TGbot
git add .
git commit -m "Production ready"
git push

# Then on Ubuntu:
ssh user@your-ubuntu-server
cd ~
git clone your-repo-url TGbot
cd TGbot
```

### **2. Install Dependencies on Ubuntu**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12+ (if needed)
sudo apt install python3.12 python3.12-venv python3-pip -y

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt
```

### **3. Setup Environment**

```bash
# Copy the production template
cp ENV_PRODUCTION_READY.txt .env

# Edit with nano or vim
nano .env

# Fill in:
# - ADMIN_CHAT_ID (get from @userinfobot)
# - WALLET_PRIVATE_KEY (your bot wallet)

# Fix .env formatting (removes any Windows line endings)
perl -0pi -e 's/\r//g' .env
perl -0pi -e 's/^\h+//mg' .env
```

### **4. Fix Telegram Conflicts**

```bash
# Make script executable
chmod +x scripts/fix_telegram_conflict.py

# Run the conflict fixer
python scripts/fix_telegram_conflict.py

# Wait 10 seconds
sleep 10
```

### **5. Test Run (Read-Only Mode)**

```bash
# Make sure you're in the venv
source .venv/bin/activate

# Load environment variables
set -a
source .env
set +a

# Test run (read-only, safe)
python scripts/run_bot.py --network mainnet
```

### **6. Setup as System Service (Production)**

Create systemd service file:

```bash
sudo nano /etc/systemd/system/trading-bot.service
```

Paste this:

```ini
[Unit]
Description=Solana Revolutionary Trading Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/TGbot
Environment="PATH=/home/your-username/TGbot/.venv/bin"
EnvironmentFile=/home/your-username/TGbot/.env
ExecStart=/home/your-username/TGbot/.venv/bin/python scripts/run_bot.py --network mainnet
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable on boot
sudo systemctl enable trading-bot

# Start the service
sudo systemctl start trading-bot

# Check status
sudo systemctl status trading-bot

# View logs
sudo journalctl -u trading-bot -f
```

### **7. Firewall Setup**

```bash
# Allow health check port
sudo ufw allow 8080/tcp

# Allow SSH (if not already)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

### **8. Monitor & Manage**

```bash
# View logs
sudo journalctl -u trading-bot -f

# Restart bot
sudo systemctl restart trading-bot

# Stop bot
sudo systemctl stop trading-bot

# Check bot health
curl http://localhost:8080/health

# View recent logs
tail -f logs/trading_bot.log
```

### **9. Going Live (Enable Trading)**

```bash
# Edit .env
nano .env

# Change:
ALLOW_BROADCAST=true

# Restart
sudo systemctl restart trading-bot

# Now all trades require confirm token:
# /buy TOKEN 1.0 confirm=lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A
```

### **10. Security Hardening**

```bash
# Secure .env file
chmod 600 .env

# Restrict access to bot directory
chmod 700 ~/TGbot

# Setup automatic updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure --priority=low unattended-upgrades

# Install fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## **Quick Reference Commands**

```bash
# Start bot manually
cd ~/TGbot
source .venv/bin/activate
set -a; source .env; set +a
python scripts/run_bot.py --network mainnet

# View service logs
sudo journalctl -u trading-bot -n 100 --no-pager

# Restart service
sudo systemctl restart trading-bot

# Update bot
cd ~/TGbot
git pull
source .venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart trading-bot

# Backup database
cp trading_bot.db "trading_bot.db.backup.$(date +%Y%m%d_%H%M%S)"
```

---

## **Troubleshooting**

### **Telegram Conflict Error**
```bash
# Run conflict fixer
python scripts/fix_telegram_conflict.py

# Wait 30 seconds
sleep 30

# Restart
sudo systemctl restart trading-bot
```

### **Permission Errors**
```bash
# Fix ownership
sudo chown -R your-username:your-username ~/TGbot

# Fix permissions
chmod 600 .env
chmod +x scripts/*.py
```

### **Database Lock**
```bash
# Stop bot
sudo systemctl stop trading-bot

# Wait
sleep 5

# Start
sudo systemctl start trading-bot
```

---

## **Your Generated Tokens**

```env
CONFIRM_TOKEN=lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A
WALLET_ENCRYPTION_KEY=i6RtLA9zCQ7vtNwOdej8eekndp7AKKJclOzYeBEaDJY
```

**REMEMBER:** Change these after testing! Generate new ones with:

```bash
python -c "import secrets, string; alphabet = string.ascii_letters + string.digits; print('CONFIRM_TOKEN=' + ''.join(secrets.choice(alphabet) for _ in range(32))); print('WALLET_ENCRYPTION_KEY=' + secrets.token_urlsafe(32))"
```

---

## **Production Checklist**

- [ ] Ubuntu server setup complete
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] ADMIN_CHAT_ID filled in
- [ ] WALLET_PRIVATE_KEY filled in
- [ ] Telegram conflicts resolved
- [ ] Bot tested in read-only mode
- [ ] Systemd service created
- [ ] Firewall configured
- [ ] Logs monitoring working
- [ ] Health check endpoint responding
- [ ] Database backups setup
- [ ] Security hardening complete
- [ ] Ready to set ALLOW_BROADCAST=true
- [ ] Confirm token tested

---

**You're ready to rock! 🤘**

