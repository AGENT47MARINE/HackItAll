import { useState } from 'react';
import { Link } from 'react-router-dom';
import { authAPI } from '../services/api';
import './Auth.css';

export default function Register({ onLogin }) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    educationLevel: '',
    interests: '',
    skills: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      const userData = {
        email: formData.email,
        password: formData.password,
        education_level: formData.educationLevel,
        interests: formData.interests.split(',').map(i => i.trim()).filter(i => i),
        skills: formData.skills.split(',').map(s => s.trim()).filter(s => s),
        notification_email: true,
        notification_sms: false,
        low_bandwidth_mode: false,
      };

      await authAPI.register(userData);
      onLogin();
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">Create Account</h1>
        <p className="auth-subtitle">Join to discover opportunities</p>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="error-message">{error}</div>}

          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password (min 8 characters) *</label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="educationLevel">Education Level *</label>
            <input
              id="educationLevel"
              name="educationLevel"
              type="text"
              placeholder="e.g., High School, Undergraduate"
              value={formData.educationLevel}
              onChange={handleChange}
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="interests">Interests (comma-separated)</label>
            <input
              id="interests"
              name="interests"
              type="text"
              placeholder="e.g., AI, Web Development, Design"
              value={formData.interests}
              onChange={handleChange}
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="skills">Skills (comma-separated)</label>
            <input
              id="skills"
              name="skills"
              type="text"
              placeholder="e.g., Python, React, Figma"
              value={formData.skills}
              onChange={handleChange}
              disabled={loading}
            />
          </div>

          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? 'Creating account...' : 'Register'}
          </button>
        </form>

        <p className="auth-link">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}
