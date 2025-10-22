"""
Real-time log viewer with filtering options
"""

import sys
import time
from datetime import datetime

def view_logs(lines=50, follow=False, filter_text=None):
    """
    View bot logs
    
    Args:
        lines: Number of lines to show
        follow: If True, continuously tail the log file
        filter_text: Only show lines containing this text
    """
    
    log_file = 'logs/trading_bot.log'
    
    print("="*70)
    print(f"TRADING BOT LOGS (Last {lines} lines)")
    if filter_text:
        print(f"Filter: '{filter_text}'")
    print("="*70)
    print()
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            # Read all lines
            all_lines = f.readlines()
            
            # Filter if needed
            if filter_text:
                all_lines = [line for line in all_lines if filter_text.lower() in line.lower()]
            
            # Get last N lines
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            # Display
            for line in recent_lines:
                print(line.rstrip())
            
            print()
            print("="*70)
            print(f"Showing {len(recent_lines)} lines")
            
            if follow:
                print("Following log file (Ctrl+C to exit)...")
                print("="*70)
                
                # Follow mode
                f.seek(0, 2)  # Go to end of file
                while True:
                    line = f.readline()
                    if line:
                        if not filter_text or filter_text.lower() in line.lower():
                            print(line.rstrip())
                    else:
                        time.sleep(0.5)
    
    except FileNotFoundError:
        print(f"[ERROR] Log file not found: {log_file}")
        print(f"[INFO] The bot may not be writing logs yet")
    except KeyboardInterrupt:
        print("\n[STOPPED] Log viewer stopped")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='View trading bot logs')
    parser.add_argument('-n', '--lines', type=int, default=50, help='Number of lines to show')
    parser.add_argument('-f', '--follow', action='store_true', help='Follow log file (like tail -f)')
    parser.add_argument('--filter', type=str, help='Filter lines containing text')
    parser.add_argument('--sniper', action='store_true', help='Show only sniper activity')
    parser.add_argument('--trades', action='store_true', help='Show only trade activity')
    parser.add_argument('--errors', action='store_true', help='Show only errors')
    
    args = parser.parse_args()
    
    # Apply preset filters
    filter_text = args.filter
    if args.sniper:
        filter_text = 'sniper'
    elif args.trades:
        filter_text = 'trade'
    elif args.errors:
        filter_text = 'ERROR'
    
    view_logs(args.lines, args.follow, filter_text)

