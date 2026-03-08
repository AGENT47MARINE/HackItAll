import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { teamsAPI } from '../services/api';
import GridBackground from '../components/GridBackground';
import GlassSurface from '../components/GlassSurface';
import PixelLogo from '../components/PixelLogo';
import './Pages.css';

export default function SubmissionAuditView() {
    const { teamId } = useParams();
    const navigate = useNavigate();

    const [auditData, setAuditData] = useState({
        title: '',
        description: '',
        github_url: ''
    });
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleAudit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const data = await teamsAPI.auditSubmission(teamId, auditData);
            setReport(data);
        } catch (err) {
            console.error('Audit failed:', err);
            setError('The AI Judge is currently unavailable. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="detail-page pb-20">
            <GridBackground />
            <div className="page-logo-watermark">
                <PixelLogo />
            </div>

            <div className="detail-content container mx-auto px-4">
                <div className="mb-10 text-center animate-in">
                    <span className="px-4 py-1 bg-red-500/20 text-red-400 border border-red-500/30 rounded-full text-xs font-bold uppercase tracking-widest flex items-center gap-2 w-fit mx-auto">
                        🛡️ AI JUDGE AUDIT <span className="bg-red-500 text-white px-1.5 py-0.5 rounded text-[8px]">PRO</span>
                    </span>
                    <h1 className="text-4xl md:text-5xl font-black text-white mt-4 tracking-tight uppercase">Quality Control</h1>
                    <p className="text-white/40 mt-2 italic">Pre-submission audit to maximize your winning probability.</p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">

                    {/* Left: Input Form */}
                    <div className="animate-in">
                        <GlassSurface className="p-8" borderRadius={24} backgroundOpacity={0.05}>
                            <h3 className="text-white font-bold mb-6 flex items-center gap-2">
                                📑 SUBMISSION DRAFT
                            </h3>
                            <form onSubmit={handleAudit} className="space-y-6">
                                <div>
                                    <label className="block text-white/50 text-xs font-bold uppercase mb-2">Project Title</label>
                                    <input
                                        type="text"
                                        required
                                        className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white focus:outline-none focus:border-red-500/50 transition-all"
                                        placeholder="Enter your project title..."
                                        value={auditData.title}
                                        onChange={(e) => setAuditData({ ...auditData, title: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-white/50 text-xs font-bold uppercase mb-2">Detailed Description</label>
                                    <textarea
                                        required
                                        rows={8}
                                        className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white focus:outline-none focus:border-red-500/50 transition-all font-sans text-sm"
                                        placeholder="Paste your submission readme or Devpost description here..."
                                        value={auditData.description}
                                        onChange={(e) => setAuditData({ ...auditData, description: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-white/50 text-xs font-bold uppercase mb-2">GitHub / Demo Link (Optional)</label>
                                    <input
                                        type="url"
                                        className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white focus:outline-none focus:border-red-500/50 transition-all"
                                        placeholder="https://github.com/..."
                                        value={auditData.github_url}
                                        onChange={(e) => setAuditData({ ...auditData, github_url: e.target.value })}
                                    />
                                </div>
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full py-4 bg-red-500 text-white font-black uppercase tracking-widest rounded-xl hover:bg-red-600 transition-all shadow-[0_0_20px_rgba(239,68,68,0.3)] flex items-center justify-center gap-3 disabled:opacity-50"
                                >
                                    {loading ? (
                                        <>
                                            <div className="loading-spinner-modern !w-5 !h-5 border-white/30 border-t-white"></div>
                                            AUDITING...
                                        </>
                                    ) : (
                                        <>🛡️ RUN AI JUDGE AUDIT</>
                                    )}
                                </button>
                            </form>
                        </GlassSurface>
                    </div>

                    {/* Right: Audit Results */}
                    <div className="animate-in" style={{ animationDelay: '0.1s' }}>
                        {report ? (
                            <div className="space-y-6">
                                {/* Probability Score */}
                                <GlassSurface className="p-8 text-center" borderRadius={24} backgroundOpacity={0.1}>
                                    <h4 className="text-white/40 text-xs font-bold uppercase mb-2">Winning Probability</h4>
                                    <div className="text-6xl font-black text-red-500 mb-2">
                                        {Math.round(report.winning_probability * 100)}%
                                    </div>
                                    <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)] transition-all duration-1000"
                                            style={{ width: `${report.winning_probability * 100}%` }}
                                        ></div>
                                    </div>
                                </GlassSurface>

                                {/* Red Flags */}
                                <GlassSurface className="p-6 border-l-4 border-l-red-500" borderRadius={16} backgroundOpacity={0.05}>
                                    <h3 className="text-red-500 font-bold mb-4 flex items-center gap-2">
                                        🚩 RED FLAGS
                                    </h3>
                                    <ul className="space-y-3">
                                        {report.red_flags.map((flag, i) => (
                                            <li key={i} className="text-white/80 text-sm flex gap-3">
                                                <span className="text-red-500">•</span> {flag}
                                            </li>
                                        ))}
                                    </ul>
                                </GlassSurface>

                                {/* Improvements */}
                                <GlassSurface className="p-6 border-l-4 border-l-yellow-500" borderRadius={16} backgroundOpacity={0.05}>
                                    <h3 className="text-yellow-500 font-bold mb-4 flex items-center gap-2">
                                        ✨ STRATEGIC FIXES
                                    </h3>
                                    <ul className="space-y-4">
                                        {report.improvements.map((fix, i) => (
                                            <li key={i} className="text-white/80 text-sm p-3 bg-white/5 rounded-lg border border-white/5 italic">
                                                "{fix}"
                                            </li>
                                        ))}
                                    </ul>
                                </GlassSurface>

                                {/* Judge Feedback */}
                                <GlassSurface className="p-6 border-l-4 border-l-blue-500" borderRadius={16} backgroundOpacity={0.05}>
                                    <h3 className="text-blue-400 font-bold mb-4 flex items-center gap-2">
                                        🧑‍⚖️ JUDGE PERSONA INSIGHT
                                    </h3>
                                    <p className="text-white/70 text-sm leading-relaxed">
                                        {report.judge_persona_feedback}
                                    </p>
                                </GlassSurface>
                            </div>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center p-12 text-center opacity-30 border-2 border-dashed border-white/10 rounded-3xl">
                                <div className="text-6xl mb-6">🛡️</div>
                                <h3 className="text-xl font-bold text-white mb-2">Audit Report Pending</h3>
                                <p className="text-white/60">Upload your submission details to receive a full audit from our AI Judges.</p>
                            </div>
                        )}
                    </div>

                </div>
            </div>
        </div>
    );
}
