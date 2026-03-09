import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { teamsAPI } from '../services/api';
import GridBackground from '../components/GridBackground';
import GlassSurface from '../components/GlassSurface';
import PremiumIcon from '../components/PremiumIcon';
import PixelLogo from '../components/PixelLogo';
import './Pages.css';

export default function SquadArchitectView() {
    const { teamId } = useParams();
    const navigate = useNavigate();
    const [blueprint, setBlueprint] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchBlueprint = async () => {
            try {
                const data = await teamsAPI.getBlueprint(teamId);
                setBlueprint(data);
            } catch (err) {
                console.error('Error fetching blueprint:', err);
                setError('Failed to generate your sprint blueprint.');
            } finally {
                setLoading(false);
            }
        };
        fetchBlueprint();
    }, [teamId]);

    if (loading) {
        return (
            <div className="detail-page">
                <GridBackground />
                <div className="detail-content flex flex-col items-center justify-center min-h-[60vh]">
                    <div className="loading-spinner-modern mb-6"></div>
                    <h2 className="text-xl text-white font-bold animate-pulse">Architecting your 48-hour victory...</h2>
                    <p className="text-white/40 mt-2">Optimizing roles and milestone distribution based on team skills.</p>
                </div>
            </div>
        );
    }

    if (error || !blueprint) {
        return (
            <div className="detail-page">
                <GridBackground />
                <div className="detail-content p-8 text-center">
                    <h2 className="text-2xl text-red-400 mb-4">Blueprint Restricted</h2>
                    <p className="text-white/60 mb-8">{error || "This strategic blueprint is only available to confirmed team members."}</p>
                    <button onClick={() => navigate(-1)} className="px-6 py-2 bg-white/10 rounded-full border border-white/20 hover:bg-white/20 transition-all">
                        ← Go Back
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="detail-page pb-20">
            <GridBackground />

            <div className="detail-content">
                <div className="mb-10 text-center animate-in">
                    <span className="px-4 py-1 bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-full text-xs font-bold uppercase tracking-widest flex items-center gap-2 w-fit mx-auto">
                        SQUAD ARCHITECT <span className="bg-blue-500 text-white px-1.5 py-0.5 rounded text-[8px]">PRO</span>
                    </span>
                    <h1 className="text-4xl md:text-5xl font-black text-white mt-4 tracking-tight uppercase">THE BATTLE PLAN</h1>
                    <p className="text-white/40 mt-2">Customized Strategy & Sprint Roadmap</p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                    {/* Left: Roles & Skeleton */}
                    <div className="lg:col-span-1 space-y-6 animate-in" style={{ animationDelay: '0.1s' }}>
                        <GlassSurface className="p-6" borderRadius={20} backgroundOpacity={0.05}>
                            <h3 className="text-blue-400 font-bold mb-6 flex items-center gap-3">
                                <PremiumIcon name="users" size={18} />
                                ROLE DEPLOYMENT
                            </h3>
                            <div className="space-y-4">
                                {Object.entries(blueprint.role_assignments).map(([name, role]) => (
                                    <div key={name} className="p-3 bg-white/5 rounded-xl border border-white/10">
                                        <div className="text-white font-bold">{name}</div>
                                        <div className="text-blue-300/60 text-sm">{role}</div>
                                    </div>
                                ))}
                            </div>
                        </GlassSurface>

                        <GlassSurface className="p-6" borderRadius={20} backgroundOpacity={0.05}>
                            <h3 className="text-purple-400 font-bold mb-6 flex items-center gap-3">
                                <PremiumIcon name="building" size={18} />
                                PROJECT SKELETON
                            </h3>
                            <div className="prose prose-invert prose-sm">
                                <pre className="bg-black/40 p-4 rounded-xl text-purple-200 border border-purple-500/10 overflow-x-auto whitespace-pre-wrap">
                                    {blueprint.suggested_skeleton}
                                </pre>
                            </div>
                        </GlassSurface>
                    </div>

                    {/* Right: Roadmap Timeline */}
                    <div className="lg:col-span-2 animate-in" style={{ animationDelay: '0.2s' }}>
                        <GlassSurface className="p-8" borderRadius={24} backgroundOpacity={0.08}>
                            <h3 className="text-green-400 font-bold mb-10 text-xl flex items-center gap-4">
                                <PremiumIcon name="sprint" size={24} />
                                THE 48-HOUR SPRINT
                            </h3>
                            <div className="space-y-12 relative">
                                {/* Vertical line */}
                                <div className="absolute left-[19px] top-4 bottom-4 w-0.5 bg-gradient-to-b from-green-500/50 via-blue-500/30 to-purple-500/10"></div>

                                {blueprint.roadmap.map((step, idx) => (
                                    <div key={idx} className="relative pl-12">
                                        <div className="absolute left-0 top-1 w-10 h-10 bg-black border-2 border-green-500/50 rounded-full flex items-center justify-center text-[10px] font-black text-green-400 z-10 shadow-[0_0_15px_rgba(34,197,94,0.3)]">
                                            {step.time.split(' ')[0]}
                                        </div>
                                        <div className="mb-1 text-xs font-bold text-green-500 uppercase tracking-widest">{step.time}</div>
                                        <h4 className="text-white text-xl font-bold mb-2">{step.task}</h4>
                                        <div className="inline-block px-3 py-1 bg-white/10 rounded-lg text-sm text-white/50 border border-white/5">
                                            <span className="font-bold text-white/70">Milestone:</span> {step.milestone}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </GlassSurface>
                    </div>

                </div>

                <div className="mt-12 text-center text-white/20 text-xs italic">
                    AI Roadmap generated based on team skill entropy and event complexity ratings.
                </div>
            </div>
        </div>
    );
}
