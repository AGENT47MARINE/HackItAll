import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import './TrackEvent.css';

export default function TrackEvent() {
    const [searchParams] = useSearchParams();
    const eventUrl = searchParams.get('url') || '';
    const [loading, setLoading] = useState(true);
    const [eventData, setEventData] = useState(null);

    useEffect(() => {
        // Simulate parsing the URL
        const timer = setTimeout(() => {
            const domain = (() => {
                try { return new URL(eventUrl).hostname.replace('www.', ''); }
                catch { return 'unknown'; }
            })();

            setEventData({
                url: eventUrl,
                domain,
                title: inferTitle(eventUrl, domain),
                platform: inferPlatform(domain),
                status: 'detected',
            });
            setLoading(false);
        }, 1500);
        return () => clearTimeout(timer);
    }, [eventUrl]);

    return (
        <div className="track-page">
            {/* Subtle grid background */}
            <div className="track-grid-bg" />

            {/* Navigation */}
            <nav className="track-nav">
                <Link to="/" className="track-nav-brand">
                    <span style={{ color: '#00f0ff' }}>◆</span> HACKITALL
                </Link>
                <Link to="/" className="track-back-link">← Back to Home</Link>
            </nav>

            <div className="track-content">
                {loading ? (
                    <motion.div
                        className="track-loading"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                    >
                        <div className="track-spinner" />
                        <p className="track-loading-text">Analyzing event link...</p>
                        <code className="track-loading-url">{eventUrl}</code>
                    </motion.div>
                ) : (
                    <motion.div
                        className="track-result"
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                    >
                        {/* Status Bar */}
                        <div className="track-status-bar">
                            <span className="track-status-dot" />
                            <span>Event Detected</span>
                        </div>

                        {/* Event Card */}
                        <div className="track-event-card">
                            <div className="track-event-header">
                                <div className="track-platform-badge">{eventData.platform}</div>
                                <span className="track-event-domain">{eventData.domain}</span>
                            </div>

                            <h1 className="track-event-title">{eventData.title}</h1>

                            <div className="track-event-url-wrap">
                                <code className="track-event-url">{eventUrl}</code>
                            </div>

                            {/* Actions */}
                            <div className="track-actions">
                                <Link to="/register" className="track-action-btn primary">
                                    Sign Up to Track This Event
                                    <span className="btn-arrow">→</span>
                                </Link>
                                <a href={eventUrl} target="_blank" rel="noopener noreferrer" className="track-action-btn ghost">
                                    Visit Original Page ↗
                                </a>
                            </div>

                            {/* Features Preview */}
                            <div className="track-features-preview">
                                <h3>When you track this event, you'll get:</h3>
                                <div className="track-features-grid">
                                    <div className="track-feature-item">
                                        <span>🔔</span>
                                        <div>
                                            <strong>Deadline Reminders</strong>
                                            <p>7, 3, and 1 day before</p>
                                        </div>
                                    </div>
                                    <div className="track-feature-item">
                                        <span>📊</span>
                                        <div>
                                            <strong>Progress Tracking</strong>
                                            <p>Track your application status</p>
                                        </div>
                                    </div>
                                    <div className="track-feature-item">
                                        <span>👥</span>
                                        <div>
                                            <strong>Team Management</strong>
                                            <p>Organize with your team</p>
                                        </div>
                                    </div>
                                    <div className="track-feature-item">
                                        <span>📅</span>
                                        <div>
                                            <strong>Calendar Sync</strong>
                                            <p>Add to Google/Apple Calendar</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    );
}

function inferTitle(url, domain) {
    try {
        const path = new URL(url).pathname;
        const parts = path.split('/').filter(Boolean);
        if (parts.length > 0) {
            const last = parts[parts.length - 1];
            return last.replace(/[-_]/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        }
    } catch { }
    return `Event on ${domain}`;
}

function inferPlatform(domain) {
    if (domain.includes('devpost')) return 'Devpost';
    if (domain.includes('mlh')) return 'MLH';
    if (domain.includes('eventbrite')) return 'Eventbrite';
    if (domain.includes('hackerearth')) return 'HackerEarth';
    if (domain.includes('unstop')) return 'Unstop';
    if (domain.includes('github')) return 'GitHub';
    return 'External';
}
