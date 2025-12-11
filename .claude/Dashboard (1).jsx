import React, { useState, useEffect, useRef } from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';
import { Activity, TrendingUp, Shield, Zap, Brain, Users, DollarSign, AlertTriangle, CheckCircle, Clock, Target, Award } from 'lucide-react';

// 🎨 APOLLO Brand Colors
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

// 📊 Dashboard Component
export default function APOLLODashboard() {
  const [systemStatus, setSystemStatus] = useState('operational');
  const [activeTrades, setActiveTrades] = useState([]);
  const [botMetrics, setBotMetrics] = useState({
    totalTrades: 0,
    winRate: 0,
    totalPnL: 0,
    activeUsers: 0,
    eliteWallets: 441,
    predictionsToday: 0,
    flashLoansExecuted: 0,
    avgConfidence: 0
  });
  const [realtimeData, setRealtimeData] = useState([]);
  const [phaseStatus, setPhaseStatus] = useState({
    predictions: 'active',
    flashLoans: 'active',
    launchPredictor: 'active',
    predictionMarkets: 'active'
  });

  // 🔄 Simulate Real-Time Updates
  useEffect(() => {
    const interval = setInterval(() => {
      // Update metrics
      setBotMetrics(prev => ({
        ...prev,
        totalTrades: prev.totalTrades + Math.floor(Math.random() * 3),
        winRate: 72 + Math.random() * 10,
        totalPnL: prev.totalPnL + (Math.random() * 100 - 20),
        activeUsers: 847 + Math.floor(Math.random() * 50),
        predictionsToday: prev.predictionsToday + Math.floor(Math.random() * 2),
        flashLoansExecuted: prev.flashLoansExecuted + Math.floor(Math.random() * 1),
        avgConfidence: 75 + Math.random() * 15
      }));

      // Add real-time data point
      setRealtimeData(prev => {
        const newData = [...prev, {
          time: new Date().toLocaleTimeString(),
          pnl: (Math.random() * 200 - 50),
          confidence: 70 + Math.random() * 20,
          trades: Math.floor(Math.random() * 5)
        }];
        return newData.slice(-20); // Keep last 20 points
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  // 📈 Sample Performance Data
  const performanceData = [
    { date: 'Mon', pnl: 2500, trades: 45, winRate: 72 },
    { date: 'Tue', pnl: 3200, trades: 52, winRate: 75 },
    { date: 'Wed', pnl: 1800, trades: 38, winRate: 68 },
    { date: 'Thu', pnl: 4100, trades: 61, winRate: 79 },
    { date: 'Fri', pnl: 3600, trades: 54, winRate: 74 },
    { date: 'Sat', pnl: 2900, trades: 47, winRate: 71 },
    { date: 'Today', pnl: 3400, trades: 49, winRate: 76 }
  ];

  // 🎯 Phase Distribution
  const phaseDistribution = [
    { name: 'Predictions', value: 42, color: COLORS.primary },
    { name: 'Flash Loans', value: 28, color: COLORS.secondary },
    { name: 'Launch Snipes', value: 20, color: COLORS.warning },
    { name: 'Markets', value: 10, color: COLORS.success }
  ];

  // 🔥 Top Performing Tokens
  const topTokens = [
    { symbol: '$BONK', pnl: '+$4,250', winRate: 85, trades: 12 },
    { symbol: '$WIF', pnl: '+$3,890', winRate: 82, trades: 9 },
    { symbol: '$PYTH', pnl: '+$3,120', winRate: 78, trades: 15 },
    { symbol: '$JTO', pnl: '+$2,640', winRate: 75, trades: 8 },
    { symbol: '$JUP', pnl: '+$2,310', winRate: 73, trades: 11 }
  ];

  return (
    <div style={{
      minHeight: '100vh',
      background: `linear-gradient(135deg, ${COLORS.dark} 0%, #0f1329 100%)`,
      color: COLORS.text,
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      padding: '2rem'
    }}>
      
      {/* 🎯 Header */}
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
            🦄 APOLLO CyberSentinel
          </h1>
          <p style={{ color: COLORS.textMuted, fontSize: '1.1rem' }}>
            Enterprise Trading Intelligence Platform
          </p>
        </div>
        
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem'
        }}>
          <StatusBadge status={systemStatus} />
          <div style={{
            background: COLORS.darkCard,
            padding: '0.75rem 1.5rem',
            borderRadius: '12px',
            border: `2px solid ${COLORS.primary}`,
            boxShadow: `0 0 20px ${COLORS.primary}40`
          }}>
            <div style={{ fontSize: '0.8rem', color: COLORS.textMuted }}>System Time</div>
            <div style={{ fontSize: '1.1rem', fontWeight: '700', color: COLORS.primary }}>
              {new Date().toLocaleTimeString()}
            </div>
          </div>
        </div>
      </header>

      {/* 📊 Metrics Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '1.5rem',
        marginBottom: '2rem'
      }}>
        <MetricCard
          icon={<DollarSign size={32} />}
          title="Total P&L"
          value={`$${botMetrics.totalPnL.toFixed(2)}`}
          change="+15.3%"
          positive={true}
          color={COLORS.success}
        />
        <MetricCard
          icon={<TrendingUp size={32} />}
          title="Win Rate"
          value={`${botMetrics.winRate.toFixed(1)}%`}
          change="+2.4%"
          positive={true}
          color={COLORS.primary}
        />
        <MetricCard
          icon={<Activity size={32} />}
          title="Total Trades"
          value={botMetrics.totalTrades}
          change="Live"
          positive={true}
          color={COLORS.secondary}
        />
        <MetricCard
          icon={<Users size={32} />}
          title="Active Users"
          value={botMetrics.activeUsers}
          change="+8.2%"
          positive={true}
          color={COLORS.warning}
        />
        <MetricCard
          icon={<Brain size={32} />}
          title="AI Confidence"
          value={`${botMetrics.avgConfidence.toFixed(1)}%`}
          change="ULTRA"
          positive={true}
          color={COLORS.primary}
        />
        <MetricCard
          icon={<Zap size={32} />}
          title="Flash Loans"
          value={botMetrics.flashLoansExecuted}
          change="Today"
          positive={true}
          color={COLORS.secondary}
        />
        <MetricCard
          icon={<Target size={32} />}
          title="Predictions"
          value={botMetrics.predictionsToday}
          change="24h"
          positive={true}
          color={COLORS.warning}
        />
        <MetricCard
          icon={<Shield size={32} />}
          title="Elite Wallets"
          value={botMetrics.eliteWallets}
          change="Tracked"
          positive={true}
          color={COLORS.success}
        />
      </div>

      {/* 📈 Main Charts Section */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))',
        gap: '1.5rem',
        marginBottom: '2rem'
      }}>
        
        {/* Performance Chart */}
        <ChartCard title="7-Day Performance" icon={<TrendingUp size={24} />}>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={performanceData}>
              <defs>
                <linearGradient id="colorPnl" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.8}/>
                  <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.textMuted + '30'} />
              <XAxis dataKey="date" stroke={COLORS.textMuted} />
              <YAxis stroke={COLORS.textMuted} />
              <Tooltip 
                contentStyle={{ 
                  background: COLORS.darkCard, 
                  border: `1px solid ${COLORS.primary}`,
                  borderRadius: '8px'
                }}
              />
              <Area 
                type="monotone" 
                dataKey="pnl" 
                stroke={COLORS.primary} 
                fillOpacity={1} 
                fill="url(#colorPnl)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Real-Time Activity */}
        <ChartCard title="Real-Time Activity" icon={<Activity size={24} />}>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={realtimeData}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.textMuted + '30'} />
              <XAxis dataKey="time" stroke={COLORS.textMuted} />
              <YAxis stroke={COLORS.textMuted} />
              <Tooltip 
                contentStyle={{ 
                  background: COLORS.darkCard, 
                  border: `1px solid ${COLORS.secondary}`,
                  borderRadius: '8px'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="confidence" 
                stroke={COLORS.secondary} 
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* 📊 Phase Status & Distribution */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '1.5rem',
        marginBottom: '2rem'
      }}>
        
        {/* Phase Status */}
        <ChartCard title="4-Phase System Status" icon={<Shield size={24} />}>
          <div style={{ padding: '1rem' }}>
            <PhaseStatusItem 
              phase="Phase 1: Predictions" 
              status={phaseStatus.predictions}
              metric="87% avg confidence"
            />
            <PhaseStatusItem 
              phase="Phase 2: Flash Loans" 
              status={phaseStatus.flashLoans}
              metric="100x leverage active"
            />
            <PhaseStatusItem 
              phase="Phase 3: Launch Predictor" 
              status={phaseStatus.launchPredictor}
              metric="2-6hr early detection"
            />
            <PhaseStatusItem 
              phase="Phase 4: Pred Markets" 
              status={phaseStatus.predictionMarkets}
              metric="12 active markets"
            />
          </div>
        </ChartCard>

        {/* Phase Distribution */}
        <ChartCard title="Trade Distribution by Phase" icon={<Target size={24} />}>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={phaseDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {phaseDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* 🏆 Top Performers */}
      <ChartCard title="Top Performing Tokens" icon={<Award size={24} />}>
        <div style={{ padding: '1rem' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: `2px solid ${COLORS.textMuted}40` }}>
                <th style={{ padding: '0.75rem', textAlign: 'left', color: COLORS.textMuted }}>Token</th>
                <th style={{ padding: '0.75rem', textAlign: 'right', color: COLORS.textMuted }}>P&L</th>
                <th style={{ padding: '0.75rem', textAlign: 'right', color: COLORS.textMuted }}>Win Rate</th>
                <th style={{ padding: '0.75rem', textAlign: 'right', color: COLORS.textMuted }}>Trades</th>
              </tr>
            </thead>
            <tbody>
              {topTokens.map((token, index) => (
                <tr key={index} style={{ 
                  borderBottom: `1px solid ${COLORS.textMuted}20`,
                  transition: 'background 0.2s'
                }}>
                  <td style={{ padding: '1rem', fontWeight: '700', fontSize: '1.1rem' }}>
                    {token.symbol}
                  </td>
                  <td style={{ 
                    padding: '1rem', 
                    textAlign: 'right',
                    color: COLORS.success,
                    fontWeight: '700'
                  }}>
                    {token.pnl}
                  </td>
                  <td style={{ padding: '1rem', textAlign: 'right' }}>
                    {token.winRate}%
                  </td>
                  <td style={{ padding: '1rem', textAlign: 'right', color: COLORS.textMuted }}>
                    {token.trades}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </ChartCard>

      {/* 🔔 System Alerts */}
      <ChartCard title="System Alerts & Notifications" icon={<AlertTriangle size={24} />}>
        <div style={{ padding: '1rem' }}>
          <Alert type="success" message="Flash loan arbitrage executed: +$247 profit in 0.4s" />
          <Alert type="info" message="New ULTRA confidence prediction: $BONK expected +65% in 6h" />
          <Alert type="warning" message="Elite wallet 0x7a8f... accumulated 50,000 $WIF tokens" />
          <Alert type="info" message="Launch prediction: New token detected 4.2h before launch" />
          <Alert type="success" message="Prediction market resolved: UP winners receive 1.84x payout" />
        </div>
      </ChartCard>

    </div>
  );
}

// 🎨 Reusable Components

function MetricCard({ icon, title, value, change, positive, color }) {
  return (
    <div style={{
      background: COLORS.darkCard,
      padding: '1.5rem',
      borderRadius: '16px',
      border: `2px solid ${color}40`,
      boxShadow: `0 4px 20px ${color}20`,
      transition: 'transform 0.2s, box-shadow 0.2s',
      cursor: 'pointer'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-4px)';
      e.currentTarget.style.boxShadow = `0 8px 30px ${color}40`;
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = `0 4px 20px ${color}20`;
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ color: color, opacity: 0.9 }}>
          {icon}
        </div>
        <span style={{
          fontSize: '0.85rem',
          color: positive ? COLORS.success : COLORS.danger,
          fontWeight: '600'
        }}>
          {change}
        </span>
      </div>
      <div style={{ marginTop: '1rem' }}>
        <div style={{ fontSize: '0.9rem', color: COLORS.textMuted, marginBottom: '0.25rem' }}>
          {title}
        </div>
        <div style={{ fontSize: '2rem', fontWeight: '800', color: color }}>
          {value}
        </div>
      </div>
    </div>
  );
}

function ChartCard({ title, icon, children }) {
  return (
    <div style={{
      background: COLORS.darkCard,
      padding: '1.5rem',
      borderRadius: '16px',
      border: `2px solid ${COLORS.textMuted}20`,
      boxShadow: `0 4px 20px rgba(0,0,0,0.3)`
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        marginBottom: '1.5rem',
        color: COLORS.primary
      }}>
        {icon}
        <h3 style={{ fontSize: '1.25rem', fontWeight: '700', margin: 0 }}>
          {title}
        </h3>
      </div>
      {children}
    </div>
  );
}

function StatusBadge({ status }) {
  const statusConfig = {
    operational: { color: COLORS.success, text: 'OPERATIONAL', icon: <CheckCircle size={20} /> },
    warning: { color: COLORS.warning, text: 'WARNING', icon: <AlertTriangle size={20} /> },
    error: { color: COLORS.danger, text: 'ERROR', icon: <AlertTriangle size={20} /> }
  };

  const config = statusConfig[status] || statusConfig.operational;

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      background: `${config.color}20`,
      border: `2px solid ${config.color}`,
      padding: '0.5rem 1rem',
      borderRadius: '12px',
      fontWeight: '700',
      color: config.color,
      boxShadow: `0 0 20px ${config.color}40`
    }}>
      {config.icon}
      {config.text}
    </div>
  );
}

