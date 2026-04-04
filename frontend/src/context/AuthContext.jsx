import React, { createContext, useState, useEffect, useContext } from 'react';
import { supabase } from '../lib/supabase';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [session, setSession] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Get initial session
        supabase.auth.getSession().then(({ data: { session } }) => {
            setSession(session);
            setUser(session?.user || null);
            setLoading(false);
            if (session?.access_token) {
                axios.defaults.headers.common['Authorization'] = `Bearer ${session.access_token}`;
            }
        });

        // Listen for auth changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
            (_event, session) => {
                setSession(session);
                setUser(session?.user || null);
                setLoading(false);
                if (session?.access_token) {
                    axios.defaults.headers.common['Authorization'] = `Bearer ${session.access_token}`;
                } else {
                    delete axios.defaults.headers.common['Authorization'];
                }
            }
        );

        return () => subscription.unsubscribe();
    }, []);

    const sendOtp = async (email) => {
        try {
            const { error } = await supabase.auth.signInWithOtp({
                email,
            });
            if (error) throw error;
            return { success: true };
        } catch (error) {
            console.error("Error sending OTP:", error);
            return { success: false, error: error.message };
        }
    };

    const verifyOtp = async (email, otp) => {
        try {
            const { data, error } = await supabase.auth.verifyOtp({
                email,
                token: otp,
                type: 'email',
            });
            if (error) throw error;
            return { success: true, data };
        } catch (error) {
            console.error("Error verifying OTP:", error);
            return { success: false, error: error.message };
        }
    };

    const logout = async () => {
        try {
            const { error } = await supabase.auth.signOut();
            if (error) throw error;
        } catch (error) {
            console.error("Error signing out:", error);
        }
    };

    // Keep token for compatibility if some components check for it
    const token = session?.access_token || null;

    // Overwrite the original context value fields but use supabase logic
    return (
        <AuthContext.Provider value={{ user, session, token, loading, sendOtp, verifyOtp, logout }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
