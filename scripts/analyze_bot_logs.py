"""
Analyze bot logs to show activity
"""

def analyze_logs():
    try:
        with open('logs/trading_bot.log', 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except:
        print("❌ Could not read log file")
        return
    
    print(f"\n📊 BOT LOG ANALYSIS")
    print("="*70)
    print(f"Total log lines: {len(lines)}\n")
    
    # Count different activities
    sniper_checks = [l for l in lines if 'Checking Birdeye' in l or 'Checking DexScreener' in l]
    wallet_scans = [l for l in lines if 'Scanning' in l and 'tracked wallets' in l]
    wallet_loads = [l for l in lines if 'Loading' in l and 'tracked wallets' in l]
    trades = [l for l in lines if 'EXECUTED' in l or 'Trade executed' in l]
    errors = [l for l in lines if ' ERROR ' in l]
    conflicts = [l for l in lines if '409 Conflict' in l]
    rate_limits = [l for l in lines if '429 Too Many' in l]
    
    print(f"🎯 SNIPER CHECKS: {len(sniper_checks)}")
    if sniper_checks:
        print(f"  Every ~10 seconds")
        print(f"  Last check: {sniper_checks[-1].split('INFO - ')[-1].strip()}")
    
    print(f"\n👛 WALLET SCANNING: {len(wallet_scans)} scans")
    if wallet_scans:
        for scan in wallet_scans[-3:]:
            print(f"  {scan.split('INFO - ')[-1].strip()}")
    
    print(f"\n📦 WALLET LOADING: {len(wallet_loads)} load operations")
    if wallet_loads:
        for load in wallet_loads[-2:]:
            print(f"  {load.split('INFO - ')[-1].strip()}")
    
    print(f"\n💰 TRADES EXECUTED: {len(trades)}")
    if trades:
        for trade in trades:
            print(f"  {trade.strip()}")
    else:
        print(f"  No trades yet (waiting for opportunities)")
    
    print(f"\n❌ ERRORS: {len(errors)}")
    if errors:
        unique_errors = {}
        for err in errors:
            msg = err.split(' - ERROR - ')[-1].strip()[:60]
            unique_errors[msg] = unique_errors.get(msg, 0) + 1
        
        for err, count in list(unique_errors.items())[:5]:
            print(f"  ({count}x) {err}")
    
    print(f"\n⚠️ TELEGRAM CONFLICTS: {len(conflicts)}")
    if conflicts:
        print(f"  This means another bot instance is trying to connect")
        print(f"  Should stop after a few attempts")
    
    print(f"\n🔥 RATE LIMITS: {len(rate_limits)}")
    if rate_limits:
        print(f"  Helius API hitting rate limit")
        print(f"  Bot will slow down automatically")
    
    # Check what's currently happening
    print(f"\n📈 CURRENT ACTIVITY (Last 10 lines):")
    print("-"*70)
    for line in lines[-10:]:
        if 'INFO - ' in line:
            time_part = line.split(' - ')[0]
            msg_part = line.split(' - INFO - ')[-1].strip()
            print(f"  [{time_part.split()[1]}] {msg_part[:60]}")
    
    print("="*70)
    
    # Summary
    print(f"\n✅ BOT IS:")
    print(f"  {'✅' if sniper_checks else '❌'} Monitoring for new tokens (Birdeye + DexScreener)")
    print(f"  {'✅' if wallet_scans else '❌'} Scanning wallets for copy trades")
    print(f"  {'⚠️' if conflicts else '✅'} Telegram connection ({'conflicts detected' if conflicts else 'OK'})")
    print(f"  {'⏳' if not trades else '✅'} Waiting for trade opportunities")

if __name__ == "__main__":
    analyze_logs()

