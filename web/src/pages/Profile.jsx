import { useState, useEffect, useRef } from 'react';
import api, { profileAPI } from '../services/api';
import GridBackground from '../components/GridBackground';
import PixelLogo from '../components/PixelLogo';
import './Pages.css';

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await profileAPI.getProfile();
      setProfile(data);
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
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
      const updatedProfile = await profileAPI.uploadResume(file);
      setProfile(updatedProfile);
      alert('Resume parsed successfully! Your profile has been updated.');
    } catch (error) {
      console.error('Error uploading resume:', error);
      alert('Failed to parse resume. Please try again or update manually.');
    } finally {
      setUploading(false);
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
