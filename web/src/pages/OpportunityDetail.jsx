import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@clerk/clerk-react';
import { opportunitiesAPI, trackingAPI } from '../services/api';
import GridBackground from '../components/GridBackground';
import PixelLogo from '../components/PixelLogo';
import TeamSection from '../components/TeamSection';
import './Pages.css';

export default function OpportunityDetail() {
  const { isSignedIn: isAuthenticated } = useAuth();
  const { id } = useParams();
  const navigate = useNavigate();
  const [opportunity, setOpportunity] = useState(null);
  const [fitAnalysis, setFitAnalysis] = useState(null);
  const [projectIdeas, setProjectIdeas] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [generatingIdeas, setGeneratingIdeas] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadOpportunity();
    if (isAuthenticated) {
      loadFitAnalysis();
      loadProjectIdeas();
    }
  }, [id, isAuthenticated]);

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

  const loadFitAnalysis = async () => {
    setAnalyzing(true);
    try {
      const data = await opportunitiesAPI.analyzeFit(id);
      setFitAnalysis(data);
    } catch (error) {
      console.error('Error analyzing fit:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const loadProjectIdeas = async () => {
    setGeneratingIdeas(true);
    try {
      const data = await opportunitiesAPI.getIdeas(id);
      setProjectIdeas(data.ideas);
    } catch (error) {
      console.error('Error fetching project ideas:', error);
    } finally {
      setGeneratingIdeas(false);
    }
  };

  const handleSave = async () => {
    if (!isAuthenticated) {
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
    return (
      <div className="detail-page">
        <GridBackground />
        <div className="detail-content">
          <div className="loading-modern">
            <div className="loading-spinner-modern"></div>
            <p>Loading opportunity...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!opportunity) {
    return (
      <div className="detail-page">
        <GridBackground />
        <div className="detail-content">
          <div className="empty-state-modern">
            <div className="empty-icon">◇</div>
            <h2>Opportunity not found</h2>
            <p>This opportunity may have been removed or doesn't exist</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="detail-page">
      <GridBackground />

      <div className="page-logo-watermark">
        <PixelLogo />
      </div>

      <div className="detail-content">
        {/* Hero Image */}
        {opportunity.image_url && (
          <div className="detail-hero-image-container">
            <img src={opportunity.image_url} alt={opportunity.title} className="detail-hero-image" />
            <div className="detail-hero-overlay"></div>
          </div>
        )}

        {/* Header */}
        <div className="detail-header-modern">
          <div className="detail-header-top">
            <h1 className="detail-title">{opportunity.title}</h1>
            <span className="type-badge-modern">{opportunity.type.replace('_', ' ')}</span>
          </div>
          <div className="detail-deadline">
            <span className="deadline-label">Deadline:</span>
            <span className="deadline-value">{formatDate(opportunity.deadline)}</span>
          </div>
        </div>

        {/* Content Grid */}
        <div className="detail-grid">

          {/* AI Fit Analysis */}
          {isAuthenticated && (analyzing || fitAnalysis) && (
            <div className={`detail-card ai-fit-card ${fitAnalysis?.is_ready ? 'ready' : (fitAnalysis ? 'not-ready' : '')}`}>
              <h2 className="detail-card-title">🤖 AI Fit Analysis</h2>
              {analyzing ? (
                <div className="analyzing-text">Analyzing your profile against this opportunity...</div>
              ) : (
                <>
                  <p className="detail-text ai-recommendation-text">{fitAnalysis.recommendation_text}</p>

                  {fitAnalysis.matching_skills?.length > 0 && (
                    <div className="fit-skills-group">
                      <h4 className="fit-skills-title">✅ Matching Skills</h4>
                      <div className="tags-list-modern">
                        {fitAnalysis.matching_skills.map(skill => <span key={skill} className="tag-modern skill-tag success">{skill}</span>)}
                      </div>
                    </div>
                  )}

                  {fitAnalysis.missing_skills?.length > 0 && (
                    <div className="fit-skills-group">
                      <h4 className="fit-skills-title">⚠️ Missing Skills</h4>
                      <div className="tags-list-modern">
                        {fitAnalysis.missing_skills.map(skill => <span key={skill} className="tag-modern skill-tag warning">{skill}</span>)}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {/* AI Project Ideas */}
          {isAuthenticated && (generatingIdeas || projectIdeas) && (
            <div className={`detail-card ai-ideas-card`}>
              <h2 className="detail-card-title">💡 Auto-Generated Project Ideas</h2>
              {generatingIdeas ? (
                <div className="analyzing-text">Brainstorming potential projects based on your skills...</div>
              ) : (
                <div className="ideas-list-modern">
                  {projectIdeas?.map((idea, index) => (
                    <div key={index} className="idea-item">
                      <h3 className="idea-title">{idea.title}</h3>
                      <p className="idea-desc">{idea.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Description */}
          <div className="detail-card">
            <h2 className="detail-card-title">Description</h2>
            <p className="detail-text">{opportunity.description}</p>
          </div>

          {/* Timeline */}
          {opportunity.timeline && opportunity.timeline.length > 0 && (
            <div className="detail-card timeline-card">
              <h2 className="detail-card-title">📅 Event Timeline</h2>
              <div className="vertical-timeline-modern">
                {opportunity.timeline.map((event, index) => (
                  <div key={index} className="timeline-item-modern">
                    <div className="timeline-dot-modern"></div>
                    <div className="timeline-content-modern">
                      <span className="timeline-label-modern">{event.label}</span>
                      <span className="timeline-date-modern">{formatDate(event.date)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Prizes */}
          {opportunity.prizes && opportunity.prizes.length > 0 && (
            <div className="detail-card prizes-card">
              <h2 className="detail-card-title">🏆 Prizes & Rewards</h2>
              <div className="prizes-grid-modern">
                {opportunity.prizes.map((prize, index) => (
                  <div key={index} className="prize-item-modern">
                    <div className="prize-icon-modern">✨</div>
                    <div className="prize-info-modern">
                      <span className="prize-label-modern">{prize.label}</span>
                      <span className="prize-value-modern">{prize.value}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Required Skills */}
          {opportunity.required_skills && opportunity.required_skills.length > 0 && (
            <div className="detail-card">
              <h2 className="detail-card-title">Required Skills</h2>
              <div className="tags-list-modern">
                {opportunity.required_skills.map((skill, index) => (
                  <span key={index} className="tag-modern skill-tag">{skill}</span>
                ))}
              </div>
            </div>
          )}

          {/* Eligibility */}
          {opportunity.eligibility && (
            <div className="detail-card">
              <h2 className="detail-card-title">Eligibility</h2>
              <p className="detail-text">{opportunity.eligibility}</p>
            </div>
          )}

          {/* Tags */}
          {opportunity.tags && opportunity.tags.length > 0 && (
            <div className="detail-card">
              <h2 className="detail-card-title">Tags</h2>
              <div className="tags-list-modern">
                {opportunity.tags.map((tag, index) => (
                  <span key={index} className="tag-modern">{tag}</span>
                ))}
              </div>
            </div>
          )}

          {/* Teams for Hackathons */}
          {opportunity.type === 'hackathon' && (
            <TeamSection opportunityId={opportunity.id} />
          )}
        </div>

        {/* Actions */}
        <div className="detail-actions-modern">
          <button onClick={handleSave} disabled={saving} className="detail-button save">
            {saving ? 'Saving...' : isAuthenticated ? '📌 Save to Tracker' : '📌 Save (Login Required)'}
          </button>
          <button onClick={handleApply} className="detail-button apply">
            Apply Now →
          </button>
        </div>
      </div>
    </div>
  );
}
