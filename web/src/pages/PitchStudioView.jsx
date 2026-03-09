import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { teamsAPI } from '../services/api';
import GridBackground from '../components/GridBackground';
import GlassSurface from '../components/GlassSurface';
import PremiumIcon from '../components/PremiumIcon';
import PixelLogo from '../components/PixelLogo';
import './Pages.css';

export default function PitchStudioView() {
    const { teamId } = useParams();
    const navigate = useNavigate();
    const [pitch, setPitch] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('script'); // 'script', 'elevator', 'slides'

    useEffect(() => {
        const fetchPitch = async () => {
            try {
                const data = await teamsAPI.getPitch(teamId);
                setPitch(data);
            } catch (err) {
                console.error('Error fetching pitch assets:', err);
                setError('Failed to generate your strategic pitch.');
            } finally {
                setLoading(false);
            }
        };
        fetchPitch();
    }, [teamId]);

    if (loading) {
        return (
            <div className="detail-page">
                <GridBackground />
                <div className="detail-content flex flex-col items-center justify-center min-h-[60vh]">
                    <div className="loading-spinner-modern mb-6"></div>
                    <h2 className="text-xl text-white font-bold animate-pulse">Crafting your winning narrative...</h2>
                    <p className="text-white/40 mt-2">Synthesizing tech data and judge preferences into a strategic script.</p>
                </div>
            </div>
        );
    }

    if (error || !pitch) {
        return (
            <div className="detail-page">
                <GridBackground />
                <div className="detail-content p-8 text-center">
                    <h2 className="text-2xl text-red-400 mb-4">Studio Locked</h2>
                    <p className="text-white/60 mb-8">{error || "Pitch assets are currently restricted to the team leader."}</p>
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

            <div className="detail-content container mx-auto px-4">
                <div className="mb-10 text-center animate-in">
                    <span className="px-4 py-1 bg-purple-500/20 text-purple-400 border border-purple-500/30 rounded-full text-xs font-bold uppercase tracking-widest flex items-center gap-2 w-fit mx-auto">
                        AI PITCH STUDIO <span className="bg-purple-500 text-white px-1.5 py-0.5 rounded text-[8px]">PRO</span>
                    </span>
                    <h1 className="text-4xl md:text-5xl font-black text-white mt-4 tracking-tight uppercase">THE WINNER'S PITCH</h1>
                    <p className="text-white/40 mt-2">High-Stakes Presentation Assets & Scripts</p>
                </div>

                {/* Tab Switcher */}
                <div className="flex justify-center gap-4 mb-10 overflow-x-auto pb-2">
                    {['elevator', 'script', 'slides'].map(tab => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`px-6 py-2 rounded-full border text-sm font-bold uppercase transition-all whitespace-nowrap flex items-center gap-2 ${activeTab === tab
                                ? 'bg-purple-500 text-white border-purple-400 shadow-[0_0_15px_rgba(168,85,247,0.4)]'
                                : 'bg-white/5 text-white/40 border-white/10 hover:bg-white/10'
                                }`}
                        >
                            {tab === 'elevator' ? <PremiumIcon name="lightning" size={14} /> : tab === 'script' ? <PremiumIcon name="scroll" size={14} /> : <PremiumIcon name="frame" size={14} />}
                            {tab === 'elevator' ? 'Elevator Pitch' : tab === 'script' ? 'Demo Script' : 'Slide Blueprint'}
                        </button>
                    ))}
                </div>

                <div className="max-w-4xl mx-auto">
                    {activeTab === 'elevator' && (
                        <GlassSurface className="p-8 border-l-4 border-l-purple-500 animate-in" backgroundOpacity={0.08} borderRadius={24}>
                            <h3 className="text-purple-400 font-bold mb-6 text-xl">THE 30-SECOND PITCH</h3>
                            <p className="text-white text-2xl font-medium leading-relaxed italic">
                                "{pitch.elevator_pitch}"
                            </p>
                            <div className="mt-8 p-4 bg-purple-500/10 rounded-xl border border-purple-500/20 text-xs text-purple-300">
                                <strong>Pro-Tip:</strong> Memorize this as your core 'Identity'. Use it whenever a judge walks past your booth.
                            </div>
                        </GlassSurface>
                    )}

                    {activeTab === 'script' && (
                        <GlassSurface className="p-8 animate-in" backgroundOpacity={0.08} borderRadius={24}>
                            <h3 className="text-blue-400 font-bold mb-6 text-xl">3-MINUTE DEMO WORKFLOW</h3>
                            <div className="prose prose-invert max-w-none">
                                <pre className="bg-black/40 p-6 rounded-xl text-blue-100 border border-blue-500/10 overflow-x-auto whitespace-pre-wrap font-mono leading-relaxed">
                                    {pitch.demo_script}
                                </pre>
                            </div>
                        </GlassSurface>
                    )}

                    {activeTab === 'slides' && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in">
                            {pitch.slide_blueprint.map((slide, idx) => (
                                <GlassSurface key={idx} className="p-6 h-full" backgroundOpacity={0.05} borderRadius={20}>
                                    <div className="text-white/20 font-black text-4xl mb-2">0{idx + 1}</div>
                                    <h4 className="text-white font-bold text-xl mb-3">{slide.title}</h4>
                                    <p className="text-white/60 text-sm mb-6 leading-relaxed">{slide.content}</p>
                                    <div className="mt-auto p-3 bg-white/5 rounded-lg border border-dashed border-white/10">
                                        <span className="text-[10px] font-bold text-purple-400 uppercase block mb-1">Visual Direction</span>
                                        <p className="text-white/40 text-xs italic">{slide.visual_tip}</p>
                                    </div>
                                </GlassSurface>
                            ))}
                        </div>
                    )}
                </div>

                {/* Audit CTA (Coming Next) */}
                <div className="mt-20 text-center opacity-40 hover:opacity-100 transition-opacity">
                    <p className="text-sm text-white/50 mb-4">Want to test your pitch against the AI Judge?</p>
                    <button className="px-8 py-3 bg-red-500/20 text-red-400 border border-red-500/30 rounded-full font-bold uppercase tracking-widest text-xs cursor-not-allowed flex items-center gap-2 mx-auto">
                        <PremiumIcon name="shield" size={16} />
                        AI JUDGE AUDIT (LOCKED)
                    </button>
                    <p className="text-[10px] mt-2 text-white/20 italic">Unlock this by finishing your draft submission.</p>
                </div>
            </div>
        </div>
    );
}
