import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
import Opportunities from './pages/Opportunities';
import OpportunityDetail from './pages/OpportunityDetail';
import Tracked from './pages/Tracked';
import Profile from './pages/Profile';
import Layout from './components/Layout';
import { authAPI } from './services/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('authToken');
    setIsAuthenticated(!!token);
    setLoading(false);
  };

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = async () => {
    await authAPI.logout();
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: 'linear-gradient(180deg, #0a0a0f 0%, #1a1a2e 100%)',
        color: '#fff'
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes - no auth required */}
        <Route path="/" element={<Layout onLogout={handleLogout} isAuthenticated={isAuthenticated} />}>
          <Route index element={<Home />} />
          <Route path="opportunities" element={<Opportunities />} />
          <Route path="opportunities/:id" element={<OpportunityDetail isAuthenticated={isAuthenticated} />} />
        </Route>

        {/* Auth routes */}
        <Route path="/login" element={
          isAuthenticated ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />
        } />
        <Route path="/register" element={
          isAuthenticated ? <Navigate to="/" replace /> : <Register onLogin={handleLogin} />
        } />

        {/* Protected routes - auth required */}
        <Route path="/" element={<Layout onLogout={handleLogout} isAuthenticated={isAuthenticated} />}>
          <Route path="tracked" element={
            isAuthenticated ? <Tracked /> : <Navigate to="/login" replace />
          } />
          <Route path="profile" element={
            isAuthenticated ? <Profile /> : <Navigate to="/login" replace />
          } />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
