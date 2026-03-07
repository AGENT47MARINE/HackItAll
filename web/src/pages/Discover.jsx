import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { opportunitiesAPI } from '../services/api';
import OpportunityCard from '../components/OpportunityCard';
import GridBackground from '../components/GridBackground';
import GlassSurface from '../components/GlassSurface';
import './Pages.css';

export default function Discover() {
    const { isSignedIn } = useAuth();
    const [trending, setTrending] = useState([]);
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [recLoading, setRecLoading] = useState(false);

    useEffect(() => {
        const fetchAll = async () => {
            setLoading(true);
            try {
                // Always fetch trending
                const trendingData = await opportunitiesAPI.getTrending();
                setTrending(trendingData);

                // If user is authenticated, fetch their personalized AI recommendations
                if (isSignedIn) {
                    setRecLoading(true);
                    const recData = await opportunitiesAPI.getRecommendations();
                    // Store the full recommendation object to get the score
                    setRecommendations(recData);
                    setRecLoading(false);
                }
            } catch (error) {
                console.error('Error fetching discover feed:', error);
                setRecLoading(false);
            } finally {
                setLoading(false);
            }
        };
        fetchAll();
    }, [isSignedIn]);

    return (
        <div className="opportunities-page">
            <GridBackground />

            <div className="opportunities-content">

                {/* Personalized "For You" AI Section (Only visible if signed in) */}
                {isSignedIn && (
                    <div className="mb-24">
                        <div className="opportunities-header">
                            <h1 className="opportunities-title">
                                For <span className="gradient-text">You 🎯</span>
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
                            <div className="empty-state-modern">
                                <p>No personalized matches found right now. Check back later!</p>
                            </div>
                        ) : (
                            <GlassSurface
                                width="100%"
                                height="auto"
                                borderRadius={24}
                                backgroundOpacity={0.02}
                                opacity={0.6}
                                blur={20}
                                className="p-8"
                            >
                                <div className="opportunities-grid-modern">
                                    {recommendations.map((rec, index) => (
                                        <div
                                            key={rec.opportunity.id}
                                            className="animate-in"
                                            style={{
                                                animationDelay: `${index * 150}ms`,
                                                display: 'block',
                                                textDecoration: 'none',
                                                color: 'inherit',
                                                cursor: 'pointer'
                                            }}
                                            onClick={() => window.location.href = `/opportunities/${rec.opportunity.id}`}
                                        >
                                            <OpportunityCard
                                                opportunity={rec.opportunity}
                                                relevanceScore={rec.relevance_score}
                                            />
                                        </div>
                                    ))}
                                </div>
                            </GlassSurface>
                        )}
                        <div className="my-12 w-full h-px bg-white/10" />
                    </div>
                )}

                {/* Global Trending Section */}
                <div className="opportunities-header">
                    <h1 className="opportunities-title">
                        Trending <span className="gradient-text">Now 🔥</span>
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
