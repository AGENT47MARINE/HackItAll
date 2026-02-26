import { useEffect, useRef, useState } from 'react';
import './TerminalBackground.css';

const CODE_SNIPPETS = [
    [
        '$ hackitall init my-project',
        '✓ Project scaffolded',
        '✓ Dependencies installed',
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
        'import React from "react";',
        'import { useState } from "react";',
        '',
        'function HackathonProject() {',
        '  const [ideas, setIdeas] = useState([]);',
        '  const [coffee, setCoffee] = useState(5);',
        '',
        '  // TODO: Build something amazing',
        '  const innovate = async () => {',
        '    const result = await api.submit();',
        '    return "🚀 Innovation!";',
        '  }',
        '',
        '  return <App />;',
        '}',
    ],
    [
        '$ git add .',
        '$ git commit -m "feat: hackathon MVP"',
        '[main a3f7b2c] feat: hackathon MVP',
        ' 12 files changed, 847 insertions(+)',
        '',
        '$ git push origin main',
        'Enumerating objects: 42, done.',
        'Compressing objects: 100% (38/38)',
        'Writing objects: 100% (42/42)',
        'Total 42 (delta 12), reused 0',
        'To github.com:team/hackathon.git',
        ' * [new branch]  main -> main',
        '',
        '✓ Deployed successfully!',
    ],
    [
        '╔════════════════════════════════╗',
        '║    HACKATHON STATUS            ║',
        '╠════════════════════════════════╣',
        '║ Time Left:  03:47:12           ║',
        '║ Energy:  ▓▓▓▓▓▓░░░░  60%      ║',
        '║ Focus:   ▓▓▓▓▓▓▓░░░  70%      ║',
        '║ Coffee:  ▓▓▓▓▓▓▓▓▓░  90%      ║',
        '║ Lines:   1,247 written         ║',
        '╠════════════════════════════════╣',
        '║ [✓] Setup Project              ║',
        '║ [✓] Design UI                  ║',
        '║ [~] Implement Features         ║',
        '║ [ ] Test & Debug               ║',
        '║ [ ] Deploy & Submit            ║',
        '╚════════════════════════════════╝',
    ],
    [
        '$ hackitall search --type hackathon',
        '',
        'Searching opportunities...',
        '',
        '┌─────────────────────────────────┐',
        '│ ⚡ MLH Hackathon 2025           │',
        '│    Deadline: Apr 15, 2025       │',
        '│    Prize: $10,000               │',
        '└─────────────────────────────────┘',
        '┌─────────────────────────────────┐',
        '│ 🚀 NASA Space Apps Challenge    │',
        '│    Deadline: Oct 5, 2025        │',
        '│    Global Event                 │',
        '└─────────────────────────────────┘',
        '',
        'Found 247 results. Showing top 2.',
    ],
];

export default function TerminalBackground() {
    const [currentSnippet, setCurrentSnippet] = useState(0);
    const [visibleLines, setVisibleLines] = useState(0);
    const [blink, setBlink] = useState(true);
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

    const snippet = CODE_SNIPPETS[currentSnippet];

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
                    {snippet.slice(0, visibleLines).map((line, i) => (
                        <div key={`${currentSnippet}-${i}`} className="terminal-bg-line">
                            {colorize(line)}
                        </div>
                    ))}
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
        </div>
    );
}

function colorize(line) {
    // Simple syntax highlighting
    if (line.startsWith('$') || line.startsWith('>')) {
        return <span className="tl-green">{line}</span>;
    }
    if (line.startsWith('✓') || line.startsWith('✅')) {
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
