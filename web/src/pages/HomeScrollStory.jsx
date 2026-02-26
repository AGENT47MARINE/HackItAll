import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, useScroll, useTransform, useInView, AnimatePresence } from 'framer-motion';
import TerminalBackground from '../components/TerminalBackground';
import EventCard from '../components/EventCard';
import { IconBolt, IconBell, IconCpu, IconClock, IconUsers, IconCheck, IconMail, IconCalendar, IconEye, IconLink } from '../components/Icons';
import { opportunitiesAPI } from '../services/api';
import './HomeScrollStory.css';

// ─── Particle Canvas Background ────────────────────────────────────────────
function ParticleField() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let w = canvas.width = window.innerWidth;
    let h = canvas.height = window.innerHeight;
    let animId;

    const particles = Array.from({ length: 80 }, () => ({
      x: Math.random() * w,
      y: Math.random() * h,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      size: Math.random() * 1.5 + 0.5,
      opacity: Math.random() * 0.3 + 0.05,
    }));

    const draw = () => {
      ctx.clearRect(0, 0, w, h);

      // Grid pattern
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.015)';
      ctx.lineWidth = 0.5;
      const gridSize = 80;
      for (let x = 0; x < w; x += gridSize) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
      }
      for (let y = 0; y < h; y += gridSize) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
      }

      // Particles
      particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0) p.x = w;
        if (p.x > w) p.x = 0;
        if (p.y < 0) p.y = h;
        if (p.y > h) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${p.opacity})`;
        ctx.fill();
      });

      // Connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 150) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(255, 255, 255, ${0.03 * (1 - dist / 150)})`;
            ctx.stroke();
          }
        }
      }

      animId = requestAnimationFrame(draw);
    };

    draw();

    const onResize = () => {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', onResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', onResize);
    };
  }, []);

  return <canvas ref={canvasRef} className="particle-field" />;
}

// ─── Animated Counter ──────────────────────────────────────────────────────
function AnimatedCounter({ value, label, suffix = '' }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.5 });
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    if (!isInView) return;
    const num = parseInt(value.replace(/[^0-9]/g, ''));
    const duration = 2000;
    const start = Date.now();
    const timer = setInterval(() => {
      const elapsed = Date.now() - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.floor(num * eased));
      if (progress >= 1) clearInterval(timer);
    }, 16);
    return () => clearInterval(timer);
  }, [isInView, value]);

  return (
    <div className="stat-counter" ref={ref}>
      <span className="stat-number">{display.toLocaleString()}{suffix}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

// ─── Terminal Typing Effect ────────────────────────────────────────────────
function TerminalTyping() {
  const [lines, setLines] = useState([]);
  const [currentLine, setCurrentLine] = useState(0);
  const terminalRef = useRef(null);

  const terminalLines = [
    { type: 'prompt', text: '$ hackitall init my-project' },
    { type: 'output', text: '✓ Project initialized' },
    { type: 'output', text: '✓ Connected to HackItAll API' },
    { type: 'prompt', text: '$ hackitall search --type hackathon --status open' },
    { type: 'output', text: '' },
    { type: 'output', text: '  Found 247 active hackathons:' },
    { type: 'output', text: '' },
    { type: 'highlight', text: '  ┌──────────────────────────────────────┐' },
    { type: 'highlight', text: '  │  ⚡ MLH Global Hack 2025            │' },
    { type: 'highlight', text: '  │     Prize: $10,000  │  12 days left  │' },
    { type: 'highlight', text: '  └──────────────────────────────────────┘' },
    { type: 'output', text: '' },
    { type: 'highlight', text: '  ┌──────────────────────────────────────┐' },
    { type: 'highlight', text: '  │  🚀 Google Summer of Code            │' },
    { type: 'highlight', text: '  │     Stipend: $3,000 │  28 days left  │' },
    { type: 'highlight', text: '  └──────────────────────────────────────┘' },
    { type: 'output', text: '' },
    { type: 'prompt', text: '$ hackitall track --event "MLH Global Hack"' },
    { type: 'success', text: '✓ Event tracked! Reminders set for 7d, 3d, 1d before deadline' },
    { type: 'prompt', text: '$ _' },
  ];

  useEffect(() => {
    if (currentLine >= terminalLines.length) return;

    const line = terminalLines[currentLine];
    const delay = line.type === 'prompt' ? 60 : 25;
    const totalDelay = line.text.length * delay + 200;

    let chars = 0;
    const typeInterval = setInterval(() => {
      chars++;
      setLines(prev => {
        const copy = [...prev];
        copy[currentLine] = { ...line, text: line.text.slice(0, chars) };
        return copy;
      });
      if (chars >= line.text.length) {
        clearInterval(typeInterval);
      }
    }, delay);

    const nextTimer = setTimeout(() => {
      setCurrentLine(c => c + 1);
    }, totalDelay);

    return () => {
      clearInterval(typeInterval);
      clearTimeout(nextTimer);
    };
  }, [currentLine]);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [lines]);

  return (
    <div className="terminal-window-new">
      <div className="terminal-chrome">
        <div className="terminal-dots">
          <span className="tdot tdot-red" />
          <span className="tdot tdot-yellow" />
          <span className="tdot tdot-green" />
        </div>
        <span className="terminal-title-bar">hackitall — zsh — 80×24</span>
      </div>
      <div className="terminal-body-new" ref={terminalRef}>
        {lines.map((line, i) => (
          <div key={i} className={`terminal-line tl-${line.type}`}>
            {line.text}
          </div>
        ))}
        <div className="terminal-cursor" />
      </div>
    </div>
  );
}

