import { Outlet, Link, useLocation } from 'react-router-dom';
import './Layout.css';

export default function Layout({ onLogout, isAuthenticated }) {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="nav-container">
          <Link to="/" className="nav-brand">
            <span className="brand-icon">◆</span>
            OpportunityHub
          </Link>
          <div className="nav-links">
            <Link to="/" className={`nav-link ${isActive('/')}`}>
              Discover
            </Link>
            <Link to="/opportunities" className={`nav-link ${isActive('/opportunities')}`}>
              Search
            </Link>
            {isAuthenticated ? (
              <>
                <Link to="/tracked" className={`nav-link ${isActive('/tracked')}`}>
                  Saved
                </Link>
                <Link to="/profile" className={`nav-link ${isActive('/profile')}`}>
                  Profile
                </Link>
                <button onClick={onLogout} className="nav-button logout-button">
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="nav-button login-button">
                  Login
                </Link>
                <Link to="/register" className="nav-button register-button">
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
