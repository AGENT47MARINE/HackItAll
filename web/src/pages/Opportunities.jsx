import { useState, useEffect } from 'react';
import { opportunitiesAPI } from '../services/api';
import OpportunityCard from '../components/OpportunityCard';
import GridBackground from '../components/GridBackground';
import './Pages.css';

export default function Opportunities() {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState(null);
  const [isAISearch, setIsAISearch] = useState(false);

  const types = ['hackathon', 'scholarship', 'internship', 'skill_program'];

  useEffect(() => {
    if (searchQuery || selectedType) {
      searchOpportunities();
    }
  }, [selectedType, isAISearch]);

  const searchOpportunities = async () => {
    setLoading(true);
    try {
      if (isAISearch && searchQuery) {
        const data = await opportunitiesAPI.semanticSearch(searchQuery);
        setOpportunities(data);
      } else {
        const params = {};
        if (searchQuery) params.search = searchQuery;
        if (selectedType) params.type = [selectedType];
        const data = await opportunitiesAPI.search(params);
        setOpportunities(data);
      }
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
    <div className="opportunities-page">
      <GridBackground />

      <div className="opportunities-content">
        {/* Header Section */}
        <div className="opportunities-header">
          <h1 className="opportunities-title">
            Explore
            <span className="gradient-text"> Opportunities</span>
          </h1>
          <p className="opportunities-subtitle">
            Search through thousands of hackathons, scholarships, internships, and skill programs
          </p>
        </div>

        {/* Search Section */}
        <div className="search-section-modern">
          <form onSubmit={handleSearch} className="search-form-modern">
            <input
              type="text"
              placeholder={isAISearch ? "Describe what you're looking for (e.g., 'beginner AI hackathons')..." : "Search by title, organization, or keywords..."}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input-modern"
            />
            <button type="submit" className="search-button-modern">
              {isAISearch ? '🪄 AI Search' : 'Search'}
            </button>
          </form>

          <div className="flex-center-between mt-12">
            <div className="filter-chips-modern">
              <button
                className={`filter-chip-modern ${!selectedType ? 'active' : ''}`}
                onClick={() => setSelectedType(null)}
              >
                All
              </button>
              {types.map((type) => (
                <button
                  key={type}
                  className={`filter-chip-modern ${selectedType === type ? 'active' : ''}`}
                  onClick={() => setSelectedType(type)}
                >
                  {type.replace('_', ' ')}
                </button>
              ))}
            </div>

            <div className={`ai-toggle-pill ${isAISearch ? 'active' : ''}`} onClick={() => setIsAISearch(!isAISearch)}>
              <span className="ai-toggle-icon">✨</span>
              <span className="ai-toggle-text">AI Mode</span>
              <div className="ai-toggle-switch">
                <div className="ai-toggle-handle" />
              </div>
            </div>
          </div>
        </div>

        {/* Results Section */}
        {loading ? (
          <div className="loading-modern">
            <div className="loading-spinner-modern"></div>
            <p>Searching opportunities...</p>
          </div>
        ) : opportunities.length === 0 ? (
          <div className="empty-state-modern">
            <div className="empty-icon">◇</div>
            <h2>No opportunities found</h2>
            <p>Try adjusting your search criteria or filters</p>
          </div>
        ) : (
          <>
            <div className="results-count">
              Found <span className="count-highlight">{opportunities.length}</span> opportunities
            </div>
            <div className="opportunities-grid-modern">
              {opportunities.map((opportunity) => (
                <div key={opportunity.id} style={{ display: 'block', textDecoration: 'none', color: 'inherit' }} onClick={() => window.location.href = `/opportunities/${opportunity.id}`} className="clickable-card-wrapper">
                  <OpportunityCard opportunity={opportunity} />
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