function PhaseStatusItem({ phase, status, metric }) {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '1rem',
      marginBottom: '0.75rem',
      background: status === 'active' ? `${COLORS.success}10` : `${COLORS.danger}10`,
      border: `1px solid ${status === 'active' ? COLORS.success : COLORS.danger}40`,
      borderRadius: '8px'
    }}>
      <div>
        <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>{phase}</div>
        <div style={{ fontSize: '0.85rem', color: COLORS.textMuted }}>{metric}</div>
      </div>
      <div style={{
        padding: '0.4rem 0.8rem',
        borderRadius: '6px',
        background: status === 'active' ? COLORS.success : COLORS.danger,
        color: COLORS.text,
        fontSize: '0.75rem',
        fontWeight: '700',
        textTransform: 'uppercase'
      }}>
        {status}
      </div>
    </div>
  );
}

function Alert({ type, message }) {
  const typeConfig = {
    success: { color: COLORS.success, icon: <CheckCircle size={18} /> },
    info: { color: COLORS.secondary, icon: <Activity size={18} /> },
    warning: { color: COLORS.warning, icon: <AlertTriangle size={18} /> },
    error: { color: COLORS.danger, icon: <AlertTriangle size={18} /> }
  };

  const config = typeConfig[type] || typeConfig.info;

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      padding: '1rem',
      marginBottom: '0.75rem',
      background: `${config.color}10`,
      border: `1px solid ${config.color}40`,
      borderRadius: '8px',
      color: COLORS.text
    }}>
      <div style={{ color: config.color, flexShrink: 0 }}>
        {config.icon}
      </div>
      <div style={{ fontSize: '0.95rem' }}>
        {message}
      </div>
      <div style={{ 
        marginLeft: 'auto', 
        fontSize: '0.75rem', 
        color: COLORS.textMuted,
        flexShrink: 0
      }}>
        {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
}
