import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const SearchBar = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const wrapperRef = useRef(null);
    const navigate = useNavigate();
    const { token } = useAuth();

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

    // Debounced search
    useEffect(() => {
        const fetchStocks = async () => {
            try {
                const response = await axios.get(`http://localhost:5000/api/stocks/search?q=${query}`);
                setResults(response.data);
            } catch (err) {
                console.error("Error fetching stocks:", err);
            }
        };

        const debounceId = setTimeout(() => {
            if (query.length > 0) {
                fetchStocks();
            } else {
                setResults([]);
            }
        }, 300);

        return () => clearTimeout(debounceId);
    }, [query]);

    const handleSelect = (ticker) => {
        setIsOpen(false);
        setQuery('');
        if (!token) {
            // Not logged in → send to login, remember intended destination
            navigate('/login', { state: { from: `/dashboard?ticker=${ticker}` } });
        } else {
            navigate(`/dashboard?ticker=${ticker}`);
        }
    };

    return (
        <div ref={wrapperRef} className="relative w-full max-w-2xl mx-auto">
            <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                    type="text"
                    className="search-bar-input w-full pl-12 pr-4 py-4 rounded-xl border border-gray-200 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-lg bg-white"
                    placeholder="Search for companies (e.g., RELIANCE, TCS)"
                    value={query}
                    onChange={(e) => {
                        setQuery(e.target.value);
                        setIsOpen(true);
                    }}
                    onFocus={() => setIsOpen(true)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && query.trim()) {
                            handleSelect(query.toUpperCase());
                        }
                    }}
                />
            </div>

            {isOpen && results.length > 0 && (
                <ul className="absolute z-10 w-full mt-2 bg-white border border-gray-100 rounded-lg shadow-xl overflow-hidden max-h-96 overflow-y-auto">
                    {results.map((stock) => (
                        <li
                            key={stock.ticker}
                            className="px-6 py-4 hover:bg-gray-50 cursor-pointer border-b border-gray-50 last:border-0"
                            onClick={() => handleSelect(stock.ticker)}
                        >
                            <div className="flex justify-between items-center">
                                <span className="font-semibold text-gray-900">{stock.name}</span>
                                <span className="text-sm font-medium text-gray-400 bg-gray-100 px-2 py-1 rounded">{stock.ticker}</span>
                            </div>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default SearchBar;
