import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

const ProtectedRoute = () => {
    const { token, loading } = useAuth();
    const location = useLocation();

    if (loading) {
        return <div className="min-h-screen flex items-center justify-center bg-gray-50 text-gray-500">Loading auth state...</div>;
    }

    // If there's no token, push to the login screen
    if (!token) {
        return <Navigate to="/login" state={{ from: location.pathname + location.search }} replace />;
    }

    // Otherwise, render the child routes via standard Outlet
    return <Outlet />;
};

export default ProtectedRoute;
