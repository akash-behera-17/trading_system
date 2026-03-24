import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token') || null);
    const [loading, setLoading] = useState(true);

    // Set the default Authorization header globally if token exists
    useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            localStorage.setItem('token', token);

            // In a real app we'd decode JWT or call a /me endpoint to get the user context.
            // For this step, simply holding the token is enough for routing logic.
            setUser({ authenticated: true });
        } else {
            delete axios.defaults.headers.common['Authorization'];
            localStorage.removeItem('token');
            setUser(null);
        }
        setLoading(false);
    }, [token]);

    const login = async (email, password) => {
        try {
            // Expecting Flask to be running on port 5000
            const response = await axios.post('http://localhost:5000/api/auth/login', {
                email,
                password
            });
            setToken(response.data.token);
            return { success: true };
        } catch (error) {
            console.error("Login failed:", error);
            return {
                success: false,
                error: error.response?.data?.error || "Login failed due to server error"
            };
        }
    };

    const logout = () => {
        setToken(null);
    };

    const register = async (username, email, password) => {
        try {
            const response = await axios.post('http://localhost:5000/api/auth/register', {
                username,
                email,
                password
            });
            // Normally after register one might login automatically, but let's just return success for the UI to handle
            return { success: true };
        } catch (error) {
            console.error("Registration failed:", error);
            return {
                success: false,
                error: error.response?.data?.error || "Registration failed due to server error"
            };
        }
    }

    return (
        <AuthContext.Provider value={{ user, token, login, logout, register, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
