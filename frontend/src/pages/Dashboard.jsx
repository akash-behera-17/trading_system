import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';
import {
    LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer
} from 'recharts';
import { Activity, Target, ShieldAlert, BadgeCheck, XCircle } from 'lucide-react';

const Dashboard = () => {
    const [searchParams] = useSearchParams();
    const ticker = searchParams.get('ticker');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchDashboard = async () => {
            try {
                setLoading(true);
                const res = await axios.get(`http://localhost:5000/api/stocks/dashboard?ticker=${ticker}`);
                setData(res.data);
            } catch (err) {
                setError(err.response?.data?.error || 'Failed to load dashboard data');
            } finally {
                setLoading(false);
            }
        };
        if (ticker) fetchDashboard();
    }, [ticker]);

    if (!ticker) return <div className="p-8 text-center text-gray-500">No ticker selected. Please return to Home to search.</div>;
    if (loading) return <div className="flex justify-center items-center h-screen"><Activity className="animate-spin text-primary h-12 w-12" /></div>;
    if (error) return <div className="p-8 text-center text-red-500">{error}</div>;

    const { fundamentals, chart_data, pros, cons } = data;

    return (
        <div className="min-h-screen bg-gray-50 pb-12">

            {/* Header Bar */}
            <div className="bg-white border-b border-gray-200 py-6 px-8 shadow-sm mb-8">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">{fundamentals.shortName}</h1>
                        <span className="inline-block mt-1 px-3 py-1 bg-gray-100 text-gray-700 font-semibold rounded text-sm tracking-wide">
                            {ticker.toUpperCase()}
                        </span>
                    </div>
                    <div className="text-right">
                        <p className="text-sm font-medium text-gray-500 uppercase tracking-widest mb-1">Current Price</p>
                        <p className="text-4xl font-extrabold text-gray-900">₹{fundamentals.currentPrice}</p>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

                {/* Core Fundamental Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-center">
                        <span className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Market Cap</span>
                        <span className="text-xl font-bold text-gray-900 mt-2">
                            {fundamentals.marketCap !== 'N/A' ? `₹${(fundamentals.marketCap / 10000000000).toFixed(2)}Cr` : 'N/A'}
                        </span>
                    </div>
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-center">
                        <span className="text-sm font-semibold text-gray-400 uppercase tracking-wider">P/E Ratio</span>
                        <span className="text-xl font-bold text-gray-900 mt-2">{fundamentals.trailingPE}</span>
                    </div>
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-center">
                        <span className="text-sm font-semibold text-gray-400 uppercase tracking-wider">P/B Ratio</span>
                        <span className="text-xl font-bold text-gray-900 mt-2">{fundamentals.priceToBook}</span>
                    </div>
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-center">
                        <span className="text-sm font-semibold text-gray-400 uppercase tracking-wider">52W High / Low</span>
                        <span className="text-xl font-bold text-gray-900 mt-2">
                            ₹{fundamentals.fiftyTwoWeekHigh} / ₹{fundamentals.fiftyTwoWeekLow}
                        </span>
                    </div>
                </div>

                {/* Main Interface: Chart & Analysis pane */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                    {/* Left Column: Interactive Chart */}
                    <div className="lg:col-span-2 bg-white rounded-3xl shadow-sm border border-gray-100 p-6">
                        <div className="flex items-center mb-6">
                            <Target className="h-5 w-5 text-gray-400 mr-2" />
                            <h2 className="text-lg font-bold text-gray-800">6-Month Price Action</h2>
                        </div>
                        <div className="h-96 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={chart_data || []}>
                                    <XAxis dataKey="date" tick={{ fontSize: 12, fill: '#6B7280' }} tickLine={false} axisLine={false} minTickGap={30} />
                                    <YAxis domain={['auto', 'auto']} tick={{ fontSize: 12, fill: '#6B7280' }} tickLine={false} axisLine={false} tickFormatter={(val) => `₹${val}`} />
                                    <Tooltip
                                        contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}
                                        labelStyle={{ fontWeight: 'bold', color: '#111827' }}
                                        itemStyle={{ color: '#1a56db' }}
                                    />
                                    <Line type="monotone" dataKey="price" stroke="#1a56db" strokeWidth={2} dot={false} activeDot={{ r: 6, fill: '#1a56db' }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Right Column: Pros and Cons / Intelligence */}
                    <div className="flex flex-col gap-6">
                        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 flex-1">
                            <h2 className="text-lg font-bold text-gray-800 mb-6 flex items-center">
                                <BadgeCheck className="h-5 w-5 text-green-500 mr-2" />
                                Pros (Technical Strengths)
                            </h2>
                            {pros && pros.length > 0 ? (
                                <ul className="space-y-4">
                                    {pros.map((pro, index) => (
                                        <li key={index} className="flex items-start">
                                            <div className="flex-shrink-0 h-5 w-5 rounded-full bg-green-100 flex items-center justify-center mt-0.5">
                                                <span className="block h-2 w-2 rounded-full bg-green-500"></span>
                                            </div>
                                            <span className="ml-3 text-sm text-gray-700 leading-relaxed">{pro}</span>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p className="text-sm text-gray-400 italic">No distinctive pros identified.</p>
                            )}
                        </div>

                        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 flex-1">
                            <h2 className="text-lg font-bold text-gray-800 mb-6 flex items-center">
                                <XCircle className="h-5 w-5 text-red-500 mr-2" />
                                Cons (Technical Risks)
                            </h2>
                            {cons && cons.length > 0 ? (
                                <ul className="space-y-4">
                                    {cons.map((con, index) => (
                                        <li key={index} className="flex items-start">
                                            <div className="flex-shrink-0 h-5 w-5 rounded-full bg-red-100 flex items-center justify-center mt-0.5">
                                                <span className="block h-2 w-2 rounded-full bg-red-500"></span>
                                            </div>
                                            <span className="ml-3 text-sm text-gray-700 leading-relaxed">{con}</span>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p className="text-sm text-gray-400 italic">No critical risks identified.</p>
                            )}
                        </div>

                        {/* Neuro-Symbolic Callout Stub (Phase 10 integration) */}
                        <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-3xl p-6 shadow-md text-white">
                            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-2 flex items-center">
                                <ShieldAlert className="h-4 w-4 mr-2" />
                                AI Inference Target
                            </h3>
                            <p className="text-sm text-gray-300">Phase 10: Autoencoder and Expert System overlay will inject "Buy/Sell" classification directly into this pane.</p>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
