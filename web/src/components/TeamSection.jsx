import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { teamsAPI } from '../services/api';
import PremiumIcon from './PremiumIcon';
import './TeamSection.css';

export default function TeamSection({ opportunityId }) {
    const { isSignedIn, userId } = useAuth();
    const [teams, setTeams] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [creating, setCreating] = useState(false);

    // Form state
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [neededSkills, setNeededSkills] = useState('');
    const [maxMembers, setMaxMembers] = useState(4);

    useEffect(() => {
        loadTeams();
    }, [opportunityId]);

    const loadTeams = async () => {
        try {
            const data = await teamsAPI.getTeamsForOpportunity(opportunityId);
            setTeams(data);
        } catch (e) {
            console.error('Failed to load teams', e);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateTeam = async (e) => {
        e.preventDefault();
        if (!isSignedIn) return;

        setCreating(true);
        try {
            await teamsAPI.createTeam(opportunityId, {
                name,
                description,
                needed_skills: neededSkills,
                max_members: maxMembers
            });
            setShowCreateForm(false);
            setName('');
            setDescription('');
            setNeededSkills('');
            setMaxMembers(4);
            await loadTeams();
        } catch (e) {
            alert(e.response?.data?.detail || 'Failed to create team');
        } finally {
            setCreating(false);
        }
    };

    const handleJoinRequest = async (teamId) => {
        if (!isSignedIn) {
            alert('You must be signed in to join a team.');
            return;
        }

        const message = prompt('Leave a short message for the team leader:');
        if (message === null) return;

        try {
            await teamsAPI.requestToJoinTeam(teamId, message);
            alert('Join request sent successfully!');
        } catch (e) {
            alert(e.response?.data?.detail || 'Failed to send request');
        }
    };

    if (loading) {
        return <div className="team-loading">Loading teams...</div>;
    }

    return (
        <div className="team-section">
            <div className="team-header-row">
                <h2 className="detail-card-title flex items-center gap-3">
                    <PremiumIcon name="handshake" size={20} />
                    Find a Team
                </h2>
                {isSignedIn && !showCreateForm && (
                    <button
                        className="detail-button apply team-create-btn"
                        onClick={() => setShowCreateForm(true)}
                    >
                        + Create Team
                    </button>
                )}
            </div>

            {showCreateForm && (
                <form className="team-create-form" onSubmit={handleCreateTeam}>
                    <h3>Create a New Team</h3>
                    <input
                        type="text"
                        placeholder="Team Name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                        className="team-input"
                    />
                    <textarea
                        placeholder="Description (What are you building?)"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        className="team-input"
                        rows={3}
                    />
                    <input
                        type="text"
                        placeholder="Needed Skills (e.g., React, Python, UI/UX)"
                        value={neededSkills}
                        onChange={(e) => setNeededSkills(e.target.value)}
                        className="team-input"
                    />
                    <div className="team-form-actions">
                        <button type="submit" className="detail-button apply" disabled={creating}>
                            {creating ? 'Creating...' : 'Submit'}
                        </button>
                        <button type="button" className="detail-button save" onClick={() => setShowCreateForm(false)}>
                            Cancel
                        </button>
                    </div>
                </form>
            )}

            {teams.length === 0 ? (
                <div className="team-empty">
                    <p>No teams are currently looking for members.</p>
                    {!isSignedIn && <p>Sign in to create a team!</p>}
                </div>
            ) : (
                <div className="team-list">
                    {teams.map(team => (
                        <div key={team.id} className="team-card">
                            <div className="team-card-header">
                                <h4>{team.name}</h4>
                                <span className="team-capacity">Capacity: {team.max_members}</span>
                            </div>
                            {team.description && <p className="team-desc">{team.description}</p>}
                            {team.needed_skills && (
                                <div className="team-skills">
                                    <strong>Looking for:</strong> <span>{team.needed_skills}</span>
                                </div>
                            )}

                            {isSignedIn && team.leader_id !== userId && (
                                <button
                                    className="detail-button apply team-join-btn"
                                    onClick={() => handleJoinRequest(team.id)}
                                >
                                    Request to Join
                                </button>
                            )}
                            {team.leader_id === userId && (
                                <div className="team-leader-controls">
                                    <span className="team-leader-badge">You are the leader</span>
                                    <button
                                        className="detail-button save mt-2 w-full text-xs py-2 bg-blue-500/10 border-blue-500/30 flex items-center justify-center gap-2"
                                        onClick={() => window.location.href = `/teams/${team.id}/blueprint`}
                                    >
                                        <PremiumIcon name="rocket" size={14} />
                                        VIEW AI BATTLE PLAN
                                    </button>
                                    <button
                                        className="detail-button apply mt-2 w-full text-xs py-2 bg-purple-500/10 border-purple-500/30 flex items-center justify-center gap-2"
                                        style={{ color: '#a855f7' }}
                                        onClick={() => window.location.href = `/teams/${team.id}/pitch`}
                                    >
                                        <PremiumIcon name="lightning" size={14} />
                                        GO TO PITCH STUDIO
                                    </button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
