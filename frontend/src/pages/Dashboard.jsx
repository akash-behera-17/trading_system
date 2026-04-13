import React, { useEffect, useState } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { useAuth } from '../context/useAuth';
import StockChart from '../components/StockChart';
import './Dashboard.css';

const Dashboard = () => {
    const [searchParams] = useSearchParams();
    const ticker = searchParams.get('ticker');
    const [ta, setTa] = useState(null);
    const [aiData, setAiData] = useState(null);
    const [aiUnavailable, setAiUnavailable] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const { logout } = useAuth();

    useEffect(() => {
        const fetchAll = async () => {
            try {
                setLoading(true);
                setError('');
                setAiUnavailable(false);
                const [taRes, aiRes] = await Promise.allSettled([
                    api.get('/api/stocks/technical-analysis', { params: { ticker } }),
                    api.post('/predict', { ticker })
                ]);
                if (taRes.status === 'fulfilled') setTa(taRes.value.data);
                else setError('Failed to load technical analysis');
                if (aiRes.status === 'fulfilled') {
                    setAiData(aiRes.value.data);
                } else {
                    setAiData(null);
                    setAiUnavailable(true);
                }
            } catch (fetchError) {
                console.error('Failed to load dashboard data:', fetchError);
                setError('Failed to load data');
            } finally {
                setLoading(false);
            }
        };
        if (ticker) fetchAll();
    }, [ticker]);



    const handleLogout = () => { logout(); navigate('/'); };

    if (!ticker) return <div className="dashboard"><div className="dash-loading"><span>No ticker selected.</span></div></div>;
    if (loading) return (
        <div className="dashboard">
            <div className="dash-loading">
                <div className="spin-ring"></div>
                <span>Loading analysis for {ticker}...</span>
            </div>
        </div>
    );
    if (error && !ta) return <div className="dashboard"><div className="dash-loading"><span style={{ color: '#f87171' }}>{error}</span></div></div>;

    const clr = (s) => s === 'bullish' ? 'text-green' : s === 'bearish' ? 'text-red' : 'text-muted';
    const badgeCls = (s) => s === 'bullish' ? 'bull' : s === 'bearish' ? 'bear' : 'neut';
    const lbl = (s) => s === 'bullish' ? 'Bullish' : s === 'bearish' ? 'Bearish' : 'Neutral';

    let verdictText = '⚡ NEUTRAL';
    let verdictType = 'neutral';
    let verdictConf = '';
    let verdictBadge = 'HOLD / WAIT';

    if (aiData) {
        if (aiData.final_recommendation?.includes('STRONG BUY')) {
            verdictText = '🟢 STRONG BUY'; verdictType = 'bullish';
            verdictConf = `ML Verified · ${aiData.rule_description}`; verdictBadge = 'STRONG BUY';
        } else if (aiData.final_recommendation?.includes('AVOID')) {
            verdictText = '🔴 AVOID — BULL TRAP'; verdictType = 'bearish';
            verdictConf = `Anomaly Detected · ${aiData.rule_description}`; verdictBadge = 'AVOID';
        } else if (aiData.rule_signal === -1) {
            verdictText = '🔴 SELL'; verdictType = 'bearish';
            verdictConf = aiData.rule_description; verdictBadge = 'SELL';
        } else {
            verdictText = '⚡ WAIT — Unconfirmed'; verdictType = 'neutral';
            verdictConf = aiData.rule_description; verdictBadge = 'HOLD / WAIT';
        }
    }

    const fibGradients = [
        'rgba(34,197,94,0.15)', 'rgba(96,165,245,0.15)', 'rgba(96,165,245,0.25)',
        'rgba(99,102,241,0.3)', 'rgba(99,102,241,0.45)', 'rgba(99,102,241,0.6)'
    ];

    const overviewCards = [
        {
            label: 'Daily Trend',
            value: ta.trend.daily,
            tone: ta.trend.daily.includes('Bullish') ? 'bull' : ta.trend.daily.includes('Bearish') ? 'bear' : 'neutral',
            detail: ta.trend.monthly
        },
        {
            label: 'RSI Regime',
            value: ta.rsi.value ? `${ta.rsi.value}` : 'N/A',
            tone: ta.rsi.value > 70 ? 'bear' : ta.rsi.value < 40 ? 'bull' : 'neutral',
            detail: ta.rsi.interpretation
        },
        {
            label: 'MACD Status',
            value: ta.macd.cross === 'bullish' ? 'Bullish crossover' : ta.macd.cross === 'bearish' ? 'Bearish crossover' : 'Neutral',
            tone: ta.macd.cross === 'bullish' ? 'bull' : ta.macd.cross === 'bearish' ? 'bear' : 'neutral',
            detail: ta.macd.interpretation
        },
        {
            label: 'Volume Conviction',
            value: ta.volume.trend === 'high' ? 'High conviction' : ta.volume.trend === 'low' ? 'Low conviction' : 'Average volume',
            tone: ta.volume.sellers_fading ? 'bull' : ta.volume.trend === 'low' ? 'bear' : 'neutral',
            detail: ta.volume.interpretation
        }
    ];

    return (
        <div className="dashboard">
            {/* Nav */}
            <div className="dash-nav">
                <Link to="/" className="back-link">← Back to Home</Link>
                <button onClick={handleLogout} className="logout-btn">Logout</button>
            </div>

            {/* Header */}
            <div className="dash-header">
                <div className="stock-info">
                    <h1>{ta.name}</h1>
                    <div className="stock-meta">
                        NSE: {ticker.replace('.NS', '')} &nbsp;·&nbsp; {ta.sector} &nbsp;·&nbsp; {ta.date}
                    </div>
                </div>
                <div className="price-area">
                    <div className="price-value">₹{ta.price?.toLocaleString()}</div>
                    <div className={`price-change ${ta.daily_change >= 0 ? 'up' : 'down'}`}>
                        {ta.daily_change >= 0 ? '▲' : '▼'} {ta.daily_change >= 0 ? '+' : ''}{ta.daily_change} ({ta.daily_change_pct}%)
                    </div>
                    <div className="price-range">52W: ₹{ta.w52_low?.toLocaleString()} – ₹{ta.w52_high?.toLocaleString()}</div>
                </div>
            </div>

            <div className="dash-divider"><hr /></div>

            {/* Verdict */}
            <div className="verdict-card">
                <div className={`verdict-inner ${verdictType}`}>
                    <div>
                        <div className="verdict-label">Neuro-Symbolic Verdict</div>
                        <div className="verdict-text">{verdictText}</div>
                        <div className="verdict-conf">{verdictConf}</div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                        {ta.confidence && (
                            <div style={{ textAlign: 'center' }}>
                                <div style={{
                                    fontSize: '36px', fontWeight: 800, letterSpacing: '-0.02em',
                                    background: ta.confidence.score >= 60 ? 'linear-gradient(135deg, #34d399, #22c55e)' :
                                               ta.confidence.score >= 40 ? 'linear-gradient(135deg, #fbbf24, #f59e0b)' :
                                               'linear-gradient(135deg, #f87171, #ef4444)',
                                    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'
                                }}>
                                    {ta.confidence.score}%
                                </div>
                                <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                                    Confidence
                                </div>
                            </div>
                        )}
                        <span className="verdict-badge">{verdictBadge}</span>
                    </div>
                </div>
            </div>

            {aiUnavailable && (
                <div className="ai-note">
                    AI anomaly verification is temporarily unavailable, so this view is showing the technical dashboard only.
                </div>
            )}

            <div className="overview-grid">
                {overviewCards.map((card) => (
                    <div key={card.label} className={`overview-card ${card.tone}`}>
                        <div className="overview-label">{card.label}</div>
                        <div className="overview-value">{card.value}</div>
                        <div className="overview-detail">{card.detail}</div>
                    </div>
                ))}
            </div>

            <div className="dash-content">

                {/* Chart */}
                <div className="sec-title">Interactive Chart</div>
                <div className="chart-wrapper">
                    <StockChart ticker={ticker} />
                </div>

                {/* Trend + S/R */}
                <div className="sec-title">Trend Analysis — Multi-Timeframe</div>
                <div className="grid-2">
                    <div className="glass-card">
                        <h3>Trend Direction</h3>
                        {[
                            ['Daily', ta.trend.daily],
                            ['Weekly', ta.trend.weekly],
                            ['Monthly', ta.trend.monthly],
                            ['1-Year Return', `${ta.trend.one_year_return >= 0 ? '+' : ''}${ta.trend.one_year_return}%`]
                        ].map(([k, v]) => (
                            <div className="data-row" key={k}>
                                <span className="label">{k}</span>
                                <span className={`value ${
                                    v.toString().includes('Bullish') || v.toString().startsWith('+') ? 'text-green' :
                                    v.toString().includes('Bearish') || v.toString().startsWith('-') ? 'text-red' : 'text-muted'
                                }`}>{v}</span>
                            </div>
                        ))}
                    </div>
                    <div className="glass-card">
                        <h3>Support & Resistance</h3>
                        {[
                            ['Strong Resistance', ta.support_resistance.strong_resistance, 'text-red'],
                            ['Resistance', ta.support_resistance.resistance, 'text-red'],
                            ['Support 1', ta.support_resistance.support_1, 'text-green'],
                            ['Support 2', ta.support_resistance.support_2, 'text-green'],
                            ['Strong Support', ta.support_resistance.strong_support, 'text-green']
                        ].map(([k, v, c]) => (
                            <div className="data-row" key={k}>
                                <span className="label">{k}</span>
                                <span className={`value ${c}`}>{v}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Moving Averages */}
                <div className="sec-title">Moving Average Analysis</div>
                <div className="glass-card" style={{ marginBottom: 16 }}>
                    <h3>MA Crossover Signals — ₹{ta.price?.toLocaleString()}</h3>
                    {Object.entries(ta.moving_averages.values).map(([key, val]) => val && (
                        <div className="ma-row" key={key}>
                            <div className="ma-name">{key.replace('MA_', '')}-Day</div>
                            <div className="ma-desc">₹{val?.toLocaleString()} — price {ta.price > val ? 'above' : 'below'}</div>
                            <span className={`ma-badge ${badgeCls(ta.moving_averages.signals[key])}`}>
                                {lbl(ta.moving_averages.signals[key])}
                            </span>
                        </div>
                    ))}
                    <div className="info-note">
                        {ta.scorecard.ma_stack === 'bullish'
                            ? '50-DMA is above 200-DMA — golden cross alignment. No death cross in sight.'
                            : ta.scorecard.ma_stack === 'bearish'
                                ? 'Moving average death cross detected. 50-DMA below 200-DMA.'
                                : 'Moving averages in transition. Awaiting clear directional signal.'}
                    </div>
                </div>

                {/* Momentum Indicators */}
                <div className="sec-title">Momentum Indicators</div>
                <div className="grid-2">
                    {/* RSI */}
                    <div className="glass-card">
                        <h3>RSI (14-day)</h3>
                        <div>
                            <span className="rsi-big" style={{
                                color: ta.rsi.value > 70 ? '#f87171' : ta.rsi.value < 30 ? '#34d399' : '#a5b4fc'
                            }}>{ta.rsi.value || 'N/A'}</span>
                            <span className="rsi-max"> / 100</span>
                        </div>
                        <div className="progress-track">
                            <div className="progress-bar" style={{
                                width: `${ta.rsi.value || 0}%`,
                                background: ta.rsi.value > 70 ? '#f87171' : ta.rsi.value < 30 ? '#34d399' : '#6366f1'
                            }}></div>
                        </div>
                        <div className="rsi-labels">
                            <span>Oversold 30</span><span>Neutral</span><span>Overbought 70</span>
                        </div>
                        <div className="info-note">{ta.rsi.interpretation}</div>
                    </div>

                    {/* MACD */}
                    <div className="glass-card">
                        <h3>MACD</h3>
                        {[
                            ['Signal', ta.macd.interpretation, clr(ta.macd.cross)],
                            ['MACD Line', ta.macd.line, ''],
                            ['Signal Line', ta.macd.signal, ''],
                            ['Histogram', `${ta.macd.histogram} (${ta.macd.hist_direction})`, ta.macd.histogram > 0 ? 'text-green' : 'text-red']
                        ].map(([k, v, c]) => (
                            <div className="data-row" key={k}>
                                <span className="label">{k}</span>
                                <span className={`value ${c}`}>{v}</span>
                            </div>
                        ))}
                    </div>

                    {/* Bollinger */}
                    <div className="glass-card">
                        <h3>Bollinger Bands</h3>
                        {[
                            ['Upper Band', `₹${ta.bollinger.upper?.toLocaleString()}`, 'text-red'],
                            ['Middle (20MA)', `₹${ta.bollinger.middle?.toLocaleString()}`, 'text-muted'],
                            ['Lower Band', `₹${ta.bollinger.lower?.toLocaleString()}`, 'text-green']
                        ].map(([k, v, c]) => (
                            <div className="data-row" key={k}>
                                <span className="label">{k}</span>
                                <span className={`value ${c}`}>{v}</span>
                            </div>
                        ))}
                        <div className="info-note">{ta.bollinger.interpretation}</div>
                    </div>

                    {/* Volume */}
                    <div className="glass-card">
                        <h3>Volume Analysis</h3>
                        {[
                            ['Current Volume', ta.volume.current?.toLocaleString(), ''],
                            ['20-Day Avg', ta.volume.avg_20?.toLocaleString(), ''],
                            ['Sellers Fading', ta.volume.sellers_fading ? 'Yes ✓' : 'No ✗', ta.volume.sellers_fading ? 'text-green' : 'text-red']
                        ].map(([k, v, c]) => (
                            <div className="data-row" key={k}>
                                <span className="label">{k}</span>
                                <span className={`value ${c}`}>{v}</span>
                            </div>
                        ))}
                        <div className="info-note">{ta.volume.interpretation}</div>
                    </div>
                </div>

                {/* Fibonacci */}
                <div className="sec-title">Fibonacci Retracement</div>
                <div className="glass-card" style={{ marginBottom: 16 }}>
                    <h3>Swing: ₹{ta.w52_low?.toLocaleString()} → ₹{ta.w52_high?.toLocaleString()}</h3>
                    {ta.fibonacci && Object.entries(ta.fibonacci.levels).map(([level, price], idx) => (
                        <div className="fib-row" key={level}>
                            <span className="fib-label">
                                {level === '100.0' ? '100% (top)' : level === '0.0' ? '0% (base)' : level === '61.8' ? '61.8% ★' : `${level}%`}
                            </span>
                            <div className="fib-track" style={{ background: fibGradients[idx] || 'rgba(99,102,241,0.15)' }}>
                                <div className="fib-dot" style={{ left: `${parseFloat(level)}%` }}></div>
                            </div>
                            <span className="fib-price">₹{price?.toLocaleString()}</span>
                        </div>
                    ))}
                    <div className="info-note" style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '12px' }}>
                        Current position: {ta.fibonacci.current_position}% of 52W range.
                        {ta.fibonacci.current_position > 61.8 ? ' Above golden ratio — bullish recovery.' :
                         ta.fibonacci.current_position < 38.2 ? ' Deep pullback territory.' : ' Consolidation zone.'}
                    </div>
                </div>

                {/* Signal Scorecard */}
                <div className="sec-title">Signal Scorecard</div>
                <div className="grid-4">
                    {Object.entries(ta.scorecard).map(([key, val]) => (
                        <div className="metric-card" key={key}>
                            <div className="mc-label">{key.replace('_', ' ')}</div>
                            <div className={`mc-value ${clr(val)}`}>
                                {val === 'bullish' ? '🟢 Bullish' : val === 'bearish' ? '🔴 Bearish' : '⚪ Neutral'}
                            </div>
                        </div>
                    ))}
                </div>

                {/* ═══════ TRADE PLAN SUMMARY ═══════ */}
                {ta.trade_plan && (
                    <>
                        <div className="sec-title">Trade Plan Summary</div>

                        {/* Scenario A: Pullback Buy */}
                        <div className="glass-card" style={{ marginBottom: 16, borderColor: 'rgba(34,197,94,0.15)' }}>
                            <h3 style={{ color: '#34d399', fontSize: '13px' }}>
                                📗 Scenario A: {ta.trade_plan.scenario_a.name}
                            </h3>
                            <div className="info-note" style={{ marginTop: 0, marginBottom: 16, borderColor: 'rgba(34,197,94,0.15)', background: 'rgba(34,197,94,0.05)' }}>
                                {ta.trade_plan.scenario_a.description}
                            </div>

                            {/* Entry / SL table */}
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 2fr', gap: '8px', marginBottom: 16 }}>
                                <div style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                                    <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 4 }}>Entry</div>
                                    <div style={{ fontSize: '16px', fontWeight: 700, color: '#34d399' }}>
                                        ₹{ta.trade_plan.scenario_a.entry_low?.toLocaleString()} – ₹{ta.trade_plan.scenario_a.entry_high?.toLocaleString()}
                                    </div>
                                </div>
                                <div style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                                    <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 4 }}>Stop-Loss</div>
                                    <div style={{ fontSize: '16px', fontWeight: 700, color: '#f87171' }}>
                                        ₹{ta.trade_plan.scenario_a.stop_loss?.toLocaleString()}
                                    </div>
                                </div>
                                <div style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                                    <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 4 }}>Rationale</div>
                                    <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)' }}>{ta.trade_plan.scenario_a.entry_rationale}</div>
                                </div>
                            </div>

                            {/* Targets */}
                            {ta.trade_plan.scenario_a.targets?.map((t, i) => (
                                <div className="data-row" key={i}>
                                    <span className="label">{t.label} (+{t.pct}%)</span>
                                    <span className="value text-green">₹{t.price?.toLocaleString()}</span>
                                </div>
                            ))}

                            {/* R:R */}
                            <div style={{ display: 'flex', gap: '12px', marginTop: 16, flexWrap: 'wrap' }}>
                                {ta.trade_plan.scenario_a.reward_targets?.map((rr, i) => (
                                    <div key={i} style={{
                                        padding: '8px 16px', borderRadius: '8px',
                                        background: rr.good ? 'rgba(34,197,94,0.1)' : 'rgba(255,255,255,0.03)',
                                        border: `1px solid ${rr.good ? 'rgba(34,197,94,0.2)' : 'rgba(255,255,255,0.06)'}`,
                                        fontSize: '13px', fontWeight: 700,
                                        color: rr.good ? '#34d399' : 'rgba(255,255,255,0.4)'
                                    }}>
                                        {rr.label}: <span style={{ fontFamily: "'JetBrains Mono', monospace" }}>{rr.value}</span>
                                        {rr.good && ' ✅'}
                                    </div>
                                ))}
                                <div style={{
                                    padding: '8px 16px', borderRadius: '8px',
                                    background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)',
                                    fontSize: '13px', color: 'rgba(255,255,255,0.4)'
                                }}>
                                    Risk: ₹{ta.trade_plan.scenario_a.risk_per_share}/share
                                </div>
                            </div>
                        </div>

                        {/* Scenario B: Breakout Buy */}
                        <div className="glass-card" style={{ marginBottom: 16, borderColor: 'rgba(99,102,241,0.15)' }}>
                            <h3 style={{ color: '#818cf8', fontSize: '13px' }}>
                                📘 Scenario B: {ta.trade_plan.scenario_b.name}
                            </h3>
                            <div className="info-note" style={{ marginTop: 0, marginBottom: 16, borderColor: 'rgba(99,102,241,0.15)', background: 'rgba(99,102,241,0.05)' }}>
                                {ta.trade_plan.scenario_b.description}
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '10px' }}>
                                <div style={{ padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                                    <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 4 }}>Entry</div>
                                    <div style={{ fontSize: '15px', fontWeight: 700, color: '#818cf8' }}>
                                        ₹{ta.trade_plan.scenario_b.entry_low?.toLocaleString()} – ₹{ta.trade_plan.scenario_b.entry_high?.toLocaleString()}
                                    </div>
                                </div>
                                <div style={{ padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                                    <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 4 }}>Stop-Loss</div>
                                    <div style={{ fontSize: '15px', fontWeight: 700, color: '#f87171' }}>₹{ta.trade_plan.scenario_b.stop_loss?.toLocaleString()}</div>
                                </div>
                                <div style={{ padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                                    <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 4 }}>Target (+{ta.trade_plan.scenario_b.target_pct}%)</div>
                                    <div style={{ fontSize: '15px', fontWeight: 700, color: '#34d399' }}>₹{ta.trade_plan.scenario_b.target?.toLocaleString()}</div>
                                </div>
                                <div style={{ padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                                    <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 4 }}>R:R Ratio</div>
                                    <div style={{ fontSize: '15px', fontWeight: 700, color: ta.trade_plan.scenario_b.rr_good ? '#34d399' : 'rgba(255,255,255,0.5)' }}>
                                        {ta.trade_plan.scenario_b.rr} {ta.trade_plan.scenario_b.rr_good && '✅'}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* No-Trade Zone */}
                        <div className="glass-card" style={{ marginBottom: 16, borderColor: 'rgba(239,68,68,0.2)', background: 'rgba(239,68,68,0.04)' }}>
                            <h3 style={{ color: '#f87171', fontSize: '13px' }}>
                                ❌ No-Trade Zone
                            </h3>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
                                <div style={{
                                    fontSize: '20px', fontWeight: 800, color: '#f87171',
                                    fontFamily: "'JetBrains Mono', monospace"
                                }}>
                                    ₹{ta.trade_plan.no_trade_zone.low?.toLocaleString()} – ₹{ta.trade_plan.no_trade_zone.high?.toLocaleString()}
                                </div>
                                <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)', flex: 1, minWidth: '200px' }}>
                                    {ta.trade_plan.no_trade_zone.reason}
                                </div>
                            </div>
                        </div>
                    </>
                )}

                {/* ═══════ OVERALL CONFIDENCE RATING ═══════ */}
                {ta.confidence && (
                    <>
                        <div className="sec-title">Overall Confidence Rating</div>
                        <div className="glass-card" style={{
                            borderColor: ta.confidence.score >= 60 ? 'rgba(34,197,94,0.2)' :
                                         ta.confidence.score >= 40 ? 'rgba(251,191,36,0.2)' : 'rgba(239,68,68,0.2)',
                            marginBottom: 16
                        }}>
                            {/* Big rating header */}
                            <div style={{
                                textAlign: 'center', padding: '24px 0 20px',
                                borderBottom: '1px solid rgba(255,255,255,0.06)', marginBottom: 20
                            }}>
                                <div style={{ fontSize: '14px', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.15em', marginBottom: 8 }}>
                                    Overall Rating
                                </div>
                                <div style={{
                                    fontSize: '28px', fontWeight: 800, letterSpacing: '-0.02em',
                                    background: ta.confidence.score >= 60 ? 'linear-gradient(135deg, #34d399, #22c55e)' :
                                               ta.confidence.score >= 40 ? 'linear-gradient(135deg, #fbbf24, #f59e0b)' :
                                               'linear-gradient(135deg, #f87171, #ef4444)',
                                    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'
                                }}>
                                    {ta.confidence.emoji} {ta.confidence.rating}
                                </div>
                                <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.35)', marginTop: 6 }}>
                                    {ta.confidence.description}
                                </div>
                            </div>

                            {/* Rating bars */}
                            {Object.entries(ta.confidence.bars).map(([key, bar]) => (
                                <div key={key} style={{
                                    display: 'flex', alignItems: 'center', gap: '12px',
                                    padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.03)'
                                }}>
                                    <div style={{
                                        minWidth: '100px', fontSize: '12px', fontWeight: 600,
                                        color: key === 'strong_buy' ? '#34d399' :
                                               key === 'buy' ? '#4ade80' :
                                               key === 'neutral' ? '#fbbf24' :
                                               key === 'sell' ? '#fb923c' : '#f87171',
                                        textTransform: 'capitalize'
                                    }}>
                                        {key.replace('_', ' ')}
                                    </div>
                                    <div style={{ flex: 1, display: 'flex', gap: '2px' }}>
                                        {Array.from({ length: 10 }, (_, i) => (
                                            <div key={i} style={{
                                                width: '100%', height: '8px', borderRadius: '2px',
                                                background: i < bar.value
                                                    ? (key === 'strong_buy' || key === 'buy' ? '#34d399' :
                                                       key === 'neutral' ? '#fbbf24' : '#f87171')
                                                    : 'rgba(255,255,255,0.04)',
                                                transition: 'background 0.3s'
                                            }}></div>
                                        ))}
                                    </div>
                                    <div style={{
                                        minWidth: '180px', fontSize: '11px',
                                        color: 'rgba(255,255,255,0.3)', textAlign: 'right',
                                        fontFamily: "'JetBrains Mono', monospace"
                                    }}>
                                        {bar.label}
                                    </div>
                                </div>
                            ))}

                            {/* Confidence score bar */}
                            <div style={{ marginTop: 20, textAlign: 'center' }}>
                                <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.25)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8 }}>
                                    Technical Confidence Score
                                </div>
                                <div style={{
                                    height: '12px', borderRadius: '6px',
                                    background: 'rgba(255,255,255,0.04)', overflow: 'hidden',
                                    position: 'relative'
                                }}>
                                    <div style={{
                                        height: '100%', borderRadius: '6px',
                                        width: `${ta.confidence.score}%`,
                                        background: ta.confidence.score >= 60
                                            ? 'linear-gradient(90deg, #22c55e, #34d399)'
                                            : ta.confidence.score >= 40
                                                ? 'linear-gradient(90deg, #f59e0b, #fbbf24)'
                                                : 'linear-gradient(90deg, #ef4444, #f87171)',
                                        transition: 'width 1s ease'
                                    }}></div>
                                </div>
                                <div style={{
                                    display: 'flex', justifyContent: 'space-between', marginTop: 4,
                                    fontSize: '10px', color: 'rgba(255,255,255,0.15)',
                                    fontFamily: "'JetBrains Mono', monospace"
                                }}>
                                    <span>0</span>
                                    <span style={{ fontWeight: 700, fontSize: '14px', color: 'rgba(255,255,255,0.6)' }}>
                                        {ta.confidence.score}%
                                    </span>
                                    <span>100</span>
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </div>

            {/* Footnote */}
            <div className="dash-footnote">
                ⚠ Generated by the Neuro-Symbolic Trading System v2.1. This report is for informational purposes only and does not constitute financial advice. Always conduct your own due diligence.
            </div>
        </div>
    );
};

export default Dashboard;
