import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = () => {
    const { token, loading } = useAuth();

    if (loading) {
        return <div className="min-h-screen flex items-center justify-center bg-gray-50 text-gray-500">Loading auth state...</div>;
    }

    // If there's no token, push to the login screen
    if (!token) {
        return <Navigate to="/login" replace />;
    }

    // Otherwise, render the child routes via standard Outlet
    return <Outlet />;
};

export default ProtectedRoute;
