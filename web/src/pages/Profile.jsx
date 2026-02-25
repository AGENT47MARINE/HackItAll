import { useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import './Pages.css';

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await authAPI.getCurrentUser();
      setProfile(data);
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading profile...</div>;
  }

  if (!profile) {
    return <div className="empty-state"><h2>Failed to load profile</h2></div>;
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <div className="profile-avatar">
          {profile.email.charAt(0).toUpperCase()}
        </div>
        <h1>{profile.email}</h1>
      </div>

      <div className="profile-section">
        <h2>Education</h2>
        <p>{profile.education_level}</p>
      </div>

      {profile.interests && profile.interests.length > 0 && (
        <div className="profile-section">
          <h2>Interests</h2>
          <div className="tags-list">
            {profile.interests.map((interest, index) => (
              <span key={index} className="tag">{interest}</span>
            ))}
          </div>
        </div>
      )}

      {profile.skills && profile.skills.length > 0 && (
        <div className="profile-section">
          <h2>Skills</h2>
          <div className="tags-list">
            {profile.skills.map((skill, index) => (
              <span key={index} className="tag">{skill}</span>
            ))}
          </div>
        </div>
      )}

      <div className="profile-section">
        <h2>Notifications</h2>
        <div className="profile-row">
          <span>Email Notifications</span>
          <span className="profile-value">
            {profile.notification_email ? 'Enabled' : 'Disabled'}
          </span>
        </div>
        <div className="profile-row">
          <span>SMS Notifications</span>
          <span className="profile-value">
            {profile.notification_sms ? 'Enabled' : 'Disabled'}
          </span>
        </div>
      </div>

      <div className="profile-section">
        <h2>Preferences</h2>
        <div className="profile-row">
          <span>Low Bandwidth Mode</span>
          <span className="profile-value">
            {profile.low_bandwidth_mode ? 'Enabled' : 'Disabled'}
          </span>
        </div>
      </div>
    </div>
  );
}
