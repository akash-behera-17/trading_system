import React from 'react';
import SearchBar from '../components/SearchBar';
import { TrendingUp, ShieldAlert, BarChart3 } from 'lucide-react';

const Home = () => {
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">

            {/* Hero Section */}
            <div className="w-full max-w-4xl text-center space-y-6">
                <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 tracking-tight">
                    Smarter Market <span className="text-primary text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Intelligence</span>
                </h1>
                <p className="text-lg md:text-xl text-gray-600 max-w-2xl mx-auto">
                    Advanced Neuro-Symbolic stock analysis for Indian markets.
                    Get definitive buy/sell confidence backed by deep learning.
                </p>

                {/* Search Component */}
                <div className="pt-8 pb-12">
                    <SearchBar />
                </div>

                {/* Features Preview */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-10 border-t border-gray-200 text-left">
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                        <TrendingUp className="h-8 w-8 text-blue-500 mb-4" />
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Trend Analysis</h3>
                        <p className="text-gray-600 text-sm">Actionable indicators using automated DMA, MACD, and RSI verification.</p>
                    </div>
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                        <ShieldAlert className="h-8 w-8 text-indigo-500 mb-4" />
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Anomaly Detection</h3>
                        <p className="text-gray-600 text-sm">LSTM Autoencoders filter out false signals and bull traps automatically.</p>
                    </div>
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                        <BarChart3 className="h-8 w-8 text-purple-500 mb-4" />
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Institutional Grade</h3>
                        <p className="text-gray-600 text-sm">Built to match screener.in's utility with advanced AI scoring overlays.</p>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default Home;
