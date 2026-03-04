import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import './OpportunityCard.css';

export default function OpportunityCard({ opportunity, relevanceScore, onRemove }) {
  const [offset, setOffset] = useState(157); // Circumference for r=25 is ~157

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
    <div className={`opportunity-card ${isExpired ? 'expired' : ''}`}>
      {/* Visual Match Score Ring (Stripes) */}
      {relevanceScore && (
        <div className="match-score-container" title={`${Math.round(relevanceScore * 100)}% Match`}>
          <svg className="match-ring-svg">
            <defs>
              <linearGradient id="score-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#8833ff" />
                <stop offset="100%" stopColor="#3388ff" />
              </linearGradient>
            </defs>
            <circle className="match-ring-bg" cx="27" cy="27" r="25" />
            <circle
              className="match-ring-fill"
              cx="27"
              cy="27"
              r="25"
              style={{ strokeDashoffset: offset }}
            />
          </svg>
          <span className="match-score-text">{Math.round(relevanceScore * 100)}</span>
        </div>
      )}

      {opportunity.image_url && (
        <div className="card-image-container">
          <img src={opportunity.image_url} alt={opportunity.title} className="card-image" />
        </div>
      )}

      <div className="card-header">
        <span className="type-badge">{opportunity.type.replace('_', ' ')}</span>
        <div className="card-header-badges">
          {opportunity.tracked_count > 0 && (
            <span className="tracked-badge">🔥 {opportunity.tracked_count}</span>
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

      <a
        href={opportunity.application_link}
        target="_blank"
        rel="noopener noreferrer"
        className="explore-button"
        onClick={(e) => e.stopPropagation()}
      >
        Explore & Register 🚀
      </a>

      {onRemove && (
        <button onClick={(e) => { e.stopPropagation(); onRemove(opportunity.id); }} className="remove-button">
          Remove
        </button>
      )}
    </div>
  );
}
