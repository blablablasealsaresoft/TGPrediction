"""
Enterprise-grade UI formatting for Telegram messages
Consistent, professional, and visually appealing
"""
from typing import List, Dict, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class EnterpriseUI:
    """Professional UI formatter for enterprise-grade Telegram bot"""
    
    # Visual separators
    SEPARATOR_HEAVY = "━" * 40
    SEPARATOR_LIGHT = "─" * 40
    SEPARATOR_DOT = "•" * 40
    
    # Color-coded emojis (consistent across all messages)
    ICON = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'wallet': '💰',
        'trading': '📊',
        'sniper': '🎯',
        'ai': '🧠',
        'protection': '🛡️',
        'social': '👥',
        'rewards': '🎁',
        'strategy': '📚',
        'trending': '🔥',
        'settings': '⚙️',
        'help': '❓',
        'rocket': '🚀',
        'chart': '📈',
        'medal_1': '🥇',
        'medal_2': '🥈',
        'medal_3': '🥉',
        'trophy': '🏆',
        'star': '⭐',
        'lock': '🔐',
        'key': '🔑',
        'deposit': '📥',
        'withdraw': '📤',
        'refresh': '🔄',
        'close': '❌',
        'back': '◀️',
    }
    
    @staticmethod
    def header(title: str, icon: str = '🚀') -> str:
        """Create enterprise header"""
        return f"{icon} <b>{title.upper()}</b>"
    
    @staticmethod
    def section(title: str) -> str:
        """Create section header"""
        return f"\n<b>━━━ {title} ━━━</b>"
    
    @staticmethod
    def field(label: str, value: str, mono: bool = False) -> str:
        """Create labeled field"""
        if mono:
            return f"<b>{label}:</b> <code>{value}</code>"
        return f"<b>{label}:</b> {value}"
    
    @staticmethod
    def code_block(text: str) -> str:
        """Format as code block"""
        return f"<code>{text}</code>"
    
    @staticmethod
    def bold(text: str) -> str:
        """Bold text"""
        return f"<b>{text}</b>"
    
    @staticmethod
    def mono(text: str) -> str:
        """Monospace text"""
        return f"<code>{text}</code>"
    
    @staticmethod
    def link(text: str, url: str) -> str:
        """Create link"""
        return f'<a href="{url}">{text}</a>'
    
    @staticmethod
    def separator(style: str = 'light') -> str:
        """Visual separator"""
        if style == 'heavy':
            return "\n" + EnterpriseUI.SEPARATOR_HEAVY + "\n"
        elif style == 'dot':
            return "\n" + EnterpriseUI.SEPARATOR_DOT + "\n"
        return "\n" + EnterpriseUI.SEPARATOR_LIGHT + "\n"
    
    @staticmethod
    def stat_line(label: str, value: str, emoji: str = '') -> str:
        """Format stat line"""
        emoji_part = f"{emoji} " if emoji else ""
        return f"{emoji_part}<b>{label}:</b> {value}"
    
    @staticmethod
    def wallet_address(address: str, truncate: bool = True) -> str:
        """Format wallet address"""
        if truncate and len(address) > 16:
            return f"<code>{address[:8]}...{address[-8:]}</code>"
        return f"<code>{address}</code>"
    
    @staticmethod
    def amount_sol(amount: float, show_usd: bool = False, sol_price: float = 100.0) -> str:
        """Format SOL amount"""
        if show_usd:
            usd_value = amount * sol_price
            return f"<b>{amount:.4f} SOL</b> <i>(≈${usd_value:.2f})</i>"
        return f"<b>{amount:.4f} SOL</b>"
    
    @staticmethod
    def percentage(value: float, show_sign: bool = True) -> str:
        """Format percentage"""
        sign = '+' if value > 0 and show_sign else ''
        color = '🟢' if value > 0 else '🔴' if value < 0 else '⚪'
        return f"{color} <b>{sign}{value:.2f}%</b>"
    
    @staticmethod
    def progress_bar(current: float, total: float, width: int = 10) -> str:
        """Create progress bar"""
        filled = int((current / total) * width) if total > 0 else 0
        empty = width - filled
        bar = '█' * filled + '░' * empty
        pct = (current / total) * 100 if total > 0 else 0
        return f"{bar} {pct:.1f}%"
    
    @staticmethod
    def tier_badge(tier: str) -> str:
        """Get tier emoji and formatting"""
        badges = {
            'bronze': '🥉',
            'silver': '🥈',
            'gold': '🥇',
            'platinum': '💎',
            'diamond': '💠',
            'elite': '👑'
        }
        tier_lower = tier.lower()
        emoji = badges.get(tier_lower, '🏅')
        return f"{emoji} <b>{tier.upper()}</b>"
    
    @staticmethod
    def create_button_grid(buttons: List[Dict[str, str]], cols: int = 2) -> List[List[InlineKeyboardButton]]:
        """Create grid of buttons"""
        keyboard = []
        row = []
        
        for btn in buttons:
            row.append(InlineKeyboardButton(
                btn['text'],
                callback_data=btn.get('callback'),
                url=btn.get('url')
            ))
            
            if len(row) >= cols:
                keyboard.append(row)
                row = []
        
        if row:
            keyboard.append(row)
        
        return keyboard
    
    @classmethod
    def standard_buttons(cls, include_back: bool = True, include_close: bool = True) -> List[List[InlineKeyboardButton]]:
        """Standard navigation buttons"""
        keyboard = []
        
        if include_back:
            row = [InlineKeyboardButton(f"{cls.ICON['back']} Back", callback_data="back_to_start")]
            if include_close:
                row.append(InlineKeyboardButton(f"{cls.ICON['close']} Close", callback_data="close_message"))
            keyboard.append(row)
        elif include_close:
            keyboard.append([InlineKeyboardButton(f"{cls.ICON['close']} Close", callback_data="close_message")])
        
        return keyboard


