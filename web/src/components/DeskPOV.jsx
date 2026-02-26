import { useState, useEffect } from 'react';
import './DeskPOV.css';

export default function DeskPOV() {
  const [cursor, setCursor] = useState(true);
  const [currentLine, setCurrentLine] = useState(0);

  useEffect(() => {
    const cursorInterval = setInterval(() => {
      setCursor(prev => !prev);
    }, 500);

    const lineInterval = setInterval(() => {
      setCurrentLine(prev => (prev + 1) % 5);
    }, 2000);

    return () => {
      clearInterval(cursorInterval);
      clearInterval(lineInterval);
    };
  }, []);

  return (
    <div className="desk-pov-background">
      {/* Main Terminal Window */}
      <pre className="terminal-window">
{`╔═══════════════════════════════════════════════════════════════════════════╗
║  student@hackathon:~/project$ █                                           ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  $ npm run dev                                                            ║
║  > Starting development server...                                        ║
║  > Compiling...                                                           ║
║  ${currentLine === 0 ? '> ✓ Compiled successfully!' : '> ⚠ Warning: Deprecated API'}                                                  ║
║                                                                           ║
║  $ git status                                                             ║
║  On branch feature/hackathon-project                                     ║
║  ${currentLine === 1 ? '> Modified: src/App.js' : '> Modified: src/components/Feature.js'}                                                    ║
║  ${currentLine === 1 ? '> Modified: package.json' : '> Untracked: debug.log'}                                                  ║
║                                                                           ║
║  $ npm test                                                               ║
║  ${currentLine === 2 ? '> ✓ 42 tests passing' : '> Running test suite...'}                                                      ║
║  ${currentLine === 2 ? '> ✓ All assertions passed' : '> Testing components...'}                                                   ║
║                                                                           ║
║  $ node debug.js                                                          ║
║  ${currentLine === 3 ? '> Debugging line 127...' : '> Breakpoint hit at line 127'}                                                    ║
║  ${currentLine === 3 ? '> Variable x = undefined' : '> Inspecting variables...'}                                                   ║
║  ${currentLine === 3 ? '> ERROR: Cannot read property' : '> Stack trace available'}                                              ║
║                                                                           ║
║  $ git commit -m "fix: resolved bug in authentication"                   ║
║  ${currentLine === 4 ? '> [feature/hackathon-project a7f3c2d]' : '> Committing changes...'}                                           ║
║  ${currentLine === 4 ? '> 3 files changed, 47 insertions(+)' : '> Preparing commit...'}                                          ║
║                                                                           ║
║  $ █${cursor ? '█' : ' '}                                                                        ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝`}
      </pre>

      {/* CPU Usage Widget */}
      <pre className="widget cpu-widget">
{`╔═══════════════╗
║ CPU USAGE     ║
╠═══════════════╣
║ ▓▓▓▓▓▓▓░░░ 72%║
║               ║
║ Core 1: ▓▓▓░  ║
║ Core 2: ▓▓▓▓░ ║
║ Core 3: ▓▓▓░  ║
║ Core 4: ▓▓▓▓░ ║
╚═══════════════╝`}
      </pre>

      {/* Memory Widget */}
      <pre className="widget memory-widget">
{`╔═══════════════╗
║ MEMORY        ║
╠═══════════════╣
║ RAM: 8.2/16GB ║
║ ▓▓▓▓▓░░░░░ 51%║
║               ║
║ SWAP: 0.5/4GB ║
║ ▓░░░░░░░░░ 12%║
╚═══════════════╝`}
      </pre>

      {/* Network Widget */}
      <pre className="widget network-widget">
{`╔═══════════════╗
║ NETWORK       ║
╠═══════════════╣
║ ↓ 2.4 MB/s    ║
║ ↑ 0.8 MB/s    ║
║               ║
║ Ping: 12ms    ║
║ Status: ✓ OK  ║
╚═══════════════╝`}
      </pre>

      {/* Git Status Widget */}
      <pre className="widget git-widget">
{`╔═══════════════╗
║ GIT STATUS    ║
╠═══════════════╣
║ Branch:       ║
║ feature/hack  ║
║               ║
║ Changes: 3    ║
║ Commits: 47   ║
╚═══════════════╝`}
      </pre>

      {/* Time Widget */}
      <pre className="widget time-widget">
{`╔═══════════════╗
║ TIME          ║
╠═══════════════╣
║  02:47 AM     ║
║               ║
║ ⏰ Deadline:  ║
║  4h 13m left  ║
╚═══════════════╝`}
      </pre>

      {/* Build Status Widget */}
      <pre className="widget build-widget">
{`╔═══════════════╗
║ BUILD STATUS  ║
╠═══════════════╣
║ ${currentLine === 0 ? '✓ SUCCESS' : currentLine === 3 ? '✗ FAILED' : '⟳ BUILDING'}     ║
║               ║
║ Tests: ${currentLine === 2 ? '✓ PASS' : '⟳ RUN'}  ║
║ Lint:  ✓ PASS ║
╚═══════════════╝`}
      </pre>

      {/* Coffee Counter Widget */}
      <pre className="widget coffee-widget">
{`╔═══════════════╗
║ FUEL LEVEL    ║
╠═══════════════╣
║   ╱│╲         ║
║  ╱ │ ╲        ║
║ ╱  │  ╲       ║
║╱═══════╲      ║
║ COFFEE: 5     ║
║ ENERGY: ▓▓▓░  ║
╚═══════════════╝`}
      </pre>

      {/* TODO Widget */}
      <pre className="widget todo-widget">
{`╔═══════════════╗
║ TODO LIST     ║
╠═══════════════╣
║ ✓ Setup DB    ║
║ ✓ Auth API    ║
║ ⟳ Fix bug #42 ║
║ ☐ Deploy      ║
║ ☐ Test E2E    ║
╚═══════════════╝`}
      </pre>
    </div>
  );
}
