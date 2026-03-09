import { useState, useEffect, useRef } from 'react';
import api, { profileAPI } from '../services/api';
import GridBackground from '../components/GridBackground';
import PixelLogo from '../components/PixelLogo';
import './Pages.css';
import './Profile.css';
import axios from 'axios'; // Added axios import

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);
  const [xpStats, setXpStats] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [syncStatus, setSyncStatus] = useState(null);
  const [editingSkills, setEditingSkills] = useState(false);
  const [editingInterests, setEditingInterests] = useState(false);
  const [newSkill, setNewSkill] = useState('');
  const [newInterest, setNewInterest] = useState('');
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchProfile();
    fetchNotifications();
    fetchXpStats();
  }, []);

  const fetchProfile = async () => {
    try {
      const data = await profileAPI.getProfile();
      setProfile(data);
    } catch (err) {
      console.error('Error fetching profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchNotifications = async () => {
    try {
      const response = await api.get('/notifications');
      setNotifications(response.data);
    } catch (err) {
      console.error('Error fetching notifications in profile:', err);
    }
  };

  const fetchXpStats = async () => {
    try {
      const response = await api.get('/gamification/stats');
      setXpStats(response.data);
    } catch (err) {
      console.error('Error fetching xp stats:', err);
    }
  };

  const handleResumeUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      alert('Please upload a PDF file.');
      return;
    }

    setUploading(true);
    try {
      const result = await profileAPI.uploadResume(file);
      setProfile(result);
      fetchXpStats(); // Profile sync often awards XP

      console.log('--- AI Resume Extraction Debug ---');
      console.log('Raw Text Extracted:', result.raw_text);
      console.log('Skills Found:', result.extracted_skills);
      console.log('Interests Found:', result.extracted_interests);
      console.log('---------------------------------');

      const skillsMsg = result.extracted_skills?.length > 0
        ? `\n\nExtracted Skills: ${result.extracted_skills.join(', ')}`
        : '';
      const interestsMsg = result.extracted_interests?.length > 0
        ? `\nExtracted Interests: ${result.extracted_interests.join(', ')}`
        : '';

      alert(`Resume parsed successfully! Your profile has been updated with ${result.new_skills_count} new items.${skillsMsg}${interestsMsg}\n\nCheck browser console for full extraction details.`);
    } catch (error) {
      console.error('Error uploading resume:', error);
      alert('Failed to parse resume. Please try again or update manually.');
    } finally {
      setUploading(false);
    }
  };

  const removeItem = async (type, itemToRemove) => {
    const updatedList = profile[type].filter(item => item !== itemToRemove);
    try {
      const updatedProfile = await profileAPI.updateProfile({ [type]: updatedList });
      setProfile(updatedProfile);
    } catch (error) {
      console.error(`Error removing ${type}:`, error);
    }
  };

  const addItem = async (type, newItem) => {
    if (!newItem.trim()) return;
    const updatedList = [...(profile[type] || []), newItem.trim()];
    try {
      const updatedProfile = await profileAPI.updateProfile({ [type]: updatedList });
      setProfile(updatedProfile);
      if (type === 'skills') setNewSkill('');
      else setNewInterest('');
    } catch (error) {
      console.error(`Error adding ${type}:`, error);
    }
  };

  const toggleField = async (field) => {
    // Immediate UI feedback
    const originalProfile = { ...profile };
    const updatedValue = !profile[field];
    setProfile({ ...profile, [field]: updatedValue });

    try {
      await profileAPI.updateProfile({ [field]: updatedValue });

      if (field === 'low_bandwidth_mode') {
        localStorage.setItem('liteMode', updatedValue.toString());
        // Reload or update global state if needed
        window.location.reload();
      }
    } catch (error) {
      console.error(`Error toggling ${field}:`, error);
      setProfile(originalProfile); // Revert on failure
      alert(`Failed to update ${field}. Please try again.`);
    }
  };

  const requestNotificationPermission = async () => {
    if (!("Notification" in window)) {
      alert("This browser does not support desktop notifications.");
      return;
    }

    const permission = await Notification.requestPermission();
    if (permission === "granted") {
      alert("Notifications enabled! You will receive alerts for your registered hackathons.");
    } else {
      alert("Permission denied. You can enable notifications in your browser settings.");
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

          {xpStats && (
            <div className="profile-xp-card pixel-box">
              <div className="xp-stat-header">
                <span className="tier-name">{xpStats.tier_name}</span>
                <span className="xp-count">{xpStats.total_xp} XP</span>
              </div>
              <div className="profile-xp-bar">
                <div className="profile-xp-fill" style={{ width: `${xpStats.progress_pct}%` }} />
              </div>
              <div className="xp-streak">
                🔥 {xpStats.streak_days} Day Streak
              </div>
            </div>
          )}

          <div className="profile-actions-modern">
            <button
              className="btn-modern secondary resume-btn"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? (
                <>
                  <span className="loading-spinner-tiny"></span>
                  Parsing...
                </>
              ) : (
                <>
                  <span className="btn-icon">📄</span>
                  AI Resume Sync
                </>
              )}
            </button>
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: 'none' }}
              accept=".pdf"
              onChange={handleResumeUpload}
            />
          </div>
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
          <div className="profile-card">
            <div className="profile-card-header">
              <span className="profile-icon">💡</span>
              <h2>Interests</h2>
              <button
                className="edit-toggle-btn"
                onClick={() => setEditingInterests(!editingInterests)}
              >
                {editingInterests ? 'Close' : 'Edit'}
              </button>
            </div>
            <div className="profile-card-content">
              <div className="tags-list-modern">
                {(profile.interests || []).map((interest, index) => (
                  <span key={index} className="tag-modern">
                    {interest}
                    {editingInterests && (
                      <button className="tag-remove" onClick={() => removeItem('interests', interest)}>×</button>
                    )}
                  </span>
                ))}
                {(profile.interests || []).length === 0 && !editingInterests && (
                  <p className="empty-msg-tiny">No interests added yet. Click edit to add manually.</p>
                )}
              </div>
              {editingInterests && (
                <div className="tag-add-container">
                  <input
                    type="text"
                    placeholder="Add interest..."
                    value={newInterest}
                    onChange={(e) => setNewInterest(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addItem('interests', newInterest)}
                  />
                  <button onClick={() => addItem('interests', newInterest)}>+</button>
                </div>
              )}
            </div>
          </div>

          {/* Skills Section */}
          <div className="profile-card">
            <div className="profile-card-header">
              <span className="profile-icon">⚡</span>
              <h2>Skills</h2>
              <button
                className="edit-toggle-btn"
                onClick={() => setEditingSkills(!editingSkills)}
              >
                {editingSkills ? 'Close' : 'Edit'}
              </button>
            </div>
            <div className="profile-card-content">
              <div className="tags-list-modern">
                {(profile.skills || []).map((skill, index) => (
                  <span key={index} className="tag-modern">
                    {skill}
                    {editingSkills && (
                      <button className="tag-remove" onClick={() => removeItem('skills', skill)}>×</button>
                    )}
                  </span>
                ))}
                {(profile.skills || []).length === 0 && !editingSkills && (
                  <p className="empty-msg-tiny">No skills detected. Click edit to add manually.</p>
                )}
              </div>
              {editingSkills && (
                <div className="tag-add-container">
                  <input
                    type="text"
                    placeholder="Add skill..."
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addItem('skills', newSkill)}
                  />
                  <button onClick={() => addItem('skills', newSkill)}>+</button>
                </div>
              )}
            </div>
          </div>

          {/* Notifications Section */}
          <div className="profile-card">
            <div className="profile-card-header">
              <span className="profile-icon">🔔</span>
              <h2>Reminders</h2>
            </div>
            <div className="profile-card-content">
              {/* Notification Permission Banner */}
              {("Notification" in window) && Notification.permission !== "granted" && (
                <div className="notification-permission-banner pixel-box">
                  <p>Enable browser alerts for your hackathons?</p>
                  <button onClick={requestNotificationPermission} className="btn-modern tiny primary">
                    Enable Alerts
                  </button>
                </div>
              )}

              <div className="reminders-list-modern">
                {notifications.length > 0 ? notifications.map((n, i) => (
                  <div key={i} className="reminder-item-tiny">
                    <span className="reminder-dot"></span>
                    <div className="reminder-info-tiny">
                      <p className="reminder-msg-tiny">{n.message}</p>
                      <span className="reminder-time-tiny">
                        {new Date(n.scheduled_time).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                )) : (
                  <p className="empty-msg-tiny">No upcoming reminders.</p>
                )}
              </div>
              <div className="notification-toggles-tiny">
                <div className="profile-row-modern hoverable" onClick={() => toggleField('notification_email')}>
                  <span>Email Alerts</span>
                  <span className={`profile-badge ${profile.notification_email ? 'active' : ''}`}>
                    {profile.notification_email ? 'On' : 'Off'}
                  </span>
                </div>
                <div className="profile-row-modern hoverable" onClick={() => toggleField('notification_sms')}>
                  <span>SMS Alerts</span>
                  <span className={`profile-badge ${profile.notification_sms ? 'active' : ''}`}>
                    {profile.notification_sms ? 'On' : 'Off'}
                  </span>
                </div>
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
              <div className="profile-row-modern hoverable" onClick={() => toggleField('low_bandwidth_mode')}>
                <span>Lite Mode</span>
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
