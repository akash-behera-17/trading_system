import React, { useState, useEffect, useRef, useDeferredValue } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import { api } from '../lib/api';
import { useAuth } from '../context/useAuth';

const SearchBar = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const wrapperRef = useRef(null);
    const navigate = useNavigate();
    const { token } = useAuth();
    const deferredQuery = useDeferredValue(query);

    // Close dropdown if clicked outside
    useEffect(() => {
        function handleClickOutside(event) {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [wrapperRef]);

    useEffect(() => {
        if (!isOpen) {
            return undefined;
        }

        let cancelled = false;

        const fetchStocks = async () => {
            try {
                setLoading(true);
                setError('');
                const trimmed = deferredQuery.trim();
                const response = await api.get('/api/stocks/search', {
                    params: trimmed ? { q: trimmed } : {},
                });
                if (!cancelled) {
                    setResults(response.data);
                }
            } catch (fetchError) {
                console.error('Error fetching stocks:', fetchError);
                if (!cancelled) {
                    setResults([]);
                    setError('Unable to load suggestions right now.');
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        };

        const debounceId = setTimeout(() => {
            fetchStocks();
        }, deferredQuery.trim() ? 250 : 0);

        return () => {
            cancelled = true;
            clearTimeout(debounceId);
        };
    }, [deferredQuery, isOpen]);

    const handleSelect = (ticker) => {
        setIsOpen(false);
        setQuery('');
        setError('');
        if (!token) {
            // Not logged in → send to login, remember intended destination
            navigate('/login', { state: { from: `/dashboard?ticker=${ticker}` } });
        } else {
            navigate(`/dashboard?ticker=${ticker}`);
        }
    };

    const handleEnter = () => {
        const trimmed = query.trim();
        if (!trimmed) {
            return;
        }

        const normalized = trimmed.toUpperCase();
        const exactMatch = results.find((stock) => {
            const baseTicker = stock.ticker.replace('.NS', '');
            return (
                stock.ticker === normalized ||
                baseTicker === normalized ||
                stock.name.toLowerCase() === trimmed.toLowerCase()
            );
        });

        handleSelect(exactMatch?.ticker || results[0]?.ticker || `${normalized}.NS`);
    };

    return (
        <div ref={wrapperRef} className="relative mx-auto w-full max-w-2xl">
            <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
                    <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                    type="text"
                    className="search-bar-input w-full rounded-xl border border-gray-200 bg-white py-4 pl-12 pr-4 text-lg shadow-sm focus:border-transparent focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="Search Nifty 50 companies (e.g., RELIANCE, TCS)"
                    value={query}
                    onChange={(event) => {
                        setQuery(event.target.value);
                        setIsOpen(true);
                    }}
                    onFocus={() => setIsOpen(true)}
                    onKeyDown={(event) => {
                        if (event.key === 'Enter' && query.trim()) {
                            handleEnter();
                        }
                    }}
                />
            </div>

            {isOpen && (
                <div className="absolute z-10 mt-2 w-full overflow-hidden rounded-2xl border border-white/10 bg-[#10101a] shadow-2xl shadow-black/30 backdrop-blur-xl">
                    <div className="flex items-center justify-between border-b border-white/6 px-4 py-3 text-xs uppercase tracking-[0.18em] text-white/35">
                        <span>{query.trim() ? 'Search Results' : 'Popular in Nifty 50'}</span>
                        {loading && <span>Loading</span>}
                    </div>

                    {error && (
                        <div className="px-4 py-4 text-sm text-red-300">{error}</div>
                    )}

                    {!error && !loading && results.length === 0 && (
                        <div className="px-4 py-4 text-sm text-white/45">
                            No matching stock found. Try a Nifty 50 company name or ticker.
                        </div>
                    )}

                    {!error && results.length > 0 && (
                        <ul className="max-h-96 overflow-y-auto">
                            {results.map((stock) => (
                                <li
                                    key={stock.ticker}
                                    className="cursor-pointer border-b border-white/6 px-5 py-4 transition-colors last:border-0 hover:bg-white/5"
                                    onClick={() => handleSelect(stock.ticker)}
                                >
                                    <div className="flex items-center justify-between">
                                        <span className="font-semibold text-white">{stock.name}</span>
                                        <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-xs font-medium text-white/55">
                                            {stock.ticker}
                                        </span>
                                    </div>
                                    <div className="mt-1 text-xs text-white/35">
                                        Click to open the full technical dashboard
                                    </div>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            )}
        </div>
    );
};

export default SearchBar;
