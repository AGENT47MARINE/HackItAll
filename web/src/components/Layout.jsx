import React, { useState, useEffect } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { SignedIn, SignedOut, UserButton, useUser, useAuth } from '@clerk/clerk-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import PixelLogo from './PixelLogo';
import PixelIcon from './PixelIcon';
import VoiceAssistant from './VoiceAssistant';
import './Layout.css';

const Layout = () => {
  const location = useLocation();
  const { isSignedIn } = useUser();
  const { getToken } = useAuth();
  const isActive = (path) => location.pathname === path;

  // Notification State
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifDropdown, setShowNotifDropdown] = useState(false);

  useEffect(() => {
    if (isSignedIn) {
      fetchNotifications();
      // Request permission on mount if signed in
      if ("Notification" in window && Notification.permission === "default") {
        Notification.requestPermission();
      }
    }
  }, [isSignedIn]);

  // Keep track of IDs we've already alerted on in the current session
  const [alertedIds] = useState(new Set());

  const fetchNotifications = async () => {
    try {
      const token = await getToken();
      const response = await axios.get('http://localhost:8000/api/notifications', {
        headers: { Authorization: `Bearer ${token}` }
      });

      const data = response.data;
      setNotifications(data);
      setUnreadCount(data.filter(n => !n.is_read).length);

      // Trigger Browser Notifications for new unread items
      if ("Notification" in window && Notification.permission === "granted") {
        data.forEach(n => {
          if (!n.is_read && !alertedIds.has(n.id)) {
            // It's a new unread notification
            const title = n.type === 'submission_3h' ? '🚨 URGENT HACKATHON ALERT' : '⏰ Hackathon Reminder';
            new Notification(title, {
              body: n.message,
              icon: '/pixel_logo_gold.png', // Fallback to a logo if available
              tag: n.id // Prevent duplicates
            });
            alertedIds.add(n.id);
          }
        });
      }
    } catch (err) {
      console.error('Error fetching notifications:', err);
    }
  };

  const handleNotificationClick = async (notif) => {
    if (!notif.is_read) {
      try {
        const token = await getToken();
        await axios.patch(`http://localhost:8000/api/notifications/${notif.id}/read`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
        fetchNotifications();
      } catch (err) {
        console.error('Error marking notification as read:', err);
      }
    }
    setShowNotifDropdown(false);
  };

  const toggleNotifDropdown = () => {
    setShowNotifDropdown(!showNotifDropdown);
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
            <Link to="/discover" className={`nav-link ${isActive('/discover') ? 'active' : ''}`}>
              Discover
            </Link>
            <Link to="/opportunities" className={`nav-link ${isActive('/opportunities') ? 'active' : ''}`}>
              Search
            </Link>

            <SignedIn>
              <Link to="/tracked" className={`nav-link ${isActive('/tracked') ? 'active' : ''}`}>
                Saved
              </Link>
              <Link to="/leagues" className={`nav-link ${isActive('/leagues') ? 'active' : ''}`}>
                <PixelIcon name="trophy" size={18} color="var(--pixel-gold)" active={isActive('/leagues')} />
                <span style={{ marginLeft: '4px' }}>Leagues</span>
              </Link>
              <Link to="/profile" className={`nav-link ${isActive('/profile') ? 'active' : ''}`}>
                Profile
              </Link>

              {/* Notification Bell */}
              <div className="notification-wrapper">
                <button
                  className={`nav-notif-btn ${unreadCount > 0 ? 'has-unread' : ''}`}
                  onClick={toggleNotifDropdown}
                >
                  <PixelIcon name="bell" size={20} color={unreadCount > 0 ? 'var(--pixel-gold)' : 'rgba(255,255,255,0.6)'} active={unreadCount > 0} />
                  {unreadCount > 0 && <span className="notif-badge">{unreadCount}</span>}
                </button>

                <AnimatePresence>
                  {showNotifDropdown && (
                    <motion.div
                      className="notif-dropdown glass"
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    >
                      <div className="notif-header">
                        <h3>Notifications</h3>
                        <Link to="/profile" onClick={() => setShowNotifDropdown(false)}>Settings</Link>
                      </div>
                      <div className="notif-list">
                        {notifications.length > 0 ? (
                          notifications.map(n => (
                            <div
                              key={n.id}
                              className={`notif-item ${!n.is_read ? 'unread' : ''} ${n.type}`}
                              onClick={() => handleNotificationClick(n)}
                            >
                              <div className="notif-item-icon">
                                {n.type === 'submission_3h' ? '🚨' :
                                  n.type === 'submission_24h' ? '⏰' :
                                    n.type === 'hackathon_1d' ? '🚀' : '📅'}
                              </div>
                              <div className="notif-item-body">
                                <p className="notif-message">
                                  {n.message}
                                </p>
                                <span className="notif-time">
                                  {new Date(n.scheduled_time).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                                </span>
                              </div>
                              {!n.is_read && <div className="unread-dot"></div>}
                            </div>
                          ))
                        ) : (
                          <div className="notif-empty">
                            <p>No new notifications</p>
                          </div>
                        )}
                      </div>
                      <div className="notif-footer">
                        <Link to="/tracked" onClick={() => setShowNotifDropdown(false)}>View All My Events</Link>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              <div className="nav-button-wrapper">
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

      {/* Global Voice Assistant */}
      <VoiceAssistant />

      {/* Footer (Optional, can be added if needed) */}
    </div>
  );
};

export default Layout;
