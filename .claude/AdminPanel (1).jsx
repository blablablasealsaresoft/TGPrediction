import React, { useState, useEffect } from 'react';
import { Activity, Database, Zap, Users, Settings, AlertTriangle, CheckCircle, XCircle, RefreshCw, Download, Upload, Eye, EyeOff } from 'lucide-react';

const COLORS = {
  primary: '#00ff88',
  secondary: '#00d4ff',
  danger: '#ff4757',
  warning: '#ffa502',
  success: '#26de81',
  dark: '#0a0e27',
  darkCard: '#1a1f3a',
  text: '#ffffff',
  textMuted: '#8b92b8'
};

export default function AdminPanel() {
  const [services, setServices] = useState({
    tradingBot: { status: 'healthy', uptime: 99.97, lastCheck: new Date() },
    database: { status: 'healthy', connections: 12, responseTime: 45 },
    redis: { status: 'healthy', memoryUsage: 67, hitRate: 94.3 },
    rpc: { status: 'healthy', provider: 'Helius', latency: 120 },
    telegram: { status: 'healthy', usersOnline: 847, messagesPerMin: 42 },
    ai: { status: 'healthy', modelAccuracy: 76.8, predictionsToday: 1247 }
  });

  const [config, setConfig] = useState({
    ALLOW_BROADCAST: false,
    AUTO_TRADE_ENABLED: true,
    FLASH_LOAN_ENABLED: true,
    LAUNCH_MONITOR_ENABLED: true,
    MIN_CONFIDENCE: 75,
    MAX_DAILY_TRADES: 25,
    DAILY_LIMIT_SOL: 10,
    ELITE_WALLETS_COUNT: 441,
    API_RATE_LIMIT: 100
  });

  const [logs, setLogs] = useState([
    { timestamp: new Date(), level: 'INFO', message: 'Trading bot initialized successfully', module: 'Core' },
    { timestamp: new Date(), level: 'SUCCESS', message: 'Twitter monitoring active (Twikit method)', module: 'Social' },
    { timestamp: new Date(), level: 'INFO', message: 'Flash loan scanner started (2s interval)', module: 'Arbitrage' },
    { timestamp: new Date(), level: 'SUCCESS', message: 'Elite wallet sync completed (441 wallets)', module: 'CopyTrading' },
    { timestamp: new Date(), level: 'WARNING', message: 'DexScreener rate limit approaching', module: 'API' }
  ]);

  const [showSecrets, setShowSecrets] = useState(false);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setServices(prev => ({
        ...prev,
        telegram: {
          ...prev.telegram,
          messagesPerMin: Math.floor(35 + Math.random() * 15)
        },
        ai: {
          ...prev.ai,
          predictionsToday: prev.ai.predictionsToday + Math.floor(Math.random() * 3)
        }
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const restartService = (serviceName) => {
    alert(`Restarting ${serviceName}... This will take 30-60 seconds.`);
  };

  const updateConfig = (key, value) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const exportConfig = () => {
    const configText = Object.entries(config)
      .map(([key, value]) => `${key}=${value}`)
      .join('\n');
    
    const blob = new Blob([configText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'apollo-config.env';
    a.click();
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: `linear-gradient(135deg, ${COLORS.dark} 0%, #0f1329 100%)`,
      color: COLORS.text,
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      padding: '2rem'
    }}>

      {/* Header */}
      <header style={{
        marginBottom: '2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h1 style={{
            fontSize: '2.5rem',
            fontWeight: '800',
            background: `linear-gradient(135deg, ${COLORS.primary} 0%, ${COLORS.secondary} 100%)`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '0.5rem'
          }}>
            🔐 Admin Control Panel
          </h1>
          <p style={{ color: COLORS.textMuted, fontSize: '1.1rem' }}>
            APOLLO CyberSentinel - System Administration
          </p>
        </div>
        
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button onClick={exportConfig} style={{
            padding: '0.75rem 1.5rem',
            background: COLORS.secondary,
            color: COLORS.dark,
            border: 'none',
            borderRadius: '8px',
            fontWeight: '700',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <Download size={20} />
            Export Config
          </button>
        </div>
      </header>

      {/* Service Status Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
        gap: '1.5rem',
        marginBottom: '2rem'
      }}>
        
        <ServiceCard
          title="Trading Bot"
          icon={<Activity size={24} />}
          status={services.tradingBot.status}
          metrics={[
            { label: 'Uptime', value: `${services.tradingBot.uptime}%` },
            { label: 'Last Health Check', value: services.tradingBot.lastCheck.toLocaleTimeString() }
          ]}
          onRestart={() => restartService('Trading Bot')}
        />

        <ServiceCard
          title="PostgreSQL Database"
          icon={<Database size={24} />}
          status={services.database.status}
          metrics={[
            { label: 'Active Connections', value: services.database.connections },
            { label: 'Avg Response Time', value: `${services.database.responseTime}ms` }
          ]}
          onRestart={() => restartService('Database')}
        />

        <ServiceCard
          title="Redis Cache"
          icon={<Zap size={24} />}
          status={services.redis.status}
          metrics={[
            { label: 'Memory Usage', value: `${services.redis.memoryUsage}%` },
            { label: 'Hit Rate', value: `${services.redis.hitRate}%` }
          ]}
          onRestart={() => restartService('Redis')}
        />

        <ServiceCard
          title="RPC Node"
          icon={<Activity size={24} />}
          status={services.rpc.status}
          metrics={[
            { label: 'Provider', value: services.rpc.provider },
            { label: 'Latency', value: `${services.rpc.latency}ms` }
          ]}
          onRestart={() => restartService('RPC')}
        />

        <ServiceCard
          title="Telegram Bot"
          icon={<Users size={24} />}
          status={services.telegram.status}
          metrics={[
            { label: 'Users Online', value: services.telegram.usersOnline },
            { label: 'Messages/min', value: services.telegram.messagesPerMin }
          ]}
          onRestart={() => restartService('Telegram')}
        />

        <ServiceCard
          title="AI Engine"
          icon={<Activity size={24} />}
          status={services.ai.status}
          metrics={[
            { label: 'Model Accuracy', value: `${services.ai.modelAccuracy}%` },
            { label: 'Predictions Today', value: services.ai.predictionsToday }
          ]}
          onRestart={() => restartService('AI Engine')}
        />
      </div>

      {/* Configuration Panel */}
      <ConfigPanel 
        config={config}
        onUpdate={updateConfig}
        showSecrets={showSecrets}
        toggleSecrets={() => setShowSecrets(!showSecrets)}
      />

      {/* Real-Time Logs */}
      <LogViewer logs={logs} />

      {/* Quick Actions */}
      <QuickActions />
    </div>
  );
}

function ServiceCard({ title, icon, status, metrics, onRestart }) {
  const statusConfig = {
    healthy: { color: COLORS.success, icon: <CheckCircle size={20} />, text: 'HEALTHY' },
    warning: { color: COLORS.warning, icon: <AlertTriangle size={20} />, text: 'WARNING' },
    error: { color: COLORS.danger, icon: <XCircle size={20} />, text: 'ERROR' }
  };

  const config = statusConfig[status] || statusConfig.healthy;

  return (
    <div style={{
      background: COLORS.darkCard,
      padding: '1.5rem',
      borderRadius: '16px',
      border: `2px solid ${config.color}40`,
      boxShadow: `0 4px 20px ${config.color}20`
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '1rem'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          color: COLORS.primary
        }}>
          {icon}
          <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: '700' }}>{title}</h3>
        </div>
        
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.4rem 0.8rem',
          background: `${config.color}20`,
          border: `1px solid ${config.color}`,
          borderRadius: '8px',
          fontSize: '0.75rem',
          fontWeight: '700',
          color: config.color
        }}>
          {config.icon}
          {config.text}
        </div>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        {metrics.map((metric, index) => (
          <div key={index} style={{
            display: 'flex',
            justifyContent: 'space-between',
            padding: '0.5rem 0',
            borderBottom: index < metrics.length - 1 ? `1px solid ${COLORS.textMuted}20` : 'none'
          }}>
            <span style={{ color: COLORS.textMuted }}>{metric.label}</span>
            <span style={{ fontWeight: '700', color: COLORS.text }}>{metric.value}</span>
          </div>
        ))}
      </div>

      <button onClick={onRestart} style={{
        width: '100%',
        padding: '0.75rem',
        background: `${COLORS.secondary}20`,
        border: `2px solid ${COLORS.secondary}`,
        borderRadius: '8px',
        color: COLORS.secondary,
        fontWeight: '700',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        transition: 'all 0.2s'
      }}>
        <RefreshCw size={18} />
        Restart Service
      </button>
    </div>
  );
}

function ConfigPanel({ config, onUpdate, showSecrets, toggleSecrets }) {
  return (
    <div style={{
      background: COLORS.darkCard,
      padding: '2rem',
      borderRadius: '16px',
      border: `2px solid ${COLORS.primary}40`,
      marginBottom: '2rem'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1.5rem'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          color: COLORS.primary
        }}>
          <Settings size={24} />
          <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: '700' }}>
            System Configuration
          </h2>
        </div>
        
        <button onClick={toggleSecrets} style={{
          padding: '0.5rem 1rem',
          background: `${COLORS.warning}20`,
          border: `2px solid ${COLORS.warning}`,
          borderRadius: '8px',
          color: COLORS.warning,
          fontWeight: '700',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          {showSecrets ? <EyeOff size={18} /> : <Eye size={18} />}
          {showSecrets ? 'Hide' : 'Show'} Secrets
        </button>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '1.5rem'
      }}>
        
        <ConfigItem
          label="Allow Broadcast (CRITICAL)"
          value={config.ALLOW_BROADCAST}
          type="boolean"
          onChange={(val) => onUpdate('ALLOW_BROADCAST', val)}
          danger={true}
        />

        <ConfigItem
          label="Auto-Trade Enabled"
          value={config.AUTO_TRADE_ENABLED}
          type="boolean"
          onChange={(val) => onUpdate('AUTO_TRADE_ENABLED', val)}
        />

        <ConfigItem
          label="Flash Loans Enabled"
          value={config.FLASH_LOAN_ENABLED}
          type="boolean"
          onChange={(val) => onUpdate('FLASH_LOAN_ENABLED', val)}
        />

        <ConfigItem
          label="Launch Monitor Enabled"
          value={config.LAUNCH_MONITOR_ENABLED}
          type="boolean"
          onChange={(val) => onUpdate('LAUNCH_MONITOR_ENABLED', val)}
        />

        <ConfigItem
          label="Min Confidence (%)"
          value={config.MIN_CONFIDENCE}
          type="number"
          onChange={(val) => onUpdate('MIN_CONFIDENCE', parseInt(val))}
        />

        <ConfigItem
          label="Max Daily Trades"
          value={config.MAX_DAILY_TRADES}
          type="number"
          onChange={(val) => onUpdate('MAX_DAILY_TRADES', parseInt(val))}
        />

        <ConfigItem
          label="Daily Limit (SOL)"
          value={config.DAILY_LIMIT_SOL}
          type="number"
          onChange={(val) => onUpdate('DAILY_LIMIT_SOL', parseFloat(val))}
        />

        <ConfigItem
          label="Elite Wallets Count"
          value={config.ELITE_WALLETS_COUNT}
          type="number"
          onChange={(val) => onUpdate('ELITE_WALLETS_COUNT', parseInt(val))}
          disabled={true}
        />
      </div>

      <div style={{
        marginTop: '1.5rem',
        padding: '1rem',
        background: `${COLORS.warning}10`,
        border: `1px solid ${COLORS.warning}40`,
        borderRadius: '8px',
        color: COLORS.textMuted
      }}>
        <strong style={{ color: COLORS.warning }}>⚠️ Warning:</strong> Configuration changes require service restart to take effect.
        Changes to ALLOW_BROADCAST should NEVER be made in production without proper testing.
      </div>
    </div>
  );
}

