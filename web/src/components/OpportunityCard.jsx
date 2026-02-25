import { Link } from 'react-router-dom';
import './OpportunityCard.css';

export default function OpportunityCard({ opportunity, relevanceScore, onRemove }) {
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
      <div className="card-header">
        <span className="type-badge">{opportunity.type.replace('_', ' ')}</span>
        {relevanceScore && (
          <span className="score-badge">{Math.round(relevanceScore * 100)}% match</span>
        )}
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

      {onRemove && (
        <button onClick={() => onRemove(opportunity.id)} className="remove-button">
          Remove
        </button>
      )}
    </div>
  );
}
