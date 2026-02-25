import { useState, useEffect } from 'react';
import { opportunitiesAPI } from '../services/api';
import OpportunityCard from '../components/OpportunityCard';
import './Pages.css';

export default function Home() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      const data = await opportunitiesAPI.getRecommendations(20);
      setRecommendations(data);
    } catch (error) {
      console.error('Error loading recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading recommendations...</div>;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Recommended for You</h1>
        <p>Based on your interests and skills</p>
      </div>

      {recommendations.length === 0 ? (
        <div className="empty-state">
          <h2>No recommendations yet</h2>
          <p>Update your profile to get personalized recommendations</p>
        </div>
      ) : (
        <div className="opportunities-grid">
          {recommendations.map((item, index) => (
            <OpportunityCard
              key={`${item.opportunity.id}-${index}`}
              opportunity={item.opportunity}
              relevanceScore={item.relevance_score}
            />
          ))}
        </div>
      )}
    </div>
  );
}