function ConfigItem({ label, value, type, onChange, danger = false, disabled = false }) {
  return (
    <div style={{
      padding: '1rem',
      background: COLORS.dark,
      borderRadius: '8px',
      border: danger ? `2px solid ${COLORS.danger}40` : `1px solid ${COLORS.textMuted}20`
    }}>
      <label style={{
        display: 'block',
        marginBottom: '0.5rem',
        color: danger ? COLORS.danger : COLORS.textMuted,
        fontSize: '0.9rem',
        fontWeight: '600'
      }}>
        {label}
        {danger && <span style={{ marginLeft: '0.5rem', color: COLORS.danger }}>⚠️</span>}
      </label>
      
      {type === 'boolean' ? (
        <label style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          cursor: 'pointer'
        }}>
          <input
            type="checkbox"
            checked={value}
            onChange={(e) => onChange(e.target.checked)}
            disabled={disabled}
            style={{
              width: '20px',
              height: '20px',
              cursor: disabled ? 'not-allowed' : 'pointer'
            }}
          />
          <span style={{ color: value ? COLORS.success : COLORS.danger, fontWeight: '700' }}>
            {value ? 'ENABLED' : 'DISABLED'}
          </span>
        </label>
      ) : (
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          style={{
            width: '100%',
            padding: '0.75rem',
            background: COLORS.darkCard,
            border: `2px solid ${COLORS.primary}40`,
            borderRadius: '8px',
            color: COLORS.text,
            fontSize: '1rem',
            fontWeight: '700',
            cursor: disabled ? 'not-allowed' : 'text'
          }}
        />
      )}
    </div>
  );
}

