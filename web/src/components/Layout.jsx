import { useEffect, useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { SignedIn, SignedOut, UserButton, useUser } from '@clerk/clerk-react';
import api from '../services/api';
import PixelLogo from './PixelLogo';
import PixelIcon from './PixelIcon';
import './Layout.css';

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { isLoaded, user } = useUser();

  useEffect(() => {
    // If user is authenticated, check if they finished onboarding
    const checkOnboarding = async () => {
      if (isLoaded && user && location.pathname !== '/onboarding') {
        try {
          const res = await api.get('/auth/me');
          if (res.data && res.data.education_level === 'Not Specified') {
            navigate('/onboarding');
          }
        } catch (error) {
          console.error('Failed to check onboarding status', error);
        }
      }
    };

    checkOnboarding();
  }, [isLoaded, user, location.pathname, navigate]);

  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="nav-container">
          <Link to="/" className="nav-brand">
            <PixelLogo />
            {localStorage.getItem('liteMode') === 'true' && (
              <span className="bg-amber-500 text-white text-[10px] px-1.5 py-0.5 rounded font-black ml-2 tracking-tighter">LITE</span>
            )}
          </Link>
          <div className="nav-links">
            <Link to="/discover" className={`nav-link ${isActive('/discover')}`}>
              Discover
            </Link>
            <Link to="/opportunities" className={`nav-link ${isActive('/opportunities')}`}>
              Search
            </Link>
            <SignedIn>
              <Link to="/tracked" className={`nav-link ${isActive('/tracked')}`}>
                Saved
              </Link>
              <Link to="/leagues" className={`nav-link ${isActive('/leagues')}`}>
                <PixelIcon name="trophy" size={18} color="var(--pixel-gold)" active={isActive('/leagues')} />
                <span style={{ marginLeft: '4px' }}>Leagues</span>
              </Link>
              <Link to="/profile" className={`nav-link ${isActive('/profile')}`}>
                Profile
              </Link>
              <div className="nav-button">
                <UserButton afterSignOutUrl="/" />
              </div>
            </SignedIn>
            <SignedOut>
              <Link to="/login" className="nav-button login-button">
                Login
              </Link>
              <Link to="/register" className="nav-button register-button">
                Get Started
              </Link>
            </SignedOut>
          </div>
        </div>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
