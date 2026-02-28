import { useState, useEffect } from 'react';
import { trackingAPI } from '../services/api';
import OpportunityCard from '../components/OpportunityCard';
import GridBackground from '../components/GridBackground';
import GlassSurface from '../components/GlassSurface';
import './Pages.css';

export default function Tracked() {
  const [tracked, setTracked] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scrapeUrl, setScrapeUrl] = useState('');
  const [isScraping, setIsScraping] = useState(false);

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

  const handleScrape = async (e) => {
    e.preventDefault();
    if (!scrapeUrl) return;
    setIsScraping(true);
    try {
      await trackingAPI.scrapeOpportunity(scrapeUrl);
      setScrapeUrl('');
      loadTracked(); // reload the list
    } catch (error) {
      if (error.response?.status === 409) {
        alert('You are already tracking this opportunity!');
      } else {
        alert('Failed to scrape or track opportunity.');
      }
    } finally {
      setIsScraping(false);
    }
  };

  if (loading) {
    return (
      <div className="tracked-page">
        <GridBackground />
        <div className="tracked-content">
          <div className="loading-modern">
            <div className="loading-spinner-modern"></div>
            <p>Loading saved opportunities...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="tracked-page">
      <GridBackground />



      <div className="tracked-content">
        {/* Header */}
        <div className="tracked-header">
          <h1 className="tracked-title">
            Saved
            <span className="gradient-text"> Opportunities</span>
          </h1>
          <p className="tracked-subtitle">
            {tracked.length} {tracked.length === 1 ? 'opportunity' : 'opportunities'} tracked
          </p>
        </div>

        {/* Scraper Input */}
        <div className="scraper-container" style={{ display: 'flex', justifyContent: 'center', margin: '2rem 0 3rem' }}>
          <GlassSurface
            width={600}
            height={80}
            borderRadius={20}
            borderWidth={0.05}
            brightness={40}
            opacity={0.8}
            blur={15}
            saturation={1.2}
            className="tracking-glass-surface"
          >
            <form className="scraper-form" onSubmit={handleScrape} style={{ width: '100%', margin: 0 }}>
              <input
                type="url"
                placeholder="Paste any hackathon URL here..."
                value={scrapeUrl}
                onChange={(e) => setScrapeUrl(e.target.value)}
                required
                className="scraper-input-modern"
                style={{ background: 'transparent', width: '100%' }}
              />
              <button type="submit" disabled={isScraping} className="scraper-btn-modern">
                {isScraping ? 'Scraping...' : 'Auto-Track'}
              </button>
            </form>
          </GlassSurface>
        </div>

        {/* Content */}
        {tracked.length === 0 ? (
          <div className="empty-state-modern">
            <div className="empty-icon">📌</div>
            <h2>No saved opportunities</h2>
            <p>Save opportunities to track deadlines and get reminders</p>
          </div>
        ) : (
          <div className="opportunities-grid-modern">
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
    </div>
  );
}