function LogViewer({ logs }) {
  return (
    <div style={{
      background: COLORS.darkCard,
      padding: '2rem',
      borderRadius: '16px',
      border: `2px solid ${COLORS.primary}40`,
      marginBottom: '2rem'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        marginBottom: '1.5rem',
        color: COLORS.primary
      }}>
        <Activity size={24} />
        <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: '700' }}>
          Real-Time System Logs
        </h2>
      </div>

      <div style={{
        background: COLORS.dark,
        padding: '1rem',
        borderRadius: '8px',
        maxHeight: '400px',
        overflowY: 'auto',
        fontFamily: '"Courier New", monospace',
        fontSize: '0.9rem'
      }}>
        {logs.map((log, index) => (
          <LogEntry key={index} log={log} />
        ))}
      </div>
    </div>
  );
}

function LogEntry({ log }) {
  const levelColors = {
    INFO: COLORS.secondary,
    SUCCESS: COLORS.success,
    WARNING: COLORS.warning,
    ERROR: COLORS.danger
  };

  return (
    <div style={{
      padding: '0.75rem',
      marginBottom: '0.5rem',
      background: `${levelColors[log.level]}10`,
      border: `1px solid ${levelColors[log.level]}40`,
      borderRadius: '6px',
      display: 'flex',
      gap: '1rem',
      alignItems: 'flex-start'
    }}>
      <span style={{ color: COLORS.textMuted, minWidth: '100px' }}>
        {log.timestamp.toLocaleTimeString()}
      </span>
      <span style={{
        color: levelColors[log.level],
        fontWeight: '700',
        minWidth: '80px'
      }}>
        [{log.level}]
      </span>
      <span style={{ color: COLORS.primary, minWidth: '120px' }}>
        [{log.module}]
      </span>
      <span style={{ color: COLORS.text, flex: 1 }}>
        {log.message}
      </span>
    </div>
  );
}

