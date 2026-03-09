import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import PixelIcon from '../components/PixelIcon';
import './Leagues.css';

// Custom Badge mapping
const BADGE_MAP = {
    'first_steps': { title: 'First Steps', icon: 'runner' },
    'onboarding': { title: 'Citizen', icon: 'medal' },
    'tracker_10': { title: 'Bug Catcher', icon: 'bug' },
    'first_scrape': { title: 'Data Miner', icon: 'spider' },
    'content_10': { title: 'Knowledge Seeker', icon: 'books' },
    'analyze_5': { title: 'Strategist', icon: 'search' },
    'applied_5': { title: 'Form Filler', icon: 'books' },
    'accepted_1': { title: 'Golden Ticket', icon: 'circuit' },
    'completed_3': { title: 'Hat Trick', icon: 'crown' },
    'completed_10': { title: 'Legendary Dev', icon: 'skull' },
    'streak_7': { title: 'Week Warrior', icon: 'flame' },
    'streak_30': { title: 'Monthly Monster', icon: 'gem' },
};

const MOCK_BADGES = Object.keys(BADGE_MAP).map(id => ({ id, ...BADGE_MAP[id] }));

export default function Leagues() {
    const [stats, setStats] = useState(null);
    const [leaderboard, setLeaderboard] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [statsRes, leagueRes] = await Promise.all([
                    api.get('/gamification/stats'),
                    api.get('/gamification/leaderboard'),
                ]);

                setStats(statsRes.data);
                setLeaderboard(leagueRes.data);
            } catch (error) {
                console.error('Error fetching gamification data:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const getTierIconName = (tier) => {
        const names = {
            1: 'shield', 2: 'scroll', 3: 'portal', 4: 'circuit', 5: 'gem', 6: 'crown'
        };
        return names[tier] || 'shield';
    };

    const getTierColor = (tier) => {
        const colors = {
            1: 'var(--pixel-bronze)', 2: 'var(--pixel-silver)', 3: 'var(--pixel-gold)',
            4: 'var(--pixel-platinum)', 5: 'var(--pixel-diamond)', 6: 'var(--pixel-obsidian)'
        };
        return colors[tier] || '#fff';
    };

    if (loading) {
        return (
            <div className="leagues-page">
                <div className="leagues-header">
                    <h1 style={{ fontSize: '1rem' }}>LOADING GAME DATA...</h1>
                </div>
            </div>
        );
    }

    const s = stats || { total_xp: 0, league_tier: 1, tier_name: 'Bronze Byte', streak_days: 0, progress_pct: 0, unlocked_badges: [] };

    return (
        <div className="leagues-page">
            {/* Header */}
            <motion.div
                className="leagues-header"
                initial={{ y: -50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.8, type: 'spring' }}
            >
                <h1 className="pixel-title">YOUR LEAGUE</h1>
                <p className="leagues-subtitle">{s.tier_name}</p>
            </motion.div>

            <div className="leagues-grid">
                {/* Left Side: Tier and Progress */}
                <div className="leagues-main-content">
                    <motion.div
                        className="pixel-box tier-card"
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ delay: 0.2 }}
                    >
                        <div className="tier-badge-container" style={{ borderColor: getTierColor(s.league_tier) }}>
                            <PixelIcon
                                name={getTierIconName(s.league_tier)}
                                size={60}
                                color={getTierColor(s.league_tier)}
                                active={true}
                            />
                        </div>
                        <h2 className="tier-name" style={{ color: getTierColor(s.league_tier) }}>
                            Level {s.league_tier}: {s.tier_name}
                        </h2>

                        <div className="pixel-xp-container">
                            <div className="xp-label">
                                <span>EXP</span>
                                <span>{s.total_xp} / {s.next_tier_xp}</span>
                            </div>
                            <div className="pixel-xp-bar">
                                <div className="pixel-xp-fill" style={{ width: `${s.progress_pct}%` }} />
                            </div>
                        </div>

                        <div className="stats-row">
                            <div className="stat-item">
                                <div className="stat-value">{s.total_xp}</div>
                                <div className="stat-label">Total XP</div>
                            </div>
                            <div className="stat-item">
                                <div className="stat-value">
                                    <PixelIcon name="flame" size={24} color="var(--pixel-red)" active={s.streak_days > 0} />
                                    <span style={{ marginLeft: '5px' }}>{s.streak_days}</span>
                                </div>
                                <div className="stat-label">STREAK</div>
                            </div>
                            <div className="stat-item">
                                <div className="stat-value">
                                    <PixelIcon name="trophy" size={24} color="var(--pixel-gold)" active={true} />
                                    <span style={{ marginLeft: '5px' }}>#{s.rank || '—'}</span>
                                </div>
                                <div className="stat-label">RANK / {s.total_users || 100}</div>
                            </div>
                        </div>
                    </motion.div>

                    {/* Achievements Grid */}
                    <motion.div
                        className="pixel-box"
                        initial={{ y: 30, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.4 }}
                    >
                        <h3 className="leaderboard-title">ACHIEVEMENTS</h3>
                        <div className="achievements-grid">
                            {MOCK_BADGES.map((badge, idx) => {
                                const isUnlocked = s.unlocked_badges.includes(badge.id);
                                return (
                                    <div key={badge.id} className={`badge-slot ${isUnlocked ? 'unlocked' : ''}`}>
                                        <PixelIcon
                                            name={badge.icon}
                                            size={32}
                                            color={isUnlocked ? 'var(--pixel-green)' : '#555'}
                                            active={isUnlocked}
                                        />
                                        <span className="badge-title">{badge.title}</span>
                                    </div>
                                );
                            })}
                        </div>
                    </motion.div>
                </div>

                {/* Right Side: Leaderboard */}
                <motion.div
                    className="pixel-box leaderboard-panel"
                    initial={{ x: 50, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.3 }}
                >
                    <h3 className="leaderboard-title">LEADERBOARD</h3>
                    <div className="leader-list">
                        {leaderboard.length > 0 ? leaderboard.map((player, idx) => (
                            <div key={idx} className={`leader-item ${idx === 0 ? 'top-1' : ''}`}>
                                <span className="leader-rank">{idx + 1}</span>
                                <PixelIcon
                                    name={getTierIconName(player.tier)}
                                    size={20}
                                    color={getTierColor(player.tier)}
                                />
                                <div className="leader-info">
                                    <div className="leader-name">{player.email}</div>
                                    <div className="leader-xp">
                                        {player.xp} XP • {player.streak}
                                        <PixelIcon name="flame" size={12} color="var(--pixel-red)" className="streak-icon" />
                                    </div>
                                </div>
                            </div>
                        )) : (
                            <div style={{ opacity: 0.4, textAlign: 'center', margin: '2rem 0' }}>No Data Recorded</div>
                        )}
                    </div>

                    <div style={{ marginTop: 'auto', padding: '1rem', borderTop: '2px solid #222', textAlign: 'center' }}>
                        <p style={{ fontSize: '0.8rem', opacity: 0.6 }}>League resets in 4d 12h</p>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
