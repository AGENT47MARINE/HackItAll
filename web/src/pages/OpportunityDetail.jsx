import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { opportunitiesAPI, trackingAPI } from '../services/api';
import './Pages.css';

export default function OpportunityDetail({ isAuthenticated }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [opportunity, setOpportunity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadOpportunity();
  }, [id]);

  const loadOpportunity = async () => {
    try {
      const data = await opportunitiesAPI.getById(id);
      setOpportunity(data);
    } catch (error) {
      console.error('Error loading opportunity:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!isAuthenticated) {
      // Prompt user to register/login
      if (confirm('You need to create an account to save opportunities. Would you like to register now?')) {
        navigate('/register');
      }
      return;
    }

    setSaving(true);
    try {
      await trackingAPI.saveOpportunity(id);
      alert('Opportunity saved to your tracker!');
    } catch (error) {
      if (error.response?.status === 409) {
        alert('Opportunity already saved');
      } else {
        alert('Failed to save opportunity');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleApply = () => {
    window.open(opportunity.application_link, '_blank');
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return <div className="loading">Loading opportunity...</div>;
  }

  if (!opportunity) {
    return <div className="empty-state"><h2>Opportunity not found</h2></div>;
  }

  return (
    <div className="detail-container">
      <div className="detail-header">
        <h1>{opportunity.title}</h1>
        <span className="type-badge">{opportunity.type.replace('_', ' ')}</span>
      </div>

      <div className="detail-section">
        <h2>Deadline</h2>
        <p className="deadline-text">{formatDate(opportunity.deadline)}</p>
      </div>

      <div className="detail-section">
        <h2>Description</h2>
        <p>{opportunity.description}</p>
      </div>

      {opportunity.required_skills && opportunity.required_skills.length > 0 && (
        <div className="detail-section">
          <h2>Required Skills</h2>
          <div className="tags-list">
            {opportunity.required_skills.map((skill, index) => (
              <span key={index} className="tag">{skill}</span>
            ))}
          </div>
        </div>
      )}

      {opportunity.tags && opportunity.tags.length > 0 && (
        <div className="detail-section">
          <h2>Tags</h2>
          <div className="tags-list">
            {opportunity.tags.map((tag, index) => (
              <span key={index} className="tag">{tag}</span>
            ))}
          </div>
        </div>
      )}

      {opportunity.eligibility && (
        <div className="detail-section">
          <h2>Eligibility</h2>
          <p>{opportunity.eligibility}</p>
        </div>
      )}

      <div className="detail-actions">
        <button onClick={handleSave} disabled={saving} className="save-button">
          {saving ? 'Saving...' : isAuthenticated ? 'Save to Tracker' : 'Save (Login Required)'}
        </button>
        <button onClick={handleApply} className="apply-button">
          Apply Now
        </button>
      </div>
    </div>
  );
}