// ─── Sample Events Data ────────────────────────────────────────────────────
const sampleEvents = [
  { id: 1, title: 'MLH Global Hack 2025', type: 'hackathon', deadline: '2025-04-15', prize: '$10,000', description: 'Build innovative solutions with 5,000+ hackers worldwide. 48-hour virtual hackathon with mentors from top tech companies.', eligibility: 'All students' },
  { id: 2, title: 'Google Summer of Code', type: 'internship', deadline: '2025-03-20', prize: '$3,000 stipend', description: 'Contribute to open-source projects under the guidance of expert mentors. A 12-week coding program.', eligibility: 'University students' },
  { id: 3, title: 'AWS AI/ML Scholarship', type: 'scholarship', deadline: '2025-05-01', prize: 'Full tuition', description: 'Comprehensive scholarship for students pursuing AI and machine learning research and education.', eligibility: 'Undergraduates' },
  { id: 4, title: 'NASA Space Apps Challenge', type: 'hackathon', deadline: '2025-10-05', prize: '$5,000', description: 'Solve real-world challenges using NASA open data. A global hackathon bringing together innovators.', eligibility: 'Everyone' },
  { id: 5, title: 'HackMIT 2025', type: 'hackathon', deadline: '2025-09-15', prize: '$7,500', description: 'Join 1,000+ hackers at MIT for a weekend of building and learning. Top prizes and recruiting.', eligibility: 'College students' },
  { id: 6, title: 'Meta University Internship', type: 'internship', deadline: '2025-02-28', prize: 'Paid internship', description: 'A 10-week internship at Meta for freshmen and sophomores from underrepresented communities.', eligibility: 'Freshmen/Sophomores' },
  { id: 7, title: 'CodePath Tech Fellowship', type: 'skill_program', deadline: '2025-06-15', prize: 'Free program', description: 'Industry-relevant technical courses with career coaching and mentorship from professionals.', eligibility: 'All levels' },
  { id: 8, title: 'Devpost AI Buildathon', type: 'hackathon', deadline: '2025-04-30', prize: '$15,000', description: 'Build AI-powered applications using cutting-edge APIs and tools. Virtual, team-based competition.', eligibility: 'Developers' },
];

