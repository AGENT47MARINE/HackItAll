import { useState, useEffect, useCallback, memo } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { opportunitiesAPI } from '../services/api';
import OpportunityCard from '../components/OpportunityCard';
import PremiumIcon from '../components/PremiumIcon';
import GridBackground from '../components/GridBackground';
import './Pages.css';

// Memoized wrapper so cards don't re-render when parent state changes
const RecommendationCard = memo(({ rec, index }) => {
    const opp = rec.opportunity || rec;
    const score = rec.relevance_score;
    const reasons = rec.match_reasons || [];

    return (
        <div
            className="animate-in"
            style={{
                animationDelay: `${index * 80}ms`,
                display: 'flex',
                flexDirection: 'column',
                cursor: 'pointer',
                position: 'relative',
                gap: '0.5rem',
            }}
            onClick={() => window.location.href = `/opportunities/${opp.id}`}
        >

            <OpportunityCard
                opportunity={opp}
                relevanceScore={score}
            />
            {reasons.length > 0 && (
                <div style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '0.4rem',
                    paddingLeft: '0.5rem',
                    paddingBottom: '0.25rem'
                }}>
                    {reasons.map((reason, ri) => (
                        <span key={ri} style={{
                            fontSize: '0.6rem',
                            fontWeight: 700,
                            color: 'rgba(255,255,255,0.35)',
                            background: 'rgba(255,255,255,0.03)',
                            border: '1px solid rgba(255,255,255,0.07)',
                            borderRadius: '100px',
                            padding: '0.15rem 0.6rem',
                        }}>
                            ✦ {reason}
                        </span>
                    ))}
                </div>
            )}
        </div>
    );
});
RecommendationCard.displayName = 'RecommendationCard';

export default function Discover() {
    const { isSignedIn } = useAuth();
    const [trending, setTrending] = useState([]);
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [recLoading, setRecLoading] = useState(false);

    useEffect(() => {
        const fetchTrending = async () => {
            setLoading(true);
            try {
                const trendingData = await opportunitiesAPI.getTrending();
                setTrending(trendingData);
            } catch (error) {
                console.error('Error fetching trending:', error);
            } finally {
                setLoading(false);
            }
        };

        const fetchRecommendations = async () => {
            if (!isSignedIn) return;
            setRecLoading(true);
            try {
                const recData = await opportunitiesAPI.getRecommendations();
                console.log('[ForYou] Raw recommendations response:', recData);
                setRecommendations(Array.isArray(recData) ? recData : []);
            } catch (error) {
                console.error('[ForYou] Error fetching recommendations:', error?.response?.data || error);
                setRecommendations([]);
            } finally {
                setRecLoading(false);
            }
        };

        fetchTrending();
        fetchRecommendations();
    }, [isSignedIn]);

    return (
        <div className="opportunities-page">
            <GridBackground />

            <div className="opportunities-content">

                {/* Personalized "For You" AI Section (Only visible if signed in) */}
                {isSignedIn && (
                    <div className="mb-24">
                        <div className="opportunities-header">
                            <h1 className="opportunities-title flex items-center gap-3">
                                For <span className="gradient-text">You</span>
                                <PremiumIcon name="target" size={24} />
                            </h1>
                            <p className="opportunities-subtitle">
                                Personalized matches based on your education and interests.
                            </p>
                        </div>

                        {recLoading ? (
                            <div className="loading-modern">
                                <div className="loading-spinner-modern"></div>
                                <p>Analyzing your profile...</p>
                            </div>
                        ) : recommendations.length === 0 ? (
                            <div style={{ minHeight: '200px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '1rem', border: '1px dashed rgba(255,255,255,0.07)', borderRadius: '20px', padding: '3rem' }}>
                                <PremiumIcon name="target" size={40} />
                                <p style={{ color: 'rgba(255,255,255,0.35)', fontWeight: 600, textAlign: 'center' }}>No personalized matches yet. Complete your profile to unlock AI recommendations!</p>
                            </div>
                        ) : (
                            <div style={{
                                background: 'rgba(255,255,255,0.03)',
                                border: '1px solid rgba(255,255,255,0.08)',
                                borderRadius: '24px',
                                padding: '2rem',
                            }}>
                                <div className="opportunities-grid-modern">
                                    {recommendations.map((rec, index) => (
                                        <RecommendationCard key={(rec.opportunity || rec).id} rec={rec} index={index} />
                                    ))}
                                </div>
                            </div>
                        )}

                        <div className="my-12 w-full h-px bg-white/10" />
                    </div>
                )}

                {/* Global Trending Section */}
                <div className="opportunities-header">
                    <h1 className="opportunities-title flex items-center gap-3">
                        Trending <span className="gradient-text">Now</span>
                        <PremiumIcon name="sprint" size={24} />
                    </h1>
                    <p className="opportunities-subtitle">
                        Opportunities with the highest engagement and active participants in the HackItAll community.
                    </p>
                </div>

                {loading ? (
                    <div className="loading-modern">
                        <div className="loading-spinner-modern"></div>
                        <p>Loading hot opportunities...</p>
                    </div>
                ) : trending.length === 0 ? (
                    <div className="empty-state-modern">
                        <div className="empty-icon">☄️</div>
                        <h2>Quiet around here...</h2>
                        <p>Check back later or track a new event!</p>
                    </div>
                ) : (
                    <div className="opportunities-grid-modern">
                        {trending.map((opportunity, index) => (
                            <div
                                key={opportunity.id}
                                className="animate-in"
                                style={{
                                    animationDelay: `${index * 100}ms`,
                                    display: 'block',
                                    textDecoration: 'none',
                                    color: 'inherit',
                                    cursor: 'pointer'
                                }}
                                onClick={() => window.location.href = `/opportunities/${opportunity.id}`}
                            >
                                <OpportunityCard opportunity={opportunity} />
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
