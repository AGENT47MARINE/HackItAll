import { useState, useEffect } from 'react';
import { opportunitiesAPI } from '../services/api';
import OpportunityCard from '../components/OpportunityCard';
import './Pages.css';

export default function Opportunities() {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState(null);

  const types = ['hackathon', 'scholarship', 'internship', 'skill_program'];

  useEffect(() => {
    searchOpportunities();
  }, [selectedType]);

  const searchOpportunities = async () => {
    setLoading(true);
    try {
      const params = {};
      if (searchQuery) params.search = searchQuery;
      if (selectedType) params.type = [selectedType];

      const data = await opportunitiesAPI.search(params);
      setOpportunities(data);
    } catch (error) {
      console.error('Error searching opportunities:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    searchOpportunities();
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Search Opportunities</h1>
      </div>

      <div className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Search opportunities..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="search-button">
            Search
          </button>
        </form>

        <div className="filter-chips">
          <button
            className={`filter-chip ${!selectedType ? 'active' : ''}`}
            onClick={() => setSelectedType(null)}
          >
            All
          </button>
          {types.map((type) => (
            <button
              key={type}
              className={`filter-chip ${selectedType === type ? 'active' : ''}`}
              onClick={() => setSelectedType(type)}
            >
              {type.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="loading">Searching...</div>
      ) : opportunities.length === 0 ? (
        <div className="empty-state">
          <h2>No opportunities found</h2>
          <p>Try adjusting your search criteria</p>
        </div>
      ) : (
        <div className="opportunities-grid">
          {opportunities.map((opportunity) => (
            <OpportunityCard key={opportunity.id} opportunity={opportunity} />
          ))}
        </div>
      )}
    </div>
  );
}
