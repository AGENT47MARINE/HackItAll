import { useState, useEffect } from 'react';
import api from '../services/api';
import GridBackground from '../components/GridBackground';
import PixelLogo from '../components/PixelLogo';
import './Pages.css';

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await api.get('/auth/me');
      setProfile(response.data);
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="profile-page">
        <GridBackground />
        <div className="profile-content">
          <div className="loading-modern">
            <div className="loading-spinner-modern"></div>
            <p>Loading profile...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="profile-page">
        <GridBackground />
        <div className="profile-content">
          <div className="empty-state-modern">
            <div className="empty-icon">◇</div>
            <h2>Failed to load profile</h2>
            <p>Please try again later</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <GridBackground />


      <div className="profile-content">
        {/* Header */}
        <div className="profile-header-modern">
          <div className="profile-avatar-modern">
            {profile.email.charAt(0).toUpperCase()}
          </div>
          <h1 className="profile-title">{profile.email}</h1>
          <p className="profile-subtitle">Member since {new Date(profile.created_at).toLocaleDateString()}</p>
          {profile.activity_streak !== undefined && (
            <div className="profile-streak-badge">
              🔥 {profile.activity_streak} Week Streak
            </div>
          )}
        </div>

        {/* Profile Grid */}
        <div className="profile-grid">
          {/* Education Section */}
          <div className="profile-card">
            <div className="profile-card-header">
              <span className="profile-icon">🎓</span>
              <h2>Education</h2>
            </div>
            <div className="profile-card-content">
              <p className="profile-value-large">{profile.education_level}</p>
            </div>
          </div>

          {/* Interests Section */}
          {profile.interests && profile.interests.length > 0 && (
            <div className="profile-card">
              <div className="profile-card-header">
                <span className="profile-icon">💡</span>
                <h2>Interests</h2>
              </div>
              <div className="profile-card-content">
                <div className="tags-list-modern">
                  {profile.interests.map((interest, index) => (
                    <span key={index} className="tag-modern">{interest}</span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Skills Section */}
          {profile.skills && profile.skills.length > 0 && (
            <div className="profile-card">
              <div className="profile-card-header">
                <span className="profile-icon">⚡</span>
                <h2>Skills</h2>
              </div>
              <div className="profile-card-content">
                <div className="tags-list-modern">
                  {profile.skills.map((skill, index) => (
                    <span key={index} className="tag-modern">{skill}</span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Notifications Section */}
          <div className="profile-card">
            <div className="profile-card-header">
              <span className="profile-icon">🔔</span>
              <h2>Notifications</h2>
            </div>
            <div className="profile-card-content">
              <div className="profile-row-modern">
                <span>Email Notifications</span>
                <span className={`profile-badge ${profile.notification_email ? 'active' : ''}`}>
                  {profile.notification_email ? 'Enabled' : 'Disabled'}
                </span>
              </div>
              <div className="profile-row-modern">
                <span>SMS Notifications</span>
                <span className={`profile-badge ${profile.notification_sms ? 'active' : ''}`}>
                  {profile.notification_sms ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            </div>
          </div>

          {/* Preferences Section */}
          <div className="profile-card">
            <div className="profile-card-header">
              <span className="profile-icon">⚙️</span>
              <h2>Preferences</h2>
            </div>
            <div className="profile-card-content">
              <div className="profile-row-modern">
                <span>Low Bandwidth Mode</span>
                <span className={`profile-badge ${profile.low_bandwidth_mode ? 'active' : ''}`}>
                  {profile.low_bandwidth_mode ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
