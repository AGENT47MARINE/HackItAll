import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { trackingAPI } from '../services/api';
import PremiumIcon from '../components/PremiumIcon';
import './TrackedDashboard.css';

// ── Particle Background (Constellation Effect) ────────────────
function ParticleCanvas() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animId;
    let particles = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    // Create particles
    for (let i = 0; i < 60; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        r: Math.random() * 1.5 + 0.5,
      });
    }

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Move and draw particles
      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255,255,255,0.15)';
        ctx.fill();
      });

      // Draw connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 150) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(255,255,255,${0.04 * (1 - dist / 150)})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }

      animId = requestAnimationFrame(draw);
    };

    draw();
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return <canvas ref={canvasRef} className="particle-bg" />;
}

// ── Timeline Component ──────────────────────────────────────────
const PHASES = ['Saved', 'Applied', 'Submitted', 'In Review', 'Result'];

function StatusTimeline({ status, round }) {
  const statusMap = {
    saved: 0,
    applied: 1,
    submitted: 2,
    in_review: 3,
    accepted: 4,
    rejected: 4,
    completed: 4,
  };
  const activeIdx = statusMap[(status || 'saved').toLowerCase()] ?? 0;

  return (
    <div className="status-timeline-container mb-12">
      <div className="card-timeline">
        {PHASES.map((_, i) => (
          <div
            className={`timeline-step ${i === PHASES.length - 1 ? 'last-step' : ''}`}
            key={i}
          >
            <div
              className={`timeline-dot ${i < activeIdx ? 'completed' : i === activeIdx ? 'active' : ''
                }`}
            />
            {i < PHASES.length - 1 && (
              <div className={`timeline-line ${i < activeIdx ? 'completed' : ''}`} />
            )}
          </div>
        ))}
      </div>
      <div className="timeline-labels text-[8px]">
        {PHASES.map((label, i) => (
          <div key={i} className={`timeline-label-wrapper ${i === activeIdx ? 'active' : ''}`}>
            {label}
            {i === activeIdx && round && round !== "1" && (
              <span className="round-badge ml-1">R{round}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Team Badge Component ──────────────────────────────────────
function TeamBadge({ status, onClick }) {
  const configs = {
    solo: { label: 'Solo', class: 'status-solo', name: 'target' },
    member: { label: 'In Team', class: 'status-member', name: 'users' },
    leader: { label: 'Team Leader', class: 'status-leader', name: 'shield' },
  };
  const config = configs[status] || configs.solo;

  return (
    <div className={`team-status-badge ${config.class} flex items-center gap-2`} onClick={onClick}>
      <PremiumIcon name={config.name} size={14} />
      <span className="status-label">{config.label}</span>
      {status === 'solo' && <span className="find-squad-nudge ml-1">Find Squad →</span>}
    </div>
  );
}

// ── Countdown helper ───────────────────────────────────────────
function getCountdown(deadline) {
  if (!deadline) return { text: '—', urgent: false };
  const now = new Date();
  const d = new Date(deadline);
  const diff = d - now;
  if (diff <= 0) return { text: 'Ended', urgent: false };
  const days = Math.floor(diff / 86400000);
  if (days > 14) return { text: `${days}d left`, urgent: false };
  if (days > 0) return { text: `${days}d left`, urgent: days <= 3 };
  const hrs = Math.floor(diff / 3600000);
  return { text: `${hrs}h left`, urgent: true };
}

// ── Parse tags safely ──────────────────────────────────────────
function parseTags(tags) {
  if (!tags) return [];
  if (Array.isArray(tags)) return tags;
  try { return JSON.parse(tags); } catch { return []; }
}

// ── Main Component ─────────────────────────────────────────────
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
      console.error('Error loading tracked:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (item, newStatus) => {
    try {
      if (item.participation_id) {
        await trackingAPI.updateParticipation(item.participation_id, newStatus);
      } else {
        await trackingAPI.addParticipation(item.opportunity_id, newStatus);
      }
      loadTracked();
    } catch (error) {
      alert('Failed to update status.');
    }
  };

  const handleRoundUpdate = async (item) => {
    const currentRound = parseInt(item.current_round || "1");
    const nextRound = String(currentRound + 1);
    try {
      if (item.participation_id) {
        await trackingAPI.updateParticipation(item.participation_id, item.status, nextRound);
      } else {
        await trackingAPI.addParticipation(item.opportunity_id, item.status || 'applied', nextRound);
      }
      loadTracked();
    } catch (error) {
      console.error(error);
      alert('Failed to update round.');
    }
  };

  const handleRemove = async (opportunityId) => {
    if (!confirm('Remove this opportunity from your tracker?')) return;
    try {
      await trackingAPI.removeTracked(opportunityId);
      setTracked((prev) => prev.filter((t) => t.opportunity_id !== opportunityId));
    } catch {
      alert('Failed to remove.');
    }
  };

  const handleScrape = async (e) => {
    e.preventDefault();
    if (!scrapeUrl) return;
    setIsScraping(true);
    try {
      await trackingAPI.scrapeOpportunity(scrapeUrl);
      setScrapeUrl('');
      loadTracked();
    } catch (error) {
      alert(error.response?.status === 409
        ? 'Already tracking this!' : 'Failed to scrape.');
    } finally {
      setIsScraping(false);
    }
  };

  // Mouse glow-follow on cards
  const handleCardMouse = useCallback((e) => {
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();
    card.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
    card.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
  }, []);

  // ── Render ─────────────────────────────────────────────────
  return (
    <div className="tracked-dash">
      <ParticleCanvas />

      {/* Scraper Bar */}
      <div className="scraper-bar">
        <form className="scraper-glass" onSubmit={handleScrape}>
          <span className="scraper-icon">⌘</span>
          <input
            type="url"
            placeholder="Paste any hackathon URL to auto-track..."
            value={scrapeUrl}
            onChange={(e) => setScrapeUrl(e.target.value)}
            required
          />
          <button
            type="submit"
            disabled={isScraping}
            className={`scrape-btn ${isScraping ? 'loading' : ''}`}
          >
            {isScraping ? 'Scanning...' : 'Track'}
          </button>
        </form>
      </div>

      <div className="tracked-dash-content">
        {/* Header */}
        <div className="tracked-header-row">
          <h1 className="tracked-title">
            Tracked <span className="accent">Events</span>
          </h1>
          {!loading && (
            <span className="tracked-count-badge">
              {tracked.length} {tracked.length === 1 ? 'event' : 'events'}
            </span>
          )}
        </div>

        {/* Loading */}
        {loading && (
          <div className="tracked-loading-screen">
            <div className="loading-dna">
              <span /><span /><span /><span /><span />
            </div>
            <p>Syncing your events...</p>
          </div>
        )}

        {/* Empty */}
        {!loading && tracked.length === 0 && (
          <motion.div
            className="empty-state-dash"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <div className="empty-orbit">
              <div className="center-dot" />
              <div className="orbit-ring">
                <div className="orbit-dot" />
              </div>
            </div>
            <h2>No events tracked yet</h2>
            <p>Paste a hackathon URL above or save events from the Discover page to start tracking deadlines.</p>
          </motion.div>
        )}

        {/* Cards */}
        {!loading && tracked.length > 0 && (
          <AnimatePresence>
            <div className="tracked-cards-grid">
              {tracked.map((item, i) => {
                const opp = item.opportunity || {};
                const countdown = getCountdown(opp.deadline);
                const tags = parseTags(opp.tags);

                return (
                  <motion.div
                    key={item.opportunity_id || i}
                    className="tracked-glass-card"
                    onMouseMove={handleCardMouse}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ delay: i * 0.08, duration: 0.45 }}
                    style={{ animationDelay: `${i * 0.08}s` }}
                  >
                    {/* Top Row */}
                    <div className="card-top-row">
                      <span className="card-type-badge">{opp.type || 'event'}</span>
                      <span className={`card-countdown ${countdown.urgent ? 'urgent' : ''}`}>
                        {countdown.text}
                      </span>
                    </div>

                    {/* Title & Description */}
                    <h3 className="card-title">{opp.title || 'Untitled Event'}</h3>
                    <p className="card-description">{opp.description || ''}</p>

                    {/* Tags */}
                    {tags.length > 0 && (
                      <div className="card-tags">
                        {tags.slice(0, 4).map((tag, ti) => (
                          <span key={ti} className="card-tag">{tag}</span>
                        ))}
                      </div>
                    )}

                    {/* Team Status */}
                    <TeamBadge
                      status={item.team_status}
                      onClick={() => item.team_status === 'solo' && alert('AI: Analyzing skill gaps... This will open the Matchmaker modal!')}
                    />

                    {/* Timeline */}
                    <StatusTimeline status={item.status || 'saved'} round={item.current_round} />

                    {/* Round & Status Actions */}
                    <div className="status-quick-actions mb-4 flex flex-wrap gap-2">
                      <button
                        className={`status-chip ${item.status === 'applied' ? 'active' : ''}`}
                        onClick={() => handleStatusUpdate(item, 'applied')}
                      >
                        {item.status === 'applied' ? '✓ Applied' : 'Applied'}
                      </button>
                      <button
                        className={`status-chip ${item.status === 'submitted' ? 'active' : ''}`}
                        onClick={() => handleStatusUpdate(item, 'submitted')}
                      >
                        {item.status === 'submitted' ? '✓ Submitted' : 'Submitted'}
                      </button>
                      <button
                        className={`status-chip ${item.status === 'in_review' ? 'active' : ''}`}
                        onClick={() => handleStatusUpdate(item, 'in_review')}
                      >
                        {item.status === 'in_review' ? '✓ In Review' : 'In Review'}
                      </button>
                      <button
                        className={`status-chip ${item.status === 'accepted' ? 'active' : ''}`}
                        onClick={() => handleStatusUpdate(item, 'accepted')}
                      >
                        {item.status === 'accepted' ? '✓ Won' : 'Won'}
                      </button>
                      <button
                        className="round-chip"
                        onClick={() => handleRoundUpdate(item)}
                      >
                        + Round {parseInt(item.current_round || "1") + 1}
                      </button>
                    </div>

                    {/* Actions */}
                    <div className="card-actions">
                      <div className="flex flex-wrap gap-2 w-full justify-between items-center">
                        <div className="flex gap-2">
                          {opp.application_link && (
                            <a
                              href={opp.application_link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="card-action-btn visit-btn"
                            >
                              Visit ↗
                            </a>
                          )}
                          <button
                            className="card-action-btn remove-btn"
                            onClick={() => handleRemove(item.opportunity_id)}
                          >
                            Remove
                          </button>
                        </div>

                        <div className="flex gap-2">
                          <button
                            className="card-action-btn audit-btn flex items-center justify-center gap-2"
                            onClick={() => window.location.href = `/teams/${item.team_id || 'PRO_LOCKED'}/pitch`}
                          >
                            <PremiumIcon name="lightning" size={14} />
                            Pitch <span className="text-[8px] bg-purple-500 text-white px-1 rounded ml-1">STUDIO</span>
                          </button>

                          <button
                            className="card-action-btn audit-btn flex items-center justify-center gap-2"
                            style={{ borderColor: '#ef4444', color: '#ef4444' }}
                            onClick={() => window.location.href = `/teams/${item.team_id || 'PRO_LOCKED'}/audit`}
                          >
                            <PremiumIcon name="shield" size={14} />
                            Audit <span className="text-[8px] bg-red-500 text-white px-1 rounded ml-1">JUDGE</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}
