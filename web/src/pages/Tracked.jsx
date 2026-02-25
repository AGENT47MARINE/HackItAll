import { useState, useEffect } from 'react';
import { trackingAPI } from '../services/api';
import OpportunityCard from '../components/OpportunityCard';
import './Pages.css';

export default function Tracked() {
  const [tracked, setTracked] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTracked();
  }, []);

  const loadTracked = async () => {
    try {
      const data = await trackingAPI.getTracked();
      setTracked(data);
    } catch (error) {
      console.error('Error loading tracked opportunities:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (opportunityId) => {
    if (!confirm('Are you sure you want to remove this opportunity?')) {
      return;
    }

    try {
      await trackingAPI.removeTracked(opportunityId);
      setTracked(tracked.filter(t => t.opportunity_id !== opportunityId));
    } catch (error) {
      alert('Failed to remove opportunity');
    }
  };

  if (loading) {
    return <div className="loading">Loading saved opportunities...</div>;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Saved Opportunities</h1>
        <p>{tracked.length} {tracked.length === 1 ? 'opportunity' : 'opportunities'} tracked</p>
      </div>

      {tracked.length === 0 ? (
        <div className="empty-state">
          <h2>No saved opportunities</h2>
          <p>Save opportunities to track deadlines and get reminders</p>
        </div>
      ) : (
        <div className="opportunities-grid">
          {tracked.map((item) => (
            <OpportunityCard
              key={item.opportunity_id}
              opportunity={item.opportunity}
              onRemove={handleRemove}
            />
          ))}
        </div>
      )}
    </div>
  );
}
