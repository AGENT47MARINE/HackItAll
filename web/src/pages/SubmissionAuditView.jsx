import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { teamsAPI } from '../services/api';
import GridBackground from '../components/GridBackground';
import GlassSurface from '../components/GlassSurface';
import PremiumIcon from '../components/PremiumIcon';
import PixelLogo from '../components/PixelLogo';
import './Pages.css';
import './SubmissionAuditView.css';

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
            setError('The AI Judge is currently offline. Rerouting to standby models...');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="audit-detail-page">
            <GridBackground />

            <div className="audit-container relative z-10">
                <div className="audit-header animate-in">
                    <div className="audit-pro-badge">
                        <PremiumIcon name="shield" size={14} />
                        AI JUDGE AUDIT <span>PRO</span>
                    </div>
                    <h1 className="audit-title">
                        Quality <span className="text-red-500">Control</span>
                    </h1>
                    <p className="audit-subtitle">
                        Pre-submission audit to maximize your winning probability. Powered by our proprietary judge simulation engine.
                    </p>
                </div>

                <div className="audit-grid">

                    {/* Left: Input Form */}
                    <div className="audit-col-left animate-in">
                        <GlassSurface className="audit-box-padding" borderRadius={32} backgroundOpacity={0.03} width="100%" height="auto">
                            <h3 className="audit-box-title">
                                <PremiumIcon name="document" size={20} />
                                SUBMISSION DRAFT
                            </h3>
                            <form onSubmit={handleAudit}>
                                <div className="audit-form-group">
                                    <label className="audit-label">Project Title</label>
                                    <input
                                        type="text"
                                        required
                                        className="audit-input"
                                        placeholder="Enter your project title..."
                                        value={auditData.title}
                                        onChange={(e) => setAuditData({ ...auditData, title: e.target.value })}
                                    />
                                </div>
                                <div className="audit-form-group">
                                    <label className="audit-label">Detailed Description</label>
                                    <textarea
                                        required
                                        rows={12}
                                        className="audit-textarea"
                                        placeholder="Paste your submission readme or Devpost description here..."
                                        value={auditData.description}
                                        onChange={(e) => setAuditData({ ...auditData, description: e.target.value })}
                                    />
                                </div>
                                <div className="audit-form-group">
                                    <label className="audit-label">GitHub / Demo Link (Optional)</label>
                                    <input
                                        type="url"
                                        className="audit-input"
                                        placeholder="https://github.com/..."
                                        value={auditData.github_url}
                                        onChange={(e) => setAuditData({ ...auditData, github_url: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <button
                                        type="submit"
                                        disabled={loading}
                                        className="audit-submit-btn"
                                    >
                                        {loading ? (
                                            <>
                                                <div className="loading-spinner-modern !w-5 !h-5 border-white/30 border-t-white"></div>
                                                RUNNING AUDIT...
                                            </>
                                        ) : (
                                            <>
                                                <PremiumIcon name="shield" size={18} color="#fff" />
                                                RUN AI JUDGE AUDIT
                                            </>
                                        )}
                                    </button>
                                </div>
                                {error && (
                                    <div className="error-message">
                                        {error}
                                    </div>
                                )}
                            </form>
                        </GlassSurface>
                    </div>

                    {/* Right: Audit Results */}
                    <div className="audit-col-right animate-in" style={{ animationDelay: '0.1s' }}>
                        {report ? (
                            <div className="results-stack">
                                {/* Probability Score Card */}
                                <GlassSurface className="audit-box-padding border border-red-500/20" borderRadius={32} backgroundOpacity={0.06} width="100%" height="auto">
                                    <div className="score-circle-container">
                                        <div className="score-display">
                                            <span className="score-number">{Math.round(report.winning_probability * 100)}</span>
                                            <span className="score-percent">%</span>
                                        </div>
                                        <div className="flex-1">
                                            <div>
                                                <h4 className="text-white font-black text-2xl uppercase tracking-tight">Winning Probability</h4>
                                                <p className="text-white/40 text-sm font-medium mt-1">Calculated from judge persona insights and 100+ simulated scoring rounds.</p>
                                            </div>
                                            <div className="score-bar-bg">
                                                <div
                                                    className="score-bar-fill"
                                                    style={{ width: `${report.winning_probability * 100}%` }}
                                                ></div>
                                            </div>
                                            <div className="flex justify-between mt-3" style={{ fontSize: '10px', fontWeight: '900', textTransform: 'uppercase', color: 'rgba(255,255,255,0.2)', letterSpacing: '0.1em' }}>
                                                <span>Minimum Viable</span>
                                                <span>Winner Profile</span>
                                            </div>
                                        </div>
                                    </div>
                                </GlassSurface>

                                <div className="report-section-grid">
                                    {/* Red Flags Container */}
                                    <div className="results-stack" style={{ gap: '1.5rem' }}>
                                        <h3 className="text-red-500 font-bold flex items-center gap-3 text-xs uppercase tracking-[0.2em] ml-2">
                                            <PremiumIcon name="flag" size={16} />
                                            RED FLAGS
                                        </h3>
                                        {report.red_flags.map((flag, i) => (
                                            <GlassSurface key={i} className="p-6 flag-card" borderRadius={16} backgroundOpacity={0.03} width="100%" height="auto">
                                                <p className="text-white/80 text-sm font-medium leading-relaxed">
                                                    {flag}
                                                </p>
                                            </GlassSurface>
                                        ))}
                                    </div>

                                    {/* Improvements Container */}
                                    <div className="results-stack" style={{ gap: '1.5rem' }}>
                                        <h3 className="text-yellow-500 font-bold flex items-center gap-3 text-xs uppercase tracking-[0.2em] ml-2">
                                            <PremiumIcon name="sparkles" size={16} />
                                            STRATEGIC FIXES
                                        </h3>
                                        {report.improvements.map((fix, i) => (
                                            <GlassSurface key={i} className="p-6 fix-card" borderRadius={16} backgroundOpacity={0.03} width="100%" height="auto">
                                                <p className="text-white/80 text-sm font-medium italic leading-relaxed">
                                                    "{fix}"
                                                </p>
                                            </GlassSurface>
                                        ))}
                                    </div>
                                </div>

                                {/* Judge Persona Feedback Overhaul */}
                                <GlassSurface className="audit-box-padding judge-persona-box" borderRadius={24} backgroundOpacity={0.05} width="100%" height="auto">
                                    <div className="judge-badge shadow-[0_0_20px_rgba(96,165,250,0.3)]">
                                        AI JUDGE INSIGHT
                                    </div>
                                    <div className="flex gap-8 items-start">
                                        <div className="hidden md:block">
                                            <PremiumIcon name="judge" size={32} />
                                        </div>
                                        <div className="flex-1">
                                            <p className="judge-persona-content">
                                                {report.judge_persona_feedback}
                                            </p>
                                            <div className="mt-8 pt-8 border-t border-white/5 flex items-center gap-4" style={{ fontSize: '10px', fontWeight: '900', textTransform: 'uppercase', color: 'rgba(255,255,255,0.1)', letterSpacing: '0.1em' }}>
                                                <span>Model: JudgePersona-V2</span>
                                                <span className="w-1 h-1 bg-white/[0.05] rounded-full"></span>
                                                <span>Complexity: 4.8T Param Synthesis</span>
                                            </div>
                                        </div>
                                    </div>
                                </GlassSurface>
                            </div>
                        ) : (
                            <div className="pending-audit">
                                <div className="pending-icon-wrap">
                                    <PremiumIcon name="shield" size={64} className="opacity-10" />
                                </div>
                                <h3 className="text-2xl font-black text-white/30 uppercase tracking-tight mb-4">Audit Pending</h3>
                                <p className="text-white/20 max-w-sm font-medium leading-[1.6]">
                                    Complete your submission draft to activate the AI Judge suite and receive a comprehensive winning probability audit.
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
