import { motion } from 'framer-motion';
import { IconBolt, IconGrad, IconBriefcase, IconRocket } from './Icons';

const typeColors = {
    hackathon: { accent: '#00f0ff', bg: 'rgba(0, 240, 255, 0.06)', border: 'rgba(0, 240, 255, 0.15)' },
    scholarship: { accent: '#b266ff', bg: 'rgba(178, 102, 255, 0.06)', border: 'rgba(178, 102, 255, 0.15)' },
    internship: { accent: '#00ff88', bg: 'rgba(0, 255, 136, 0.06)', border: 'rgba(0, 255, 136, 0.15)' },
    skill_program: { accent: '#ffb800', bg: 'rgba(255, 184, 0, 0.06)', border: 'rgba(255, 184, 0, 0.15)' },
    default: { accent: '#ffffff', bg: 'rgba(255, 255, 255, 0.04)', border: 'rgba(255, 255, 255, 0.1)' }
};

const typeIcons = {
    hackathon: (c) => <IconBolt size={12} color={c} />,
    scholarship: (c) => <IconGrad size={12} color={c} />,
    internship: (c) => <IconBriefcase size={12} color={c} />,
    skill_program: (c) => <IconRocket size={12} color={c} />,
};

export default function EventCard({ event, index = 0 }) {
    const type = event.type?.toLowerCase() || 'default';
    const colors = typeColors[type] || typeColors.default;
    const renderIcon = typeIcons[type] || (() => <span style={{ color: colors.accent }}>◆</span>);

    const deadline = event.deadline ? new Date(event.deadline) : null;
    const daysLeft = deadline ? Math.max(0, Math.ceil((deadline - new Date()) / (1000 * 60 * 60 * 24))) : null;

    return (
        <motion.div
            className="event-card"
            style={{
                '--card-accent': colors.accent,
                '--card-bg': colors.bg,
                '--card-border': colors.border,
            }}
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            whileHover={{ y: -8, transition: { duration: 0.3 } }}
        >
            <div className="event-card-glow" />

            <div className="event-card-header">
                <span className="event-type-badge" style={{ color: colors.accent, borderColor: colors.border }}>
                    {renderIcon(colors.accent)} {type.replace('_', ' ')}
                </span>
                {daysLeft !== null && (
                    <span className={`event-deadline-badge ${daysLeft <= 7 ? 'urgent' : ''}`}>
                        {daysLeft === 0 ? 'Today!' : `${daysLeft}d left`}
                    </span>
                )}
            </div>

            <h3 className="event-card-title">{event.title || 'Unnamed Event'}</h3>

            <p className="event-card-description">
                {event.description?.slice(0, 100) || 'Discover this amazing opportunity and take the next step in your journey.'}
                {event.description?.length > 100 ? '...' : ''}
            </p>

            <div className="event-card-meta">
                {event.prize && (
                    <div className="event-meta-item">
                        <span className="meta-label">Prize</span>
                        <span className="meta-value" style={{ color: colors.accent }}>{event.prize}</span>
                    </div>
                )}
                {deadline && (
                    <div className="event-meta-item">
                        <span className="meta-label">Deadline</span>
                        <span className="meta-value">{deadline.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                    </div>
                )}
                {event.eligibility && (
                    <div className="event-meta-item">
                        <span className="meta-label">For</span>
                        <span className="meta-value">{event.eligibility}</span>
                    </div>
                )}
            </div>

            <div className="event-card-footer">
                <span className="event-card-link" style={{ color: colors.accent }}>
                    Learn more →
                </span>
            </div>
        </motion.div>
    );
}
