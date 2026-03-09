import { Link } from 'react-router-dom';
import { useEffect, useState, memo, useMemo } from 'react';
import PremiumIcon from './PremiumIcon';
import PixelLogo from './PixelLogo';
import './OpportunityCard.css';

const OpportunityCard = memo(function OpportunityCard({ opportunity, relevanceScore, onRemove }) {
  const [offset, setOffset] = useState(157); // Circumference for r=25 is ~157
  const [imageError, setImageError] = useState(false);
  const [useLocalProxy, setUseLocalProxy] = useState(false);
  // Read once per mount — not on every render
  const isLiteMode = useMemo(() => localStorage.getItem('liteMode') === 'true', []);
  // Unique gradient ID per card to prevent SVG ID collisions causing global repaints
  const gradientId = useMemo(() => `score-gradient-${opportunity.id?.replace(/[^a-z0-9]/gi, '')}`, [opportunity.id]);

  useEffect(() => {
    // PRE-EMPTIVE PROXY: If we know the domain has CORS/Socket issues (like hacktoskill), proxy it immediately
    if (opportunity.image_url && (opportunity.image_url.includes('hacktoskill.com') || opportunity.image_url.includes('google.com'))) {
      console.log(`Pre-emptively proxying image for: ${opportunity.title}`);
      setUseLocalProxy(true);
    }
  }, [opportunity.image_url, opportunity.title]);

  const handleImageError = () => {
    if (!useLocalProxy && opportunity.image_url) {
      console.log(`Image failed, trying local proxy for: ${opportunity.title}`);
      setUseLocalProxy(true);
    } else {
      setImageError(true);
    }
  };

  useEffect(() => {
    if (relevanceScore) {
      const percentage = relevanceScore * 100;
      const progress = 157 - (percentage / 100) * 157;
      // Stagger animation slightly
      const timer = setTimeout(() => setOffset(progress), 100);
      return () => clearTimeout(timer);
    }
  }, [relevanceScore]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getDaysUntilDeadline = (deadline) => {
    const now = new Date();
    const deadlineDate = new Date(deadline);
    const diffTime = deadlineDate - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const daysLeft = getDaysUntilDeadline(opportunity.deadline);
  const isUrgent = daysLeft <= 7 && daysLeft > 0;
  const isExpired = daysLeft < 0;

  return (
    <div className={`opportunity-card ${isExpired ? 'expired' : ''} ${isLiteMode ? 'lite-card' : ''}`}>
      {/* Visual Match Score Ring (Stripes) */}
      {relevanceScore && (
        <div className="match-score-container" title={`${Math.round(relevanceScore * 100)}% Match`}>
          <svg className="match-ring-svg">
            <defs>
              <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#10b981" />
                <stop offset="100%" stopColor="#059669" />
              </linearGradient>
            </defs>
            <circle className="match-ring-bg" cx="27" cy="27" r="25" />
            <circle
              className="match-ring-fill"
              cx="27"
              cy="27"
              r="25"
              stroke={`url(#${gradientId})`}
              style={{ strokeDashoffset: offset }}
            />
          </svg>
          <span className="match-score-text">{Math.round(relevanceScore * 100)}%</span>
        </div>
      )}

      {!isLiteMode && (
        <div className="card-image-container">
          {opportunity.image_url && !imageError ? (
            <img
              src={useLocalProxy
                ? `/api/opportunities/proxy-image?url=${encodeURIComponent(opportunity.image_url)}`
                : opportunity.image_url}
              alt={opportunity.title}
              className="card-image"
              onError={handleImageError}
            />
          ) : (
            <div className="image-fallback">
              <PixelLogo />
            </div>
          )}
        </div>
      )}

      <div className="card-header">
        <span className="type-badge">{opportunity.type.replace('_', ' ')}</span>
        <div className="card-header-badges">
          {opportunity.source_registration_count > 0 && (
            <span className="global-badge flex items-center gap-1" title="Registered on Source Site">
              <PremiumIcon name="scroll" size={10} color="#fff" />
              {opportunity.source_registration_count.toLocaleString()}
            </span>
          )}
          {opportunity.participant_count > 0 && (
            <span className="participant-badge flex items-center gap-1" title="Active Participants">
              <PremiumIcon name="target" size={10} />
              {opportunity.participant_count}
            </span>
          )}
          {opportunity.tracked_count > 0 && (
            <span className="tracked-badge flex items-center gap-1" title="Saves">
              <PremiumIcon name="sprint" size={10} />
              {opportunity.tracked_count}
            </span>
          )}
        </div>
      </div>

      <Link to={`/opportunities/${opportunity.id}`} className="card-link">
        <h3 className="card-title">{opportunity.title}</h3>
      </Link>

      <p className="card-description">{opportunity.description}</p>

      <div className="card-footer">
        <div className="deadline-info">
          <span className={`deadline-label ${isUrgent ? 'urgent' : ''}`}>Deadline:</span>
          <span className={`deadline-date ${isUrgent ? 'urgent' : ''}`}>
            {formatDate(opportunity.deadline)}
          </span>
          {isExpired && <span className="expired-text">(Expired)</span>}
          {isUrgent && !isExpired && (
            <span className="urgent-text">({daysLeft} days left)</span>
          )}
        </div>
      </div>

      {opportunity.tags && opportunity.tags.length > 0 && (
        <div className="tags-container">
          {opportunity.tags.slice(0, 3).map((tag, index) => (
            <span key={index} className="tag">{tag}</span>
          ))}
          {opportunity.tags.length > 3 && (
            <span className="more-tags">+{opportunity.tags.length - 3} more</span>
          )}
        </div>
      )}

      <div className="card-cta flex items-center justify-center gap-2">
        <span className="register-text">Explore & Register</span>
        <PremiumIcon name="rocket" size={14} />
      </div>

      {onRemove && (
        <button onClick={(e) => { e.stopPropagation(); onRemove(opportunity.id); }} className="remove-button">
          Remove
        </button>
      )}
    </div>
  );
});

export default OpportunityCard;
