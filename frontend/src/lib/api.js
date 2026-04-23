import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://trading-system-ma0a.onrender.com';

export const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000, // 30 seconds to prevent infinite spinners
});

export { API_BASE_URL };
