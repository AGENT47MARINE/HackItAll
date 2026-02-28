import { useEffect, useRef, useState } from 'react';
import { IconBolt, IconRocket, IconCheck, IconMail, IconUsers, IconCalendar } from './Icons';
import './TerminalBackground.css';

const CODE_SNIPPETS = [
    [
        '$ hackitall init my-project',
        '[ICON_CHECK] Project scaffolded',
        '[ICON_CHECK] Dependencies installed',
        '',
        '$ npm run dev',
        '> hackitall@1.0.0 dev',
        '> vite',
        '',
        '  VITE v5.0.8  ready in 312ms',
        '  ➜ Local:   http://localhost:3000/',
        '  ➜ Network: use --host to expose',
    ],
    [
        '// Querying MongoDB for real-time hackathon matches',
        'const matches = await db.opportunities.find({',
        '  status: "open",',
        '  skills: { $in: ["React", "AI", "Python"] },',
        '  prize_pool: { $gte: 5000 }',
        '}).sort({ deadline: 1 }).limit(3);',
        '',
        'console.log(`Found ${matches.length} high-match events!`);',
        '[ICON_ROCKET] Initializing fast-track application sequence...',
    ],
    [
        '$ curl -X GET "https://api.hackitall.io/v1/events"',
        '  -H "Authorization: Bearer dev_token_89x"...',
        '',
        '{',
        '  "status": 200,',
        '  "data": [',
        '    {',
        '      "id": "evt_901",',
        '      "name": "Global AI Challenge",',
        '      "similarity_score": 0.98,',
        '      "action": "ready_to_track"',
        '    }',
        '  ]',
        '}',
        '[ICON_CHECK] Connection established. Latency: 24ms.',
    ],
    [
        '$ hackitall search --type hackathon',
        '',
        'Searching opportunities...',
        '',
        '┌─────────────────────────────────┐',
        '│ [ICON_BOLT] MLH Hackathon 2025           │',
        '│    Deadline: Apr 15, 2025       │',
        '│    Prize: $10,000               │',
        '└─────────────────────────────────┘',
        '┌─────────────────────────────────┐',
        '│ [ICON_ROCKET] NASA Space Apps Challenge    │',
        '│    Deadline: Oct 5, 2025        │',
        '│    Global Event                 │',
        '└─────────────────────────────────┘',
        '',
        'Found 247 results. Showing top 2.',
    ],
    [
        '[webpack-cli] Compilation starting...',
        '[ICON_CHECK] Compiling client-side modules',
        '[ICON_CHECK] Building static HTML pages',
        '[ICON_CHECK] Optimizing application assets',
        '',
        'Entrypoint main = main.b9f4a.js main.b9f4a.css',
        '[chunk] 894 modules transformed',
        '[chunk] 12 chunks generated',
        '',
        'webpack 5.89.0 compiled successfully in 1432 ms',
        '[ICON_ROCKET] Ready for production deployment.',
    ]
];

const NOTIFICATIONS = [
    { type: 'System', text: 'HackMIT 2025 Application Approved!', icon: 'mail', color: 'tl-green' },
    { type: 'Alert', text: 'Submission due in 12 hours (NASA Space Apps)', icon: 'calendar', color: 'tl-yellow' },
    { type: 'Team', text: 'Alex requested to join "Quantum Coders"', icon: 'users', color: 'tl-cyan' },
    { type: 'API', text: 'New event matches your Skill Profile', icon: 'bolt', color: 'tl-purple' }
];

