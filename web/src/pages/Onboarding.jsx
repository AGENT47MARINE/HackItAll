import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import api from '../services/api';
import GridBackground from '../components/GridBackground';
import PixelLogo from '../components/PixelLogo';
import './Auth.css';

const INTEREST_OPTIONS = [
    'Web Dev', 'App Dev', 'AI/ML', 'Data Science',
    'Cybersecurity', 'Cloud Computing', 'UI/UX Design',
    'Blockchain', 'Game Dev', 'DevOps'
];

const EDUCATION_OPTIONS = [
    'High School',
    'B.Tech 1st Year',
    'B.Tech 2nd Year',
    'B.Tech 3rd Year',
    'B.Tech 4th Year',
    'M.Tech',
    'Graduate/Alumni'
];

export default function Onboarding() {
    const { user, isLoaded } = useUser();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const [formData, setFormData] = useState({
        phone: '',
        education_level: 'B.Tech 1st Year',
        interests: []
    });

    // If the user already finished onboarding (doesn't have the default 'Not Specified' level)
    // redirect them immediately to the dashboard to prevent double-onboarding.
    useEffect(() => {
        const checkOnboardStatus = async () => {
            if (isLoaded && user) {
                try {
                    const res = await api.get('/auth/me');
                    if (res.data && res.data.education_level !== 'Not Specified') {
                        navigate('/discover');
                    }
                } catch (err) {
                    console.error("Failed to check profile status", err);
                }
            }
        };
        checkOnboardStatus();
    }, [isLoaded, user, navigate]);

    const handleInterestToggle = (interest) => {
        setFormData(prev => ({
            ...prev,
            interests: prev.interests.includes(interest)
                ? prev.interests.filter(i => i !== interest)
                : [...prev.interests, interest]
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // Send the onboarding fields to the Python backend to update the profile record
            await api.put('/profile', {
                phone: formData.phone || null,
                education_level: formData.education_level,
                interests: formData.interests,
                skills: [] // Default initialize to empty array for now
            });

            // Reroute them to the main app dashboard
            navigate('/discover');
        } catch (err) {
            console.error(err);
            setError('Failed to save profile. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (!isLoaded) return null;

    return (
        <div className="auth-container">
            <GridBackground />
            <div className="auth-content">
                <PixelLogo size="large" className="mb-8" />

                <div className="auth-card modern-glass overflow-y-auto max-h-[90vh]">
                    <div className="auth-header">
                        <h2 className="title-gradient">Complete Your Profile</h2>
                        <p className="text-secondary mt-2">Let's customize your HackItAll experience</p>
                    </div>

                    {error && <div className="auth-error">{error}</div>}

                    <form onSubmit={handleSubmit} className="auth-form space-y-6">

                        {/* Phone Number */}
                        <div className="form-group pb-4">
                            <label>Phone Number (Optional)</label>
                            <div className="input-wrapper">
                                <span className="input-icon">📱</span>
                                <input
                                    type="tel"
                                    placeholder="e.g. +1 555-0123"
                                    value={formData.phone}
                                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                />
                            </div>
                        </div>

                        {/* Year of Study */}
                        <div className="form-group pb-4">
                            <label>Current Year of Study</label>
                            <div className="input-wrapper select-wrapper">
                                <span className="input-icon">🎓</span>
                                <select
                                    className="modern-select"
                                    value={formData.education_level}
                                    onChange={(e) => setFormData({ ...formData, education_level: e.target.value })}
                                    required
                                >
                                    {EDUCATION_OPTIONS.map(opt => (
                                        <option key={opt} value={opt}>{opt}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        {/* Interests Grid */}
                        <div className="form-group pb-4">
                            <label>Areas of Interest</label>
                            <p className="text-sm text-secondary mb-3">Select the fields you want to discover opportunities for:</p>

                            <div className="tags-grid">
                                {INTEREST_OPTIONS.map(interest => (
                                    <button
                                        key={interest}
                                        type="button"
                                        onClick={() => handleInterestToggle(interest)}
                                        className={`interest-tag ${formData.interests.includes(interest) ? 'active' : ''}`}
                                    >
                                        {interest}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <button
                            type="submit"
                            className="auth-button primary-gradient mt-6"
                            disabled={loading || formData.interests.length === 0}
                        >
                            {loading ? (
                                <div className="loading-spinner-modern inline-block w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                            ) : (
                                'Start Exploring Opportunities'
                            )}
                        </button>
                        {formData.interests.length === 0 && (
                            <p className="text-xs text-center text-red-400 mt-2">Please select at least one interest.</p>
                        )}
                    </form>
                </div>
            </div>
        </div>
    );
}
