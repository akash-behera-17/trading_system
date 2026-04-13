import React, { useEffect, useRef, useState, useCallback } from 'react';
import { createChart, LineSeries, AreaSeries, HistogramSeries } from 'lightweight-charts';
import { api } from '../lib/api';

const PERIODS = [
    { label: '1M', value: '1mo' },
    { label: '6M', value: '6mo' },
    { label: '1Y', value: '1y' },
    { label: '3Y', value: '3y' },
    { label: '5Y', value: '5y' },
    { label: 'Max', value: 'max' },
];

const OVERLAYS = [
    { key: 'dma50', label: '50 DMA', color: '#6366f1' },
    { key: 'dma100', label: '100 DMA', color: '#f59e0b' },
    { key: 'dma200', label: '200 DMA', color: '#ef4444' },
    { key: 'volume', label: 'Volume', color: '#34d399' },
];

const StockChart = ({ ticker }) => {
    const chartContainerRef = useRef(null);
    const chartRef = useRef(null);
    const seriesRef = useRef({});
    const [activePeriod, setActivePeriod] = useState('1y');
    const [activeOverlays, setActiveOverlays] = useState({ dma50: false, dma100: false, dma200: true, volume: true });
    const [chartData, setChartData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const fetchData = useCallback(async (period) => {
        if (!ticker) return;
        setLoading(true);
        setError('');
        try {
            const res = await api.get('/api/stocks/chart-data', { params: { ticker, period } });
            setChartData(res.data);
        } catch (fetchError) {
            console.error('Failed to load stock chart data:', fetchError);
            setError('Failed to load chart data');
        } finally {
            setLoading(false);
        }
    }, [ticker]);

    useEffect(() => {
        fetchData(activePeriod);
    }, [activePeriod, fetchData]);

    useEffect(() => {
        if (!chartData || !chartContainerRef.current) return;

        // Clean up existing
        if (chartRef.current) {
            chartRef.current.remove();
            chartRef.current = null;
            seriesRef.current = {};
        }

        const container = chartContainerRef.current;
        const chart = createChart(container, {
            width: container.clientWidth,
            height: 450,
            layout: {
                background: { color: 'transparent' },
                textColor: 'rgba(255,255,255,0.4)',
                fontSize: 11,
                fontFamily: "Inter, system-ui, sans-serif",
            },
            grid: {
                vertLines: { color: 'rgba(255,255,255,0.03)' },
                horzLines: { color: 'rgba(255,255,255,0.03)' },
            },
            crosshair: {
                mode: 0,
                vertLine: { color: 'rgba(99,102,241,0.3)', labelBackgroundColor: '#6366f1' },
                horzLine: { color: 'rgba(99,102,241,0.3)', labelBackgroundColor: '#6366f1' },
            },
            rightPriceScale: {
                borderColor: 'rgba(255,255,255,0.06)',
            },
            timeScale: {
                borderColor: 'rgba(255,255,255,0.06)',
                timeVisible: true,
                secondsVisible: false,
            },
        });

        chartRef.current = chart;

        // Price area series
        const priceSeries = chart.addSeries(AreaSeries, {
            topColor: 'rgba(99, 102, 241, 0.25)',
            bottomColor: 'rgba(99, 102, 241, 0.0)',
            lineColor: '#6366f1',
            lineWidth: 2,
            crosshairMarkerBackgroundColor: '#6366f1',
            priceFormat: { type: 'price', precision: 2 },
        });
        const priceData = chartData.ohlcv.map(d => ({ time: d.time, value: d.close }));
        priceSeries.setData(priceData);
        seriesRef.current.price = priceSeries;

        // Volume
        if (activeOverlays.volume && chartData.volume?.length) {
            const volSeries = chart.addSeries(HistogramSeries, {
                priceFormat: { type: 'volume' },
                priceScaleId: 'volume',
            });
            chart.priceScale('volume').applyOptions({
                scaleMargins: { top: 0.8, bottom: 0 },
                visible: false,
            });
            volSeries.setData(chartData.volume);
            seriesRef.current.volume = volSeries;
        }

        // DMA overlays
        const dmaConfigs = {
            dma50: { data: chartData.dma50, color: '#6366f1', title: '50 DMA' },
            dma100: { data: chartData.dma100, color: '#f59e0b', title: '100 DMA' },
            dma200: { data: chartData.dma200, color: '#ef4444', title: '200 DMA' },
        };

        Object.entries(dmaConfigs).forEach(([key, config]) => {
            if (activeOverlays[key] && config.data?.length) {
                const dmaSeries = chart.addSeries(LineSeries, {
                    color: config.color,
                    lineWidth: 1,
                    lineStyle: 2, // dashed
                    crosshairMarkerVisible: false,
                    priceLineVisible: false,
                    lastValueVisible: false,
                    title: config.title,
                });
                dmaSeries.setData(config.data);
                seriesRef.current[key] = dmaSeries;
            }
        });

        chart.timeScale().fitContent();

        // Resize handler
        const handleResize = () => {
            if (chartRef.current && container) {
                chartRef.current.applyOptions({ width: container.clientWidth });
            }
        };
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            if (chartRef.current) {
                chartRef.current.remove();
                chartRef.current = null;
            }
        };
    }, [chartData, activeOverlays]);

    const toggleOverlay = (key) => {
        setActiveOverlays(prev => ({ ...prev, [key]: !prev[key] }));
    };

    return (
        <div style={{ position: 'relative' }}>
            {/* Controls bar */}
            <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '12px 16px', flexWrap: 'wrap', gap: '8px',
                borderBottom: '1px solid rgba(255,255,255,0.06)'
            }}>
                {/* Period buttons */}
                <div style={{ display: 'flex', gap: '4px' }}>
                    {PERIODS.map(p => (
                        <button key={p.value} onClick={() => setActivePeriod(p.value)} style={{
                            padding: '6px 14px', borderRadius: '6px', border: 'none', cursor: 'pointer',
                            fontSize: '12px', fontWeight: 600, letterSpacing: '0.03em',
                            transition: 'all 0.2s',
                            background: activePeriod === p.value ? '#6366f1' : 'rgba(255,255,255,0.04)',
                            color: activePeriod === p.value ? '#fff' : 'rgba(255,255,255,0.4)',
                        }}>{p.label}</button>
                    ))}
                </div>

                {/* Overlay toggles */}
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    {OVERLAYS.map(o => (
                        <button key={o.key} onClick={() => toggleOverlay(o.key)} style={{
                            padding: '5px 12px', borderRadius: '6px', cursor: 'pointer',
                            fontSize: '11px', fontWeight: 600, transition: 'all 0.2s',
                            border: `1px solid ${activeOverlays[o.key] ? o.color : 'rgba(255,255,255,0.08)'}`,
                            background: activeOverlays[o.key] ? `${o.color}18` : 'transparent',
                            color: activeOverlays[o.key] ? o.color : 'rgba(255,255,255,0.3)',
                        }}>
                            <span style={{
                                display: 'inline-block', width: 8, height: 8, borderRadius: '50%',
                                background: activeOverlays[o.key] ? o.color : 'rgba(255,255,255,0.15)',
                                marginRight: 6, verticalAlign: 'middle'
                            }}></span>
                            {o.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Chart */}
            <div ref={chartContainerRef} style={{ position: 'relative', minHeight: 450 }}>
                {loading && (
                    <div style={{
                        position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: 'rgba(10,10,15,0.8)', zIndex: 10, borderRadius: '0 0 16px 16px'
                    }}>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{
                                width: 32, height: 32, border: '2px solid rgba(255,255,255,0.06)',
                                borderTop: '2px solid #6366f1', borderRadius: '50%',
                                animation: 'spin 1s linear infinite', margin: '0 auto 8px'
                            }}></div>
                            <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 12 }}>Loading chart...</span>
                        </div>
                    </div>
                )}
                {error && (
                    <div style={{
                        position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
                        color: '#f87171', fontSize: 13
                    }}>{error}</div>
                )}
            </div>
        </div>
    );
};

export default StockChart;