// ─── Main Component ────────────────────────────────────────────────────────
export default function HomeScrollStory() {
  const [trackLink, setTrackLink] = useState('');
  const [events, setEvents] = useState(sampleEvents);
  const navigate = useNavigate();
  const containerRef = useRef(null);
  const eventsScrollRef = useRef(null);

  const { scrollYProgress } = useScroll();
  const progressWidth = useTransform(scrollYProgress, [0, 1], ['0%', '100%']);

  // Try to load real events from API
  useEffect(() => {
    const load = async () => {
      try {
        const data = await opportunitiesAPI.search({});
        if (data && data.length > 0) {
          setEvents(data.slice(0, 10));
        }
      } catch (e) {
        // fallback to sample data
      }
    };
    load();
  }, []);

  const handleTrackSubmit = (e) => {
    e.preventDefault();
    if (trackLink.trim()) {
      navigate(`/track?url=${encodeURIComponent(trackLink.trim())}`);
    }
  };

  // Horizontal scroll for events — passive:false needed to prevent page scroll
  useEffect(() => {
    const el = eventsScrollRef.current;
    if (!el) return;
    const handler = (e) => {
      if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
        e.preventDefault();
        el.scrollLeft += e.deltaY * 1.5;
      }
    };
    el.addEventListener('wheel', handler, { passive: false });
    return () => el.removeEventListener('wheel', handler);
  }, []);

  // Drag-to-scroll for events
  useEffect(() => {
    const el = eventsScrollRef.current;
    if (!el) return;
    let isDown = false, startX, scrollL;
    const onDown = (e) => { isDown = true; el.classList.add('dragging'); startX = e.pageX - el.offsetLeft; scrollL = el.scrollLeft; };
    const onLeave = () => { isDown = false; el.classList.remove('dragging'); };
    const onUp = () => { isDown = false; el.classList.remove('dragging'); };
    const onMove = (e) => { if (!isDown) return; e.preventDefault(); const x = e.pageX - el.offsetLeft; el.scrollLeft = scrollL - (x - startX) * 1.5; };
    el.addEventListener('mousedown', onDown);
    el.addEventListener('mouseleave', onLeave);
    el.addEventListener('mouseup', onUp);
    el.addEventListener('mousemove', onMove);
    return () => { el.removeEventListener('mousedown', onDown); el.removeEventListener('mouseleave', onLeave); el.removeEventListener('mouseup', onUp); el.removeEventListener('mousemove', onMove); };
  }, []);

  return (
    <div className="hia-container" ref={containerRef}>
      <ParticleField />

      {/* ─── Navigation ─────────────────────────────────────────────── */}
      <nav className="hia-nav">
        <Link to="/" className="hia-nav-brand">
          <span className="brand-glyph">◆</span>
          <span>HACKITALL</span>
        </Link>
        <div className="hia-nav-links">
          <Link to="/opportunities" className="hia-nav-link">Explore</Link>
          <Link to="/login" className="hia-nav-link">Sign In</Link>
          <Link to="/register" className="hia-nav-link hia-nav-cta">Get Started</Link>
        </div>
      </nav>

      {/* Removed -- no scroll progress bar */}

      {/* ═══════════════════════════════════════════════════════════════
           SECTION 1 — HERO
      ═══════════════════════════════════════════════════════════════ */}
      <section className="hia-section hia-hero">
        {/* Gradient blob orbs */}
        <div className="hero-blob hero-blob-1" />
        <div className="hero-blob hero-blob-2" />
        <div className="hero-blob hero-blob-3" />

        {/* Halftone dot texture overlay */}
        <div className="halftone-overlay" />
        {/* Terminal Background */}
        <div className="hia-hero-ascii-bg">
          <TerminalBackground />
        </div>

        {/* Foreground Content */}
        <div className="hia-hero-content">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            <div className="hia-hero-badge">
              <span className="badge-dot" />
              AI-Powered Opportunity Platform
            </div>
          </motion.div>

          {/* ASCII Block Art Logo */}
          <motion.pre
            className="hia-ascii-logo"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
          >
            {`██╗  ██╗ █████╗  ██████╗██╗  ██╗██╗████████╗ █████╗ ██╗     ██╗     
██║  ██║██╔══██╗██╔════╝██║ ██╔╝██║╚══██╔══╝██╔══██╗██║     ██║     
███████║███████║██║     █████╔╝ ██║   ██║   ███████║██║     ██║     
██╔══██║██╔══██║██║     ██╔═██╗ ██║   ██║   ██╔══██║██║     ██║     
██║  ██║██║  ██║╚██████╗██║  ██╗██║   ██║   ██║  ██║███████╗███████╗
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝`}
          </motion.pre>

          <motion.p
            className="hia-hero-sub"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.7 }}
          >
            Discover hackathons, scholarships, internships & skill programs.
            <br />
            Track deadlines. Never miss an opportunity.
          </motion.p>

          {/* ── Link Input Box ────────────────────────────────────── */}
          <motion.form
            className="hia-track-box"
            onSubmit={handleTrackSubmit}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.9 }}
          >
            <div className="track-input-wrap">
              <span className="track-input-icon"><IconLink size={16} color="rgba(255,255,255,0.4)" /></span>
              <input
                type="url"
                className="track-input"
                placeholder="Paste a hackathon or event link to start tracking..."
                value={trackLink}
                onChange={(e) => setTrackLink(e.target.value)}
              />
              <button type="submit" className="track-btn">
                Track Now
                <span className="track-btn-arrow">→</span>
              </button>
            </div>
            <p className="track-hint">
              Works with Devpost, MLH, Eventbrite, and 50+ platforms
            </p>
          </motion.form>

          {/* Scroll indicator */}
          <motion.div
            className="hia-scroll-hint"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5 }}
          >
            <div className="scroll-mouse">
              <div className="scroll-wheel" />
            </div>
            <span>Scroll to explore</span>
          </motion.div>
        </div>
      </section>

      {/* Wavy divider: Hero → Events */}
      <div className="wave-divider">
        <svg viewBox="0 0 1440 80" preserveAspectRatio="none">
          <path d="M0,40 C360,80 720,0 1080,40 C1260,60 1380,40 1440,40 L1440,80 L0,80 Z" fill="#050508" />
          <path d="M0,50 C320,10 640,70 960,30 C1200,5 1380,50 1440,35 L1440,80 L0,80 Z" fill="rgba(0,240,255,0.02)" />
        </svg>
      </div>

      {/* ═══════════════════════════════════════════════════════════════
           SECTION 2 — FEATURED EVENTS (Horizontal Scroll)
      ═══════════════════════════════════════════════════════════════ */}
      <section className="hia-section hia-events-section">
        <motion.div
          className="hia-section-header"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6 }}
        >
          <div className="section-label">
            <span className="label-line" />
            Featured Events
            <span className="label-line" />
          </div>
          <h2 className="section-heading">Opportunities for <span className="heading-accent">You</span></h2>
          <p className="section-sub">Curated hackathons, scholarships, and programs handpicked for students</p>
        </motion.div>

        <div
          className="hia-events-scroll"
          ref={eventsScrollRef}
        >
          <div className="hia-events-track">
            {events.map((event, i) => (
              <Link to={`/opportunities/${event.id}`} key={event.id} style={{ textDecoration: 'none' }}>
                <EventCard event={event} index={i} />
              </Link>
            ))}
          </div>
        </div>

        <div className="events-scroll-indicator">
          <span>← Scroll sideways to explore →</span>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════
           SECTION 3 — TERMINAL DEMO / HOW IT WORKS
      ═══════════════════════════════════════════════════════════════ */}
      <section className="hia-section hia-demo-section">
        <div className="hia-demo-grid">
          <motion.div
            className="demo-text-side"
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.7 }}
          >
            <div className="section-label">
              <span className="label-line" />
              How It Works
            </div>
            <h2 className="section-heading">
              Search. Track.<br />
              <span className="heading-accent">Never Miss Out.</span>
            </h2>
            <p className="section-sub">
              Browse thousands of opportunities without signing up. When you find something you love, track it with one click and get smart deadline reminders.
            </p>

            <div className="demo-features">
              <div className="demo-feature">
                <span className="feature-icon"><IconBolt size={22} color="#00f0ff" /></span>
                <div>
                  <strong>Instant Search</strong>
                  <p>Search across hackathons, scholarships, internships in seconds</p>
                </div>
              </div>
              <div className="demo-feature">
                <span className="feature-icon"><IconBell size={22} color="#7b61ff" /></span>
                <div>
                  <strong>Smart Reminders</strong>
                  <p>Get notified 7, 3, and 1 day before every deadline</p>
                </div>
              </div>
              <div className="demo-feature">
                <span className="feature-icon"><IconCpu size={22} color="#00ff88" /></span>
                <div>
                  <strong>AI Recommendations</strong>
                  <p>Personalized suggestions based on your interests and skills</p>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            className="demo-terminal-side"
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            <TerminalTyping />
          </motion.div>
        </div>
      </section>

      {/* Wavy divider: Demo → Tracking */}
      <div className="wave-divider wave-divider-flip">
        <svg viewBox="0 0 1440 60" preserveAspectRatio="none">
          <path d="M0,20 C480,60 960,0 1440,30 L1440,60 L0,60 Z" fill="#050508" />
          <path d="M0,30 C400,5 800,50 1200,15 C1350,5 1440,25 1440,25 L1440,60 L0,60 Z" fill="rgba(240,192,48,0.015)" />
        </svg>
      </div>
      {/* ═══════════════════════════════════════════════════════════════
           SECTION 4 — START TRACKING CTA
      ═══════════════════════════════════════════════════════════════ */}
      <section className="hia-section hia-tracking-section">
        <div className="tracking-glow-orb tracking-orb-1" />
        <div className="tracking-glow-orb tracking-orb-2" />

        <motion.div
          className="tracking-content"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.7 }}
        >
          <div className="section-label">
            <span className="label-line" />
            Start Tracking
            <span className="label-line" />
          </div>
          <h2 className="section-heading tracking-heading">
            Already participating in<br />
            a <span className="heading-accent">hackathon</span>?
          </h2>
          <p className="section-sub">
            Track your events, manage deadlines, and stay organized with your team.
            Get push notifications so you never miss a submission.
          </p>

          <div className="tracking-demo-cards">
            <motion.div
              className="tracking-card"
              whileHover={{ y: -4, scale: 1.02 }}
              transition={{ duration: 0.3 }}
            >
              <div className="tracking-card-status active">Active</div>
              <h4>MLH Global Hack 2025</h4>
              <div className="tracking-progress">
                <div className="tracking-progress-bar" style={{ width: '65%' }} />
              </div>
              <div className="tracking-card-meta">
                <span><IconClock size={14} color="rgba(255,255,255,0.5)" /> 12 days remaining</span>
                <span><IconUsers size={14} color="rgba(255,255,255,0.5)" /> Team of 4</span>
              </div>
            </motion.div>

            <motion.div
              className="tracking-card"
              whileHover={{ y: -4, scale: 1.02 }}
              transition={{ duration: 0.3 }}
            >
              <div className="tracking-card-status submitted">Submitted</div>
              <h4>Google Summer of Code</h4>
              <div className="tracking-progress">
                <div className="tracking-progress-bar completed" style={{ width: '100%' }} />
              </div>
              <div className="tracking-card-meta">
                <span><IconCheck size={14} color="#00ff88" /> Application submitted</span>
                <span><IconMail size={14} color="rgba(255,255,255,0.5)" /> Awaiting response</span>
              </div>
            </motion.div>

            <motion.div
              className="tracking-card"
              whileHover={{ y: -4, scale: 1.02 }}
              transition={{ duration: 0.3 }}
            >
              <div className="tracking-card-status upcoming">Upcoming</div>
              <h4>NASA Space Apps Challenge</h4>
              <div className="tracking-progress">
                <div className="tracking-progress-bar" style={{ width: '20%' }} />
              </div>
              <div className="tracking-card-meta">
                <span><IconCalendar size={14} color="rgba(255,255,255,0.5)" /> Starts in 45 days</span>
                <span><IconEye size={14} color="rgba(255,255,255,0.5)" /> Watching</span>
              </div>
            </motion.div>
          </div>

          <div className="tracking-cta-buttons">
            <Link to="/register" className="hia-btn hia-btn-primary">
              Start Tracking Free
              <span className="btn-glow" />
            </Link>
            <Link to="/opportunities" className="hia-btn hia-btn-ghost">
              Browse Events →
            </Link>
          </div>
        </motion.div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════
           SECTION 5 — STATS
      ═══════════════════════════════════════════════════════════════ */}
      <section className="hia-section hia-stats-section">
        <motion.div
          className="stats-grid"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6 }}
        >
          <AnimatedCounter value="10000" label="Active Opportunities" suffix="+" />
          <AnimatedCounter value="50000" label="Students Helped" suffix="+" />
          <AnimatedCounter value="85" label="Success Rate" suffix="%" />
          <AnimatedCounter value="200" label="Partner Platforms" suffix="+" />
        </motion.div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════
           SECTION 6 — FINAL CTA
      ═══════════════════════════════════════════════════════════════ */}
      <section className="hia-section hia-final-cta">
        <motion.div
          className="final-cta-content"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.7 }}
        >
          <h2 className="final-cta-heading">
            Your next opportunity<br />
            is <span className="heading-accent">waiting</span>.
          </h2>
          <p className="section-sub">
            Join thousands of students who discovered their next hackathon, scholarship, or internship through HackItAll.
          </p>
          <div className="final-cta-buttons">
            <Link to="/opportunities" className="hia-btn hia-btn-primary hia-btn-lg">
              Explore Opportunities
              <span className="btn-glow" />
            </Link>
            <Link to="/register" className="hia-btn hia-btn-ghost hia-btn-lg">
              Create Free Account →
            </Link>
          </div>
        </motion.div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════
           FOOTER
      ═══════════════════════════════════════════════════════════════ */}
      <footer className="hia-footer">
        <div className="footer-grid">
          <div className="footer-brand">
            <span className="hia-nav-brand">
              <span className="brand-glyph">◆</span> HACKITALL
            </span>
            <p className="footer-tagline">Your gateway to every opportunity.</p>
          </div>
          <div className="footer-links-group">
            <h4>Platform</h4>
            <Link to="/opportunities">Browse Events</Link>
            <Link to="/register">Create Account</Link>
            <Link to="/login">Sign In</Link>
          </div>
          <div className="footer-links-group">
            <h4>Resources</h4>
            <a href="#">How It Works</a>
            <a href="#">For Organizers</a>
            <a href="#">API Documentation</a>
          </div>
          <div className="footer-links-group">
            <h4>Connect</h4>
            <a href="#">GitHub</a>
            <a href="#">Discord</a>
            <a href="#">Twitter</a>
          </div>
        </div>
        <div className="footer-bottom">
          <span>© 2025 HackItAll. Built with ❤️ for students everywhere.</span>
        </div>
      </footer>
    </div>
  );
}