class MessageTemplates:
    """Pre-built enterprise message templates"""
    
    @staticmethod
    def welcome(user_name: str, wallet_address: str, balance: float, is_new: bool) -> tuple[str, InlineKeyboardMarkup]:
        """Enterprise welcome message"""
        ui = EnterpriseUI
        
        balance_status = f"{ui.ICON['success']} <b>New Wallet Created!</b>" if is_new else ui.field("Balance", f"{balance:.4f} SOL")
        
        message = f"""
{ui.header('SOLANA ELITE TRADING PLATFORM', ui.ICON['rocket'])}

Welcome, <b>{user_name}</b>! {ui.ICON['success']}

{ui.separator('heavy')}

{ui.section('YOUR TRADING WALLET')}
{ui.ICON['lock']} <b>Personal Address:</b>
{ui.wallet_address(wallet_address, truncate=False)}

{balance_status}

{ui.separator('light')}

{ui.section('QUICK START')}
{ui.ICON['deposit']} <b>1.</b> Fund wallet → <code>/deposit</code>
{ui.ICON['ai']} <b>2.</b> Analyze tokens → <code>/ai &lt;token&gt;</code>
{ui.ICON['trading']} <b>3.</b> Execute trades → <code>/buy</code> / <code>/sell</code>
{ui.ICON['social']} <b>4.</b> Copy elite traders → <code>/leaderboard</code>

{ui.separator('light')}

{ui.section('ELITE FEATURES')}
{ui.ICON['sniper']} Auto-Sniper: Catch new launches
{ui.ICON['ai']} AI Analysis: 6-layer safety checks
{ui.ICON['protection']} MEV Protection: Jito bundles
{ui.ICON['social']} Copy Trading: 441 elite wallets
{ui.ICON['chart']} Auto-Trading: AI-powered execution

{ui.separator('heavy')}

{ui.ICON['info']} All wallets are encrypted & secure
{ui.ICON['protection']} Every trade has anti-MEV protection
"""
        
        keyboard = [
            [
                InlineKeyboardButton(f"{ui.ICON['wallet']} My Wallet", callback_data="show_wallet"),
                InlineKeyboardButton(f"{ui.ICON['trading']} My Stats", callback_data="my_stats")
            ],
            [
                InlineKeyboardButton(f"{ui.ICON['trophy']} Leaderboard", callback_data="leaderboard"),
                InlineKeyboardButton(f"{ui.ICON['ai']} AI Analysis", callback_data="help_analysis")
            ],
            [
                InlineKeyboardButton(f"{ui.ICON['sniper']} Auto-Sniper", callback_data="sniper_info"),
                InlineKeyboardButton(f"{ui.ICON['help']} Help", callback_data="help")
            ],
            [
                InlineKeyboardButton(f"{ui.ICON['close']} Close", callback_data="close_message")
            ]
        ]
        
        return message, InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def wallet_info(wallet_address: str, balance: float, stats: Dict) -> tuple[str, InlineKeyboardMarkup]:
        """Enterprise wallet display"""
        ui = EnterpriseUI
        
        message = f"""
{ui.header('YOUR TRADING WALLET', ui.ICON['wallet'])}

{ui.separator('heavy')}

{ui.section('WALLET ADDRESS')}
{ui.wallet_address(wallet_address, truncate=False)}

{ui.separator('light')}

{ui.section('BALANCE')}
{ui.amount_sol(balance, show_usd=True)}

{ui.separator('light')}

{ui.section('PERFORMANCE (30 DAYS)')}
{ui.stat_line('Total Trades', str(stats.get('total_trades', 0)), ui.ICON['trading'])}
{ui.stat_line('Win Rate', f"{stats.get('win_rate', 0):.1f}%", ui.ICON['chart'])}
{ui.stat_line('Total P&L', f"{stats.get('total_pnl', 0):+.4f} SOL", ui.ICON['trophy'])}

{ui.separator('heavy')}

{ui.ICON['info']} <b>Security Features:</b>
• Encrypted private key storage
• Personal wallet (not shared)
• Export to Phantom/Solflare
• Full custody & control

{ui.ICON['help']} <b>Quick Actions:</b>
• <code>/deposit</code> - Fund your wallet
• <code>/balance</code> - Check balance
• <code>/export_wallet</code> - Export keys
"""
        
        keyboard = [
            [
                InlineKeyboardButton(f"{ui.ICON['deposit']} Deposit", callback_data="show_deposit"),
                InlineKeyboardButton(f"{ui.ICON['refresh']} Refresh", callback_data="refresh_wallet")
            ],
            [
                InlineKeyboardButton(f"{ui.ICON['key']} Export Keys", callback_data="export_keys_prompt"),
                InlineKeyboardButton(f"{ui.ICON['trading']} Trade History", callback_data="show_history")
            ],
            [
                InlineKeyboardButton(f"{ui.ICON['back']} Main Menu", callback_data="back_to_start")
            ]
        ]
        
        return message, InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def leaderboard(traders: List[Dict], limit: int = 10) -> tuple[str, InlineKeyboardMarkup]:
        """Enterprise leaderboard display"""
        ui = EnterpriseUI
        
        message = f"""
{ui.header('ELITE TRADERS LEADERBOARD', ui.ICON['trophy'])}

{ui.separator('heavy')}

{ui.ICON['info']} <i>Top {limit} traders ranked by performance</i>

{ui.separator('light')}
"""
        
        for i, trader in enumerate(traders[:limit], 1):
            if i == 1:
                rank = f"{ui.ICON['medal_1']}"
            elif i == 2:
                rank = f"{ui.ICON['medal_2']}"
            elif i == 3:
                rank = f"{ui.ICON['medal_3']}"
            else:
                rank = f"<b>#{i}</b>"
            
            tier_badge = ui.tier_badge(trader.get('tier', 'bronze'))
            win_rate = trader.get('win_rate', 0)
            pnl = trader.get('total_pnl', 0)
            score = trader.get('reputation_score', 0)
            
            message += f"""
{rank} <b>{trader.get('username', 'Unknown')}</b> {tier_badge}
   {ui.stat_line('Score', f"{score:.1f}/100", '📊')}
   {ui.stat_line('Win Rate', f"{win_rate:.1f}%", '🎯')}
   {ui.stat_line('Total P&L', f"{pnl:+.4f} SOL", '💰')}
   {ui.stat_line('Followers', str(trader.get('followers', 0)), '👥')}
   <code>/copy {trader.get('user_id', 0)}</code>
"""
        
        message += f"""
{ui.separator('heavy')}

{ui.ICON['info']} Tap to copy any trader above
{ui.ICON['help']} Use <code>/copy &lt;id&gt;</code> or tap buttons below
"""
        
        # Smart button layout - top 3 traders get quick buttons
        keyboard = []
        if len(traders) >= 3:
            keyboard.append([
                InlineKeyboardButton(
                    f"{ui.ICON['medal_1']} Copy #{1}",
                    callback_data=f"copy_trader_{traders[0].get('user_id', 0)}"
                ),
                InlineKeyboardButton(
                    f"{ui.ICON['medal_2']} Copy #{2}",
                    callback_data=f"copy_trader_{traders[1].get('user_id', 0)}"
                ),
            ])
        
        keyboard.extend([
            [
                InlineKeyboardButton(f"{ui.ICON['trading']} My Ranking", callback_data="my_stats"),
                InlineKeyboardButton(f"{ui.ICON['chart']} Performance", callback_data="trader_performance")
            ],
            [
                InlineKeyboardButton(f"{ui.ICON['refresh']} Refresh", callback_data="leaderboard"),
                InlineKeyboardButton(f"{ui.ICON['back']} Main Menu", callback_data="back_to_start")
            ]
        ])
        
        return message, InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def help_menu() -> tuple[str, InlineKeyboardMarkup]:
        """Enterprise help menu"""
        ui = EnterpriseUI
        
        message = f"""
{ui.header('COMMAND REFERENCE', ui.ICON['help'])}

{ui.separator('heavy')}

{ui.section('💰 WALLET MANAGEMENT')}
<code>/wallet</code> - Wallet details & balance
<code>/deposit</code> - Fund your wallet
<code>/balance</code> - Quick balance check
<code>/export_wallet</code> - Export private keys

{ui.separator('light')}

{ui.section('📊 TRADING')}
<code>/buy &lt;token&gt; &lt;amount&gt;</code> - Buy tokens
<code>/sell &lt;token&gt; &lt;amount&gt;</code> - Sell tokens
<code>/positions</code> - View open positions
<code>/history</code> - Trade history

{ui.separator('light')}

{ui.section('🧠 AI & ANALYSIS')}
<code>/ai &lt;token&gt;</code> - AI safety analysis
<code>/analyze &lt;token&gt;</code> - Full token report
<code>/trending</code> - Viral tokens (sentiment)

{ui.separator('light')}

{ui.section('🎯 AUTO-SNIPER')}
<code>/snipe &lt;token&gt;</code> - Manual snipe
<code>/snipe_enable</code> - Enable auto-sniper
<code>/snipe_disable</code> - Disable auto-sniper
<code>/sniper_status</code> - Current status

{ui.separator('light')}

{ui.section('👥 COPY TRADING')}
<code>/leaderboard</code> - View elite traders
<code>/copy &lt;trader_id&gt;</code> - Copy a trader
<code>/stop_copy &lt;id&gt;</code> - Stop copying
<code>/my_copies</code> - Active copies

{ui.separator('light')}

{ui.section('🤖 AUTOMATION')}
<code>/autostart</code> - Enable AI trading
<code>/autostop</code> - Disable AI trading
<code>/autostatus</code> - Automation status

{ui.separator('light')}

{ui.section('📈 STATS & REWARDS')}
<code>/stats</code> - Your performance
<code>/rewards</code> - Points & achievements
<code>/rankings</code> - Wallet rankings

{ui.separator('light')}

{ui.section('📚 STRATEGY MARKETPLACE')}
<code>/strategies</code> - Browse strategies
<code>/my_strategies</code> - Your strategies
<code>/publish_strategy</code> - Publish new

{ui.separator('heavy')}

{ui.ICON['protection']} <b>All trades protected with MEV defense</b>
{ui.ICON['lock']} <b>Platform fee: 0.5% per trade</b>
"""
        
        keyboard = [
            [
                InlineKeyboardButton(f"{ui.ICON['ai']} AI Guide", callback_data="help_ai"),
                InlineKeyboardButton(f"{ui.ICON['trading']} Trading Guide", callback_data="help_trading")
            ],
            [
                InlineKeyboardButton(f"{ui.ICON['sniper']} Sniper Guide", callback_data="help_sniper"),
                InlineKeyboardButton(f"{ui.ICON['social']} Copy Guide", callback_data="help_copy")
            ],
            [
                InlineKeyboardButton(f"{ui.ICON['back']} Main Menu", callback_data="back_to_start")
            ]
        ]
        
        return message, InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def stats_dashboard(user_name: str, stats: Dict, rewards: Dict) -> tuple[str, InlineKeyboardMarkup]:
        """Enterprise stats dashboard"""
        ui = EnterpriseUI
        
        win_rate = stats.get('win_rate', 0)
        total_pnl = stats.get('total_pnl', 0)
        total_trades = stats.get('total_trades', 0)
        profitable = stats.get('profitable_trades', 0)
        
        message = f"""
{ui.header('PERFORMANCE DASHBOARD', ui.ICON['chart'])}

{ui.separator('heavy')}

{ui.section('TRADER PROFILE')}
{ui.ICON['star']} <b>Name:</b> {user_name}
{ui.tier_badge(stats.get('tier', 'bronze'))}
{ui.stat_line('Reputation', f"{stats.get('reputation_score', 0):.1f}/100", ui.ICON['trophy'])}
{ui.stat_line('Followers', str(stats.get('followers', 0)), ui.ICON['social'])}

{ui.separator('light')}

{ui.section('TRADING STATS (30 DAYS)')}
{ui.stat_line('Total Trades', str(total_trades), ui.ICON['trading'])}
{ui.stat_line('Profitable', f"{profitable}/{total_trades}", ui.ICON['success'])}
{ui.stat_line('Win Rate', f"{win_rate:.1f}%", ui.ICON['chart'])}
{ui.percentage(win_rate)}

{ui.separator('light')}

{ui.section('PROFIT & LOSS')}
{ui.stat_line('Total P&L', f"{total_pnl:+.4f} SOL", ui.ICON['wallet'])}
{ui.stat_line('Best Trade', f"+{stats.get('best_trade', 0):.4f} SOL", '🟢')}
{ui.stat_line('Worst Trade', f"{stats.get('worst_trade', 0):.4f} SOL", '🔴')}

{ui.separator('light')}

{ui.section('REWARDS & GAMIFICATION')}
{ui.stat_line('Points', str(rewards.get('points', 0)), ui.ICON['star'])}
{ui.stat_line('Tier', rewards.get('tier', 'Novice'), ui.ICON['trophy'])}
{ui.progress_bar(rewards.get('points', 0), rewards.get('next_tier_points', 100))}

{ui.separator('heavy')}

{ui.ICON['info']} <i>Keep trading to climb the ranks!</i>
"""
        
        keyboard = [
            [
                InlineKeyboardButton(f"{ui.ICON['trading']} Trade History", callback_data="trade_history"),
                InlineKeyboardButton(f"{ui.ICON['chart']} Positions", callback_data="view_positions")
            ],
            [
                InlineKeyboardButton(f"{ui.ICON['rewards']} Rewards", callback_data="view_rewards"),
                InlineKeyboardButton(f"{ui.ICON['trophy']} Leaderboard", callback_data="leaderboard")
            ],
            [
                InlineKeyboardButton(f"{ui.ICON['back']} Main Menu", callback_data="back_to_start")
            ]
        ]
        
        return message, InlineKeyboardMarkup(keyboard)