export default function TerminalBackground() {
    const [currentSnippet, setCurrentSnippet] = useState(0);
    const [visibleLines, setVisibleLines] = useState(0);
    const [blink, setBlink] = useState(true);
    const [currentNotif, setCurrentNotif] = useState(0);
    const intervalRef = useRef(null);

    // Cycle through snippets
    useEffect(() => {
        const snippet = CODE_SNIPPETS[currentSnippet];
        setVisibleLines(0);

        let line = 0;
        intervalRef.current = setInterval(() => {
            line++;
            setVisibleLines(line);
            if (line >= snippet.length) {
                clearInterval(intervalRef.current);
                // Wait then move to next snippet
                setTimeout(() => {
                    setCurrentSnippet((prev) => (prev + 1) % CODE_SNIPPETS.length);
                }, 2500);
            }
        }, 120);

        return () => clearInterval(intervalRef.current);
    }, [currentSnippet]);

    // Cursor blink
    useEffect(() => {
        const blinkInterval = setInterval(() => setBlink((b) => !b), 530);
        return () => clearInterval(blinkInterval);
    }, []);

    // Cycle through notifications
    useEffect(() => {
        const notifInterval = setInterval(() => {
            setCurrentNotif((prev) => (prev + 1) % NOTIFICATIONS.length);
        }, 5000); // Change notification every 5 seconds
        return () => clearInterval(notifInterval);
    }, []);

    const snippet = CODE_SNIPPETS[currentSnippet];
    const notif = NOTIFICATIONS[currentNotif];

    return (
        <div className="terminal-bg">
            {/* Terminal Window */}
            <div className="terminal-bg-window">
                <div className="terminal-bg-chrome">
                    <span className="tbg-dot tbg-red" />
                    <span className="tbg-dot tbg-yellow" />
                    <span className="tbg-dot tbg-green" />
                    <span className="terminal-bg-title">hackitall — zsh</span>
                </div>
                <div className="terminal-bg-body">
                    {snippet.slice(0, visibleLines).map((line, i) => {
                        let icon = null;
                        let text = line;
                        if (line.includes('[ICON_BOLT]')) { icon = 'bolt'; text = line.replace('[ICON_BOLT]', '').trimStart(); }
                        else if (line.includes('[ICON_ROCKET]')) { icon = 'rocket'; text = line.replace('[ICON_ROCKET]', '').trimStart(); }
                        else if (line.includes('[ICON_CHECK]')) { icon = 'check'; text = line.replace('[ICON_CHECK]', '').trimStart(); }

                        return (
                            <div key={`${currentSnippet}-${i}`} className="terminal-bg-line">
                                {icon && <span style={{ color: 'inherit', display: 'flex' }}>
                                    {icon === 'bolt' && <IconBolt size={14} color="currentColor" />}
                                    {icon === 'rocket' && <IconRocket size={14} color="currentColor" />}
                                    {icon === 'check' && <IconCheck size={14} color="currentColor" />}
                                </span>}
                                {colorize(text)}
                            </div>
                        );
                    })}
                    <span className={`terminal-bg-cursor ${blink ? '' : 'off'}`}>█</span>
                </div>
            </div>

            {/* Secondary floating terminal (smaller, offset) */}
            <div className="terminal-bg-window terminal-bg-secondary">
                <div className="terminal-bg-chrome">
                    <span className="tbg-dot tbg-red" />
                    <span className="tbg-dot tbg-yellow" />
                    <span className="tbg-dot tbg-green" />
                    <span className="terminal-bg-title">node — debug</span>
                </div>
                <div className="terminal-bg-body">
                    <div className="terminal-bg-line"><span className="tl-green">✓</span> All 179 tests passed</div>
                    <div className="terminal-bg-line"><span className="tl-dim">Coverage: 94.2%</span></div>
                    <div className="terminal-bg-line"><span className="tl-dim">Time: 3.47s</span></div>
                    <div className="terminal-bg-line">&nbsp;</div>
                    <div className="terminal-bg-line"><span className="tl-cyan">$</span> npm run build</div>
                    <div className="terminal-bg-line"><span className="tl-dim">✓ 42 modules transformed</span></div>
                    <div className="terminal-bg-line"><span className="tl-green">✓ Build complete in 1.2s</span></div>
                </div>
            </div>

            {/* Third floating terminal (smallest, opposite corner) */}
            <div className="terminal-bg-window terminal-bg-tertiary">
                <div className="terminal-bg-chrome">
                    <span className="tbg-dot tbg-red" />
                    <span className="tbg-dot tbg-yellow" />
                    <span className="tbg-dot tbg-green" />
                    <span className="terminal-bg-title">system — monitor</span>
                </div>
                <div className="terminal-bg-body">
                    <div className="terminal-bg-line"><span className="tl-dim">CPU:</span>  <span className="tl-cyan">▓▓▓▓▓▓░░</span> <span className="tl-dim">67%</span></div>
                    <div className="terminal-bg-line"><span className="tl-dim">MEM:</span>  <span className="tl-purple">▓▓▓▓▓░░░</span> <span className="tl-dim">52%</span></div>
                    <div className="terminal-bg-line"><span className="tl-dim">DISK:</span> <span className="tl-green">▓▓░░░░░░</span> <span className="tl-dim">24%</span></div>
                    <div className="terminal-bg-line"><span className="tl-dim">NET:</span>  <span className="tl-cyan">↑ 2.4MB/s ↓ 14MB/s</span></div>
                </div>
            </div>

            {/* Quaternary floating terminal (Notification alerts) */}
            <div className="terminal-bg-window terminal-bg-quaternary">
                <div className="terminal-bg-chrome">
                    <span className="tbg-dot tbg-red" />
                    <span className="tbg-dot tbg-yellow" />
                    <span className="tbg-dot tbg-green" />
                    <span className="terminal-bg-title">notifications</span>
                </div>
                <div className="terminal-bg-body" style={{ display: 'flex', flexDirection: 'column', padding: '1rem', gap: '0.75rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span className={notif.color}>
                            {notif.icon === 'mail' && <IconMail size={16} color="currentColor" />}
                            {notif.icon === 'calendar' && <IconCalendar size={16} color="currentColor" />}
                            {notif.icon === 'users' && <IconUsers size={16} color="currentColor" />}
                            {notif.icon === 'bolt' && <IconBolt size={16} color="currentColor" />}
                        </span>
                        <span className="tl-dim" style={{ fontSize: '0.75em', textTransform: 'uppercase', letterSpacing: '1px' }}>{notif.type} Event</span>
                    </div>
                    <div className="terminal-bg-line" style={{ whiteSpace: 'normal', lineHeight: '1.4' }} key={notif.text}>
                        <span className="tl-cyan">{notif.text}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}

function colorize(line) {
    // Simple syntax highlighting
    if (line.startsWith('$') || line.startsWith('>')) {
        return <span className="tl-green">{line}</span>;
    }
    if (line.startsWith('//') || line.startsWith('#')) {
        return <span className="tl-dim">{line}</span>;
    }
    if (line.includes('import') || line.includes('from') || line.includes('const') || line.includes('function') || line.includes('return')) {
        return <span className="tl-cyan">{line}</span>;
    }
    if (line.includes('╔') || line.includes('╚') || line.includes('╠') || line.includes('║') || line.includes('┌') || line.includes('└') || line.includes('│')) {
        return <span className="tl-cyan">{line}</span>;
    }
    if (line.includes('▓')) {
        return <span className="tl-cyan">{line}</span>;
    }
    return <span className="tl-dim">{line}</span>;
}
