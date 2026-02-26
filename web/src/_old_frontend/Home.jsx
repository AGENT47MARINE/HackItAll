import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { opportunitiesAPI } from '../services/api';
import OpportunityCard from '../components/OpportunityCard';
import AsciiBackground from '../components/AsciiBackground';
import './Home.css';

export default function Home() {
  const [featuredOpportunities, setFeaturedOpportunities] = useState([]);
  const [trendingOpportunities, setTrendingOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadOpportunities();
  }, []);

  const loadOpportunities = async () => {
    try {
      // Load all opportunities (no auth required)
      const data = await opportunitiesAPI.search({});
      setFeaturedOpportunities(data.slice(0, 6));
      setTrendingOpportunities(data.slice(0, 10));
    } catch (error) {
      console.error('Error loading opportunities:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      window.location.href = `/opportunities?search=${encodeURIComponent(searchQuery)}`;
    }
  };

  const stats = [
    { label: 'Active Opportunities', value: '10,000+' },
    { label: 'Students Helped', value: '50,000+' },
    { label: 'Success Rate', value: '85%' },
  ];

  return (
    <div className="home-container">
      <AsciiBackground />
      
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Discover Your Next
            <span className="gradient-text"> Opportunity</span>
          </h1>
          <p className="hero-subtitle">
            HackItAll connects students with hackathons, scholarships, internships, and skill programs.
            <br />
            Browse freely. Register only when you're ready to track.
          </p>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="hero-search">
            <input
              type="text"
              placeholder="Search opportunities..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input-hero"
            />
            <button type="submit" className="search-button-hero">
              Search
            </button>
          </form>

          {/* Stats */}
          <div className="stats-grid">
            {stats.map((stat, index) => (
              <div key={index} className="stat-card glass-card">
                <div className="stat-value">{stat.value}</div>
                <div className="stat-label">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Opportunities */}
      <section className="featured-section">
        <div className="section-header">
          <h2 className="section-title">Featured Opportunities</h2>
          <Link to="/opportunities" className="view-all-link">
            View All →
          </Link>
        </div>

        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading opportunities...</p>
          </div>
        ) : (
          <div className="opportunities-carousel">
            {featuredOpportunities.map((opportunity) => (
              <OpportunityCard
                key={opportunity.id}
                opportunity={opportunity}
                featured
              />
            ))}
          </div>
        )}
      </section>

      {/* Trending Section */}
      <section className="trending-section">
        <div className="section-header">
          <h2 className="section-title">Trending This Week</h2>
        </div>

        <div className="trending-grid">
          {trendingOpportunities.slice(0, 5).map((opp, index) => (
            <Link
              key={opp.id}
              to={`/opportunities/${opp.id}`}
              className="trending-item glass-card"
            >
              <div className="trending-rank">#{index + 1}</div>
              <div className="trending-content">
                <h3 className="trending-title">{opp.title}</h3>
                <span className="trending-type">{opp.type.replace('_', ' ')}</span>
              </div>
              <div className="trending-arrow">→</div>
            </Link>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section glass-card">
        <h2 className="cta-title">Want to track your applications?</h2>
        <p className="cta-subtitle">
          Create a free account to save opportunities, get deadline reminders,
          and receive personalized recommendations.
        </p>
        <Link to="/register" className="cta-button">
          Get Started →
        </Link>
      </section>
    </div>
  );
}
