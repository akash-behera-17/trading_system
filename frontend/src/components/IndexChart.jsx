import React, { useEffect, useRef, useState, useCallback } from 'react';
import { createChart, AreaSeries, HistogramSeries } from 'lightweight-charts';
import { api } from '../lib/api';

const PERIODS = [
    { label: '1M', value: '1mo' },
    { label: '6M', value: '6mo' },
    { label: '1Y', value: '1y' },
    { label: '3Y', value: '3y' },
    { label: '5Y', value: '5y' },
];

const IndexChart = ({ ticker, title, accentColor = '#6366f1' }) => {
    const containerRef = useRef(null);
    const chartRef = useRef(null);
    const [activePeriod, setActivePeriod] = useState('1y');
    const [chartData, setChartData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [latestPrice, setLatestPrice] = useState(null);
    const [change, setChange] = useState(null);

    const fetchData = useCallback(async (period) => {
        setLoading(true);
        try {
            const res = await api.get('/api/stocks/chart-data', { params: { ticker, period } });
            setChartData(res.data);
            const ohlcv = res.data.ohlcv;
            if (ohlcv?.length >= 2) {
                const last = ohlcv[ohlcv.length - 1].close;
                const prev = ohlcv[ohlcv.length - 2].close;
                const chg = last - prev;
                const chgPct = ((chg / prev) * 100).toFixed(2);
                setLatestPrice(last);
                setChange({ value: chg.toFixed(2), pct: chgPct, up: chg >= 0 });
            }
        } catch (fetchError) {
            console.error(`Failed to load ${ticker}:`, fetchError);
        } finally {
            setLoading(false);
        }
    }, [ticker]);

    useEffect(() => { fetchData(activePeriod); }, [activePeriod, fetchData]);

    useEffect(() => {
        if (!chartData || !containerRef.current) return;

        if (chartRef.current) {
            chartRef.current.remove();
            chartRef.current = null;
        }

        const container = containerRef.current;
        const chart = createChart(container, {
            width: container.clientWidth,
            height: 260,
            layout: {
                background: { color: 'transparent' },
                textColor: 'rgba(255,255,255,0.3)',
                fontSize: 10,
                fontFamily: "Inter, system-ui, sans-serif",
            },
            grid: {
                vertLines: { color: 'rgba(255,255,255,0.02)' },
                horzLines: { color: 'rgba(255,255,255,0.02)' },
            },
            crosshair: {
                mode: 0,
                vertLine: { color: `${accentColor}55`, labelBackgroundColor: accentColor },
                horzLine: { color: `${accentColor}55`, labelBackgroundColor: accentColor },
            },
            rightPriceScale: { borderColor: 'rgba(255,255,255,0.04)' },
            timeScale: { borderColor: 'rgba(255,255,255,0.04)', timeVisible: false },
            handleScroll: false,
            handleScale: false,
        });

        chartRef.current = chart;

        // area series
        const areaSeries = chart.addSeries(AreaSeries, {
            topColor: `${accentColor}30`,
            bottomColor: `${accentColor}05`,
            lineColor: accentColor,
            lineWidth: 2,
            crosshairMarkerBackgroundColor: accentColor,
            priceFormat: { type: 'price', precision: 2 },
        });
        areaSeries.setData(chartData.ohlcv.map(d => ({ time: d.time, value: d.close })));

        // volume
        if (chartData.volume?.length) {
            const volSeries = chart.addSeries(HistogramSeries, {
                priceFormat: { type: 'volume' },
                priceScaleId: 'vol',
            });
            chart.priceScale('vol').applyOptions({
                scaleMargins: { top: 0.85, bottom: 0 }, visible: false,
            });
            volSeries.setData(chartData.volume);
        }

        chart.timeScale().fitContent();

        const handleResize = () => {
            if (chartRef.current && container) {
                chartRef.current.applyOptions({ width: container.clientWidth });
            }
        };
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            if (chartRef.current) { chartRef.current.remove(); chartRef.current = null; }
        };
    }, [chartData, accentColor]);

    return (
        <div style={{
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: '16px', overflow: 'hidden',
        }}>
            {/* Header */}
            <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '16px 20px 0',
            }}>
                <div>
                    <div style={{ fontSize: '16px', fontWeight: 800, letterSpacing: '-0.01em' }}>{title}</div>
                    {latestPrice && (
                        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: 4 }}>
                            <span style={{ fontSize: '22px', fontWeight: 800, letterSpacing: '-0.02em' }}>
                                {latestPrice.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </span>
                            {change && (
                                <span style={{
                                    fontSize: '13px', fontWeight: 700,
                                    color: change.up ? '#22c55e' : '#ef4444'
                                }}>
                                    {change.up ? '▲' : '▼'} {change.up ? '+' : ''}{change.value} ({change.pct}%)
                                </span>
                            )}
                        </div>
                    )}
                </div>
                {/* Period pills */}
                <div style={{ display: 'flex', gap: '3px' }}>
                    {PERIODS.map(p => (
                        <button key={p.value} onClick={() => setActivePeriod(p.value)} style={{
                            padding: '4px 10px', borderRadius: '6px', border: 'none', cursor: 'pointer',
                            fontSize: '11px', fontWeight: 600, transition: 'all 0.2s',
                            background: activePeriod === p.value ? accentColor : 'rgba(255,255,255,0.04)',
                            color: activePeriod === p.value ? '#fff' : 'rgba(255,255,255,0.3)',
                        }}>{p.label}</button>
                    ))}
                </div>
            </div>

            {/* Chart area */}
            <div ref={containerRef} style={{ position: 'relative', minHeight: 260 }}>
                {loading && (
                    <div style={{
                        position: 'absolute', inset: 0, display: 'flex',
                        alignItems: 'center', justifyContent: 'center',
                        background: 'rgba(10,10,15,0.7)', zIndex: 10
                    }}>
                        <div style={{
                            width: 24, height: 24, border: '2px solid rgba(255,255,255,0.06)',
                            borderTop: `2px solid ${accentColor}`, borderRadius: '50%',
                            animation: 'spin 1s linear infinite'
                        }}></div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default IndexChart;