function QuickActions() {
  const actions = [
    { label: 'Restart All Services', icon: <RefreshCw size={20} />, color: COLORS.warning },
    { label: 'Backup Database', icon: <Download size={20} />, color: COLORS.secondary },
    { label: 'View Full Logs', icon: <Activity size={20} />, color: COLORS.primary },
    { label: 'Emergency Stop', icon: <AlertTriangle size={20} />, color: COLORS.danger }
  ];

  return (
    <div style={{
      background: COLORS.darkCard,
      padding: '2rem',
      borderRadius: '16px',
      border: `2px solid ${COLORS.primary}40`
    }}>
      <h2 style={{
        margin: '0 0 1.5rem 0',
        fontSize: '1.5rem',
        fontWeight: '700',
        color: COLORS.primary
      }}>
        Quick Actions
      </h2>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem'
      }}>
        {actions.map((action, index) => (
          <button key={index} style={{
            padding: '1.25rem',
            background: `${action.color}20`,
            border: `2px solid ${action.color}`,
            borderRadius: '12px',
            color: action.color,
            fontWeight: '700',
            cursor: 'pointer',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '0.75rem',
            transition: 'all 0.2s'
          }}>
            {action.icon}
            {action.label}
          </button>
        ))}
      </div>
    </div>
  );
}
