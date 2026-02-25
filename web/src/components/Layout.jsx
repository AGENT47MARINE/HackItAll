import { Outlet, Link, useLocation } from 'react-router-dom';
import './Layout.css';

export default function Layout({ onLogout }) {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="nav-container">
          <Link to="/" className="nav-brand">
            Opportunity Access Platform
          </Link>
          <div className="nav-links">
            <Link to="/" className={`nav-link ${isActive('/')}`}>
              Discover
            </Link>
            <Link to="/opportunities" className={`nav-link ${isActive('/opportunities')}`}>
              Search
            </Link>
            <Link to="/tracked" className={`nav-link ${isActive('/tracked')}`}>
              Saved
            </Link>
            <Link to="/profile" className={`nav-link ${isActive('/profile')}`}>
              Profile
            </Link>
            <button onClick={onLogout} className="nav-button">
              Logout
            </button>
          </div>
        </div>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
