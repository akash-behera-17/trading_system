import React, { useEffect, useState, useRef, Suspense } from 'react';
import SearchBar from '../components/SearchBar';
import IndexChart from '../components/IndexChart';
import NeuralNetworkScene from '../components/NeuralNetworkScene';
import { TrendingUp, TrendingDown, ShieldAlert, BarChart3, ArrowDown, Zap, Brain, ChevronRight } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const Home = () => {
    const { token, logout } = useAuth();
    const navigate = useNavigate();
    const searchRef = useRef(null);
    const [movers, setMovers] = useState(null);
    const [moversLoading, setMoversLoading] = useState(true);

    useEffect(() => {
        const fetchMovers = async () => {
            try {
                setMoversLoading(true);
                const res = await axios.get('http://localhost:5000/api/stocks/market-movers');
                setMovers(res.data);
            } catch (err) {
                console.error('Failed to fetch market movers:', err);
            } finally {
                setMoversLoading(false);
            }
        };
        fetchMovers();
    }, []);



    const scrollToSearch = () => {
        searchRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const handleStockClick = (ticker) => {
        if (!token) {
            navigate('/login', { state: { from: `/dashboard?ticker=${ticker}` } });
        } else {
            navigate(`/dashboard?ticker=${ticker}`);
        }
    };

    return (
        <div style={{ minHeight: '100vh', background: '#0a0a0f', color: '#ffffff' }}>

            {/* ═══════════════════════ TOP NAV ═══════════════════════ */}
            <header style={{
                position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
                background: 'rgba(10, 10, 15, 0.85)', backdropFilter: 'blur(20px)',
                borderBottom: '1px solid rgba(255,255,255,0.06)',
                padding: '16px 32px',
                display: 'flex', justifyContent: 'space-between', alignItems: 'center'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Brain style={{ color: '#6366f1', width: 28, height: 28 }} />
                    <span style={{ fontSize: '20px', fontWeight: 800, letterSpacing: '-0.02em' }}>
                        NeuroTrade<span style={{ color: '#6366f1' }}>.ai</span>
                    </span>
                </div>
                <nav style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    {token ? (
                        <button onClick={logout} style={{
                            fontSize: '13px', fontWeight: 600, color: '#ef4444',
                            background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
                            padding: '8px 18px', borderRadius: '8px', cursor: 'pointer',
                            transition: 'all 0.2s'
                        }}>
                            Logout
                        </button>
                    ) : (
                        <Link to="/login" style={{
                            fontSize: '13px', fontWeight: 600, color: '#a5b4fc',
                            background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.3)',
                            padding: '8px 18px', borderRadius: '8px', textDecoration: 'none',
                            transition: 'all 0.2s'
                        }}>
                            Login / Sign In
                        </Link>
                    )}
                </nav>
            </header>

            {/* ═══════════════════════ SECTION 1: HERO ═══════════════════════ */}
            <section style={{
                minHeight: '100vh', display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center', textAlign: 'center',
                padding: '120px 24px 80px',
                background: 'radial-gradient(ellipse at 50% 0%, rgba(99,102,241,0.15) 0%, transparent 60%)',
                position: 'relative', overflow: 'hidden'
            }}>
                {/* ── 3D Neural Network Animation (background layer) ── */}
                <Suspense fallback={null}>
                    <NeuralNetworkScene />
                </Suspense>

                {/* Gradient overlay so text stays readable */}
                <div style={{
                    position: 'absolute', inset: 0, zIndex: 1,
                    background: 'radial-gradient(circle at 50% 50%, transparent 30%, rgba(10,10,15,0.7) 70%)',
                    pointerEvents: 'none'
                }}></div>

                {/* Animated grid background */}
                <div style={{
                    position: 'absolute', inset: 0, opacity: 0.04, zIndex: 1,
                    backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
                    backgroundSize: '60px 60px', pointerEvents: 'none'
                }}></div>

                {/* Hero content (above 3D scene) */}
                <div style={{ position: 'relative', zIndex: 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <div style={{
                        display: 'inline-flex', alignItems: 'center', gap: '8px',
                        background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.3)',
                        borderRadius: '999px', padding: '6px 16px', marginBottom: '32px',
                        fontSize: '13px', color: '#a5b4fc', fontWeight: 600,
                        backdropFilter: 'blur(8px)'
                    }}>
                        <Zap style={{ width: 14, height: 14 }} /> Neuro-Symbolic AI Engine v2.1
                    </div>

                    <h1 style={{
                        fontSize: 'clamp(2.5rem, 6vw, 4.5rem)', fontWeight: 900,
                        lineHeight: 1.1, letterSpacing: '-0.04em', maxWidth: '800px',
                        margin: '0 0 24px',
                        textShadow: '0 0 60px rgba(99,102,241,0.3)'
                    }}>
                        Neuro-Symbolic{' '}
                        <span style={{
                            background: 'linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa)',
                            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'
                        }}>
                            Trading System
                        </span>
                    </h1>

                    <p style={{
                        fontSize: '18px', color: 'rgba(255,255,255,0.55)', maxWidth: '560px',
                        lineHeight: 1.7, margin: '0 0 40px',
                        textShadow: '0 2px 10px rgba(0,0,0,0.5)'
                    }}>
                        Combining expert rule-based strategy with LSTM Autoencoder anomaly detection
                        to filter bull traps and validate trade setups on Indian markets.
                    </p>

                    <button onClick={scrollToSearch} style={{
                        background: 'linear-gradient(135deg, #6366f1, #4f46e5)',
                        color: '#fff', border: 'none', padding: '16px 40px',
                        borderRadius: '12px', fontSize: '16px', fontWeight: 700,
                        cursor: 'pointer', letterSpacing: '0.02em',
                        boxShadow: '0 0 40px rgba(99,102,241,0.4)',
                        transition: 'transform 0.2s, box-shadow 0.2s',
                        display: 'flex', alignItems: 'center', gap: '10px',
                        position: 'relative', zIndex: 3
                    }}
                        onMouseEnter={(e) => { e.target.style.transform = 'translateY(-2px)'; e.target.style.boxShadow = '0 0 60px rgba(99,102,241,0.5)'; }}
                        onMouseLeave={(e) => { e.target.style.transform = 'translateY(0)'; e.target.style.boxShadow = '0 0 40px rgba(99,102,241,0.4)'; }}
                    >
                        Get Started <ChevronRight style={{ width: 18, height: 18 }} />
                    </button>
                </div>

                <div style={{
                    position: 'absolute', bottom: '40px', zIndex: 2,
                    animation: 'bounce 2s infinite'
                }}>
                    <ArrowDown style={{ width: 24, height: 24, color: 'rgba(255,255,255,0.2)' }} />
                </div>
            </section>

            {/* ═══════════════════════ SECTION 2: MARKET OVERVIEW ═══════════════════════ */}
            <section style={{
                padding: '80px 24px',
                background: 'linear-gradient(180deg, #0a0a0f 0%, #0f0f18 100%)'
            }}>
                <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                    <h2 style={{
                        fontSize: '12px', fontWeight: 700, textTransform: 'uppercase',
                        letterSpacing: '0.15em', color: 'rgba(255,255,255,0.4)',
                        marginBottom: '12px'
                    }}>
                        Market Overview
                    </h2>
                    <h3 style={{
                        fontSize: '28px', fontWeight: 800, letterSpacing: '-0.02em',
                        marginBottom: '32px', marginTop: 0
                    }}>
                        Nifty 50 & Sensex <span style={{ color: '#6366f1' }}>Live</span>
                    </h3>

                    <div style={{
                        display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
                        gap: '20px'
                    }}>
                        <IndexChart ticker="^NSEI" title="NIFTY 50" accentColor="#6366f1" />
                        <IndexChart ticker="^BSESN" title="SENSEX" accentColor="#8b5cf6" />
                    </div>
                </div>
            </section>

            {/* ═══════════════════════ SECTION 3: TOP GAINERS & LOSERS ═══════════════════════ */}
            <section style={{
                padding: '80px 24px',
                background: '#0f0f18'
            }}>
                <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                    <h2 style={{
                        fontSize: '12px', fontWeight: 700, textTransform: 'uppercase',
                        letterSpacing: '0.15em', color: 'rgba(255,255,255,0.4)',
                        marginBottom: '12px'
                    }}>
                        Today's Market Movers
                    </h2>
                    <h3 style={{
                        fontSize: '28px', fontWeight: 800, letterSpacing: '-0.02em',
                        marginBottom: '32px', marginTop: 0
                    }}>
                        Top <span style={{ color: '#22c55e' }}>Gainers</span> & <span style={{ color: '#ef4444' }}>Losers</span>
                    </h3>

                    {moversLoading ? (
                        <div style={{ textAlign: 'center', padding: '60px 0', color: 'rgba(255,255,255,0.3)' }}>
                            <div style={{
                                width: 32, height: 32, border: '3px solid rgba(255,255,255,0.1)',
                                borderTop: '3px solid #6366f1', borderRadius: '50%',
                                animation: 'spin 1s linear infinite', margin: '0 auto 12px'
                            }}></div>
                            Loading market data...
                        </div>
                    ) : movers ? (
                        <div style={{
                            display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
                            gap: '20px'
                        }}>
                            {/* Gainers */}
                            <div style={{
                                background: 'rgba(34, 197, 94, 0.04)',
                                border: '1px solid rgba(34, 197, 94, 0.15)',
                                borderRadius: '16px', padding: '24px'
                            }}>
                                <div style={{
                                    display: 'flex', alignItems: 'center', gap: '8px',
                                    marginBottom: '20px'
                                }}>
                                    <TrendingUp style={{ color: '#22c55e', width: 20, height: 20 }} />
                                    <span style={{ fontSize: '14px', fontWeight: 700, color: '#22c55e', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                                        Top Gainers
                                    </span>
                                </div>
                                {movers.gainers?.map((stock, i) => (
                                    <div key={i} onClick={() => handleStockClick(stock.ticker)} style={{
                                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                        padding: '12px 0', borderBottom: i < movers.gainers.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none',
                                        cursor: 'pointer', transition: 'opacity 0.2s'
                                    }}
                                        onMouseEnter={e => e.currentTarget.style.opacity = '0.7'}
                                        onMouseLeave={e => e.currentTarget.style.opacity = '1'}
                                    >
                                        <div>
                                            <div style={{ fontSize: '14px', fontWeight: 600 }}>{stock.name.length > 25 ? stock.name.substring(0, 25) + '...' : stock.name}</div>
                                            <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)', fontFamily: "'Courier New', monospace" }}>{stock.ticker}</div>
                                        </div>
                                        <div style={{ textAlign: 'right' }}>
                                            <div style={{ fontSize: '14px', fontWeight: 700 }}>₹{stock.price?.toLocaleString()}</div>
                                            <div style={{ fontSize: '13px', fontWeight: 700, color: '#22c55e' }}>+{stock.change_pct}%</div>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Losers */}
                            <div style={{
                                background: 'rgba(239, 68, 68, 0.04)',
                                border: '1px solid rgba(239, 68, 68, 0.15)',
                                borderRadius: '16px', padding: '24px'
                            }}>
                                <div style={{
                                    display: 'flex', alignItems: 'center', gap: '8px',
                                    marginBottom: '20px'
                                }}>
                                    <TrendingDown style={{ color: '#ef4444', width: 20, height: 20 }} />
                                    <span style={{ fontSize: '14px', fontWeight: 700, color: '#ef4444', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                                        Top Losers
                                    </span>
                                </div>
                                {movers.losers?.map((stock, i) => (
                                    <div key={i} onClick={() => handleStockClick(stock.ticker)} style={{
                                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                        padding: '12px 0', borderBottom: i < movers.losers.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none',
                                        cursor: 'pointer', transition: 'opacity 0.2s'
                                    }}
                                        onMouseEnter={e => e.currentTarget.style.opacity = '0.7'}
                                        onMouseLeave={e => e.currentTarget.style.opacity = '1'}
                                    >
                                        <div>
                                            <div style={{ fontSize: '14px', fontWeight: 600 }}>{stock.name.length > 25 ? stock.name.substring(0, 25) + '...' : stock.name}</div>
                                            <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)', fontFamily: "'Courier New', monospace" }}>{stock.ticker}</div>
                                        </div>
                                        <div style={{ textAlign: 'right' }}>
                                            <div style={{ fontSize: '14px', fontWeight: 700 }}>₹{stock.price?.toLocaleString()}</div>
                                            <div style={{ fontSize: '13px', fontWeight: 700, color: '#ef4444' }}>{stock.change_pct}%</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <p style={{ color: 'rgba(255,255,255,0.3)' }}>Market data unavailable</p>
                    )}
                </div>
            </section>

            {/* ═══════════════════════ SECTION 4: SEARCH TOOL ═══════════════════════ */}
            <section ref={searchRef} style={{
                padding: '100px 24px 120px',
                background: 'linear-gradient(180deg, #0f0f18 0%, #0a0a0f 100%)',
                textAlign: 'center'
            }}>
                <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                    <div style={{
                        display: 'inline-flex', alignItems: 'center', gap: '8px',
                        background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.25)',
                        borderRadius: '999px', padding: '6px 16px', marginBottom: '24px',
                        fontSize: '12px', color: '#a5b4fc', fontWeight: 600
                    }}>
                        <ShieldAlert style={{ width: 14, height: 14 }} /> Neuro-Symbolic Analysis Engine
                    </div>

                    <h2 style={{
                        fontSize: 'clamp(1.5rem, 4vw, 2.5rem)', fontWeight: 800,
                        letterSpacing: '-0.02em', marginTop: 0, marginBottom: '16px'
                    }}>
                        Analyze Any Stock
                    </h2>
                    <p style={{
                        fontSize: '16px', color: 'rgba(255,255,255,0.4)',
                        marginBottom: '40px', lineHeight: 1.6
                    }}>
                        Enter a company name or ticker symbol to get a full Citadel-grade technical analysis
                        report with AI-powered bull trap detection.
                    </p>

                    <SearchBar />

                    {/* Feature cards */}
                    <div style={{
                        display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                        gap: '16px', marginTop: '60px', textAlign: 'left'
                    }}>
                        <div style={{
                            background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)',
                            borderRadius: '16px', padding: '24px'
                        }}>
                            <BarChart3 style={{ color: '#6366f1', width: 24, height: 24, marginBottom: '12px' }} />
                            <h4 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '8px', marginTop: 0 }}>Full Technical Analysis</h4>
                            <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)', lineHeight: 1.5, margin: 0 }}>
                                RSI, MACD, Bollinger Bands, Fibonacci, MAs — all computed in realtime.
                            </p>
                        </div>
                        <div style={{
                            background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)',
                            borderRadius: '16px', padding: '24px'
                        }}>
                            <ShieldAlert style={{ color: '#8b5cf6', width: 24, height: 24, marginBottom: '12px' }} />
                            <h4 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '8px', marginTop: 0 }}>Bull Trap Detection</h4>
                            <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)', lineHeight: 1.5, margin: 0 }}>
                                LSTM Autoencoders filter out false signals — no more chasing traps.
                            </p>
                        </div>
                        <div style={{
                            background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)',
                            borderRadius: '16px', padding: '24px'
                        }}>
                            <Brain style={{ color: '#a78bfa', width: 24, height: 24, marginBottom: '12px' }} />
                            <h4 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '8px', marginTop: 0 }}>Neuro-Symbolic AI</h4>
                            <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)', lineHeight: 1.5, margin: 0 }}>
                                Expert rules + deep learning combined for institutional-grade signals.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Keyframe animation */}
            <style>{`
                @keyframes bounce {
                    0%, 100% { transform: translateY(0); }
                    50% { transform: translateY(10px); }
                }
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    );
};

export default Home;
