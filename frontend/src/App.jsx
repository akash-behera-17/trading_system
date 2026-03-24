import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

import Home from './pages/Home';

// Dummy components for Phase 7 routing validation
const Login = () => <div className="p-8"><h1 className="text-2xl font-bold">Login</h1><p>Auth forms will be built here.</p></div>;
const Dashboard = () => <div className="p-8"><h1 className="text-2xl text-primary font-bold">Dashboard</h1><p>Protected screener interface.</p></div>;

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Home Page with Search */}
          <Route path="/" element={<Home />} />

          <Route path="/login" element={<Login />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Route>

        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
