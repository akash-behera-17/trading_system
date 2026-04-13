import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/useAuth';
import { ShieldCheck, Mail, Key, Activity, ArrowLeft } from 'lucide-react';

const Login = () => {
    const [step, setStep] = useState('email'); // 'email' | 'otp'
    const [email, setEmail] = useState('');
    const [otp, setOtp] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');

    const { sendOtp, verifyOtp } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const handleSendOtp = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');
        setLoading(true);

        const res = await sendOtp(email);
        if (res.success) {
            setStep('otp');
            setMessage('A one-time passcode has been sent to your email.');
        } else {
            setError(res.error || 'Failed to send OTP. Please try again.');
        }
        setLoading(false);
    };

    const handleVerifyOtp = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const res = await verifyOtp(email, otp);
        if (res.success) {
            const from = location.state?.from || '/';
            navigate(from);
        } else {
            setError(res.error || 'Invalid OTP code. Please try again.');
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen flex">
            {/* Left Side App Title - Dark Theme */}
            <div className="hidden lg:flex w-1/2 bg-gray-900 text-white flex-col justify-center items-center p-12 relative overflow-hidden">
                <div className="absolute inset-0 bg-indigo-900/20 mix-blend-multiply"></div>
                <div className="z-10 flex flex-col items-center">
                    <ShieldCheck className="h-24 w-24 text-indigo-500 mb-8" />
                    <h1 className="text-5xl font-extrabold tracking-tight text-center leading-tight">
                        Neuro-Symbolic <br />Trading System
                    </h1>
                    <p className="mt-6 text-xl text-gray-400 text-center max-w-md leading-relaxed">
                        Precision market insights powered by advanced machine learning models and expert-crafted strategies.
                    </p>
                </div>
            </div>

            {/* Right Side Login - Light Theme */}
            <div className="flex-1 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-20 bg-gray-50">
                <div className="mx-auto w-full max-w-md">
                    <div className="lg:hidden text-center mb-8">
                        <ShieldCheck className="mx-auto h-16 w-16 text-indigo-600" />
                    </div>

                    <div className="text-center lg:text-left mb-8">
                        <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">
                            {step === 'email' ? 'Sign in with Email' : 'Enter One-Time Password'}
                        </h2>
                        <p className="mt-2 text-sm text-gray-600">
                            Unlock Neuro-Symbolic Trading Insights securely.
                        </p>
                    </div>

                    <div className="bg-white py-8 px-4 shadow-xl sm:rounded-2xl sm:px-10 border border-gray-100">

                    {error && (
                        <div className="mb-4 bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
                            <p className="text-sm text-red-700 font-medium">{error}</p>
                        </div>
                    )}
                    
                    {message && (
                        <div className="mb-4 bg-green-50 border-l-4 border-green-500 p-4 rounded-md">
                            <p className="text-sm text-green-700 font-medium">{message}</p>
                        </div>
                    )}

                    {step === 'email' ? (
                        <form className="space-y-6" onSubmit={handleSendOtp}>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Email address</label>
                                <div className="mt-1 relative rounded-md shadow-sm">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Mail className="h-5 w-5 text-gray-400" />
                                    </div>
                                    <input
                                        type="email"
                                        required
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl focus:ring-indigo-500 focus:border-indigo-500 bg-gray-50 text-gray-900"
                                        placeholder="name@example.com"
                                    />
                                </div>
                            </div>
                            <div>
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition-colors"
                                >
                                    {loading ? <Activity className="h-5 w-5 animate-spin" /> : 'Send OTP'}
                                </button>
                            </div>
                        </form>
                    ) : (
                        <form className="space-y-6" onSubmit={handleVerifyOtp}>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Secure OTP Code</label>
                                <div className="mt-1 relative rounded-md shadow-sm">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Key className="h-5 w-5 text-gray-400" />
                                    </div>
                                    <input
                                        type="text"
                                        required
                                        value={otp}
                                        onChange={(e) => setOtp(e.target.value)}
                                        className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl focus:ring-indigo-500 focus:border-indigo-500 bg-gray-50 text-gray-900"
                                        placeholder="Enter the code sent to your email"
                                    />
                                </div>
                            </div>
                            <div>
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition-colors"
                                >
                                    {loading ? <Activity className="h-5 w-5 animate-spin" /> : 'Verify and Sign In'}
                                </button>
                            </div>
                            <div className="mt-4 text-center">
                                <button
                                    type="button"
                                    onClick={() => { setStep('email'); setOtp(''); setError(''); setMessage(''); }}
                                    className="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500"
                                >
                                    <ArrowLeft className="h-4 w-4 mr-1" />
                                    Back to email
                                </button>
                            </div>
                        </form>
                    )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
