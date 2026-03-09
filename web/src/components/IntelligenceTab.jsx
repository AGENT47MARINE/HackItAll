import React, { useState, useEffect } from 'react';
import { opportunitiesAPI } from '../services/api';
import GlassSurface from './GlassSurface';
import PremiumIcon from './PremiumIcon';
import './OpportunityCard.css'; // Reusing some glass styles

export default function IntelligenceTab({ opportunityId }) {
    const [scout, setScout] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchScout = async () => {
            setLoading(true);
            try {
                const data = await opportunitiesAPI.getScoutAnalysis(opportunityId);
                setScout(data);
            } catch (err) {
                console.error('Error fetching scout analysis:', err);
                setError('Failed to load strategic intelligence.');
            } finally {
                setLoading(false);
            }
        };
        fetchScout();
    }, [opportunityId]);

    if (loading) {
        return (
            <section className="mb-10 animate-in">
                <div className="flex items-center gap-3 mb-6">
                    <PremiumIcon name="shield" size={20} />
                    <h3 className="text-2xl font-black text-white tracking-tight uppercase">Intelligence Scout</h3>
                    <span className="bg-yellow-500/20 text-yellow-500 border border-yellow-500/30 px-2 py-0.5 rounded text-[10px] font-bold">PRO FEATURE</span>
                </div>
                <div className="p-8 text-center">
                    <div className="loading-spinner-modern mx-auto mb-4"></div>
                    <p className="text-white/50 animate-pulse">Analyzing past winners and judges criteria...</p>
                </div>
            </section>
        );
    }

    if (error || !scout) {
        return (
            <div className="p-8 text-center text-white/40">
                <p>{error || "No strategic data available for this event yet."}</p>
            </div>
        );
    }

    return (
        <div className="intelligence-container animate-in">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Winning Criteria */}
                <GlassSurface width="100%" height="auto" className="p-6" borderRadius={16} backgroundOpacity={0.05}>
                    <h3 className="text-blue-400 font-bold mb-4 flex items-center gap-3">
                        <PremiumIcon name="target" size={18} />
                        Winning Proof
                    </h3>
                    <p className="text-white/80 leading-relaxed italic">
                        "{scout.winning_criteria}"
                    </p>
                </GlassSurface>

                {/* Suggested Stack */}
                <GlassSurface width="100%" height="auto" className="p-6" borderRadius={16} backgroundOpacity={0.05}>
                    <h3 className="text-purple-400 font-bold mb-4 flex items-center gap-3">
                        <PremiumIcon name="tool" size={18} />
                        Winning Stack
                    </h3>
                    <div className="flex flex-wrap gap-2">
                        {scout.suggested_tech_stack.map(tech => (
                            <span key={tech} className="px-3 py-1 bg-purple-500/10 border border-purple-500/20 rounded-full text-xs text-purple-300">
                                {tech}
                            </span>
                        ))}
                    </div>
                    <p className="mt-4 text-xs text-white/40">
                        Based on technologies used by top 3 winners in similar events.
                    </p>
                </GlassSurface>

                {/* Strategic Alpha */}
                <div className="md:col-span-2">
                    <GlassSurface
                        width="100%"
                        height="auto"
                        className="p-8 border-l-4 border-l-yellow-500"
                        borderRadius={16}
                        backgroundOpacity={0.08}
                    >
                        <h3 className="text-yellow-500 font-black text-xl mb-4 flex items-center gap-3">
                            <PremiumIcon name="lightbulb" size={22} />
                            STRATEGIC ALPHA
                        </h3>
                        <p className="text-white text-lg font-medium leading-relaxed">
                            {scout.strategic_advice}
                        </p>
                    </GlassSurface>
                </div>

                {/* Track Insights */}
                <div className="md:col-span-2">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {Object.entries(scout.track_difficulty).map(([track, difficulty]) => (
                            <div key={track} className="flex justify-between items-center p-4 bg-white/5 rounded-lg border border-white/10">
                                <span className="text-white/70 font-medium">{track}</span>
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${difficulty === 'High' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'
                                    }`}>
                                    {difficulty} Competition
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

            </div>
        </div>
    );
}
