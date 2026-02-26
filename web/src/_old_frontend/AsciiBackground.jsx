import { useEffect, useRef, useState } from 'react';
import './AsciiBackground.css';

const AsciiBackground = () => {
  const canvasRef = useRef(null);
  const [notification, setNotification] = useState(null);
  const [hoveredElement, setHoveredElement] = useState(null);

  // ASCII art elements for hackathon theme
  const asciiElements = [
    {
      id: 'laptop',
      x: 20,
      y: 30,
      art: [
        '    ___________',
        '   /___________\\',
        '  |  _________  |',
        '  | |         | |',
        '  | | >CODE_  | |',
        '  | |_________| |',
        '  \\_____________/',
        '  /_____________\\'
      ],
      clickable: true,
      notification: '╔════════════════════╗\n║ Windows 95 Alert!  ║\n║ You found a secret!║\n║ Keep coding! 💻    ║\n╚════════════════════╝'
    },
    {
      id: 'coffee',
      x: 70,
      y: 20,
      art: [
        '   ( (',
        '    ) )',
        '  ......',
        '  |    |]',
        '  |    |',
        '  `----\''
      ],
      hover: 'Fuel for hackers ☕'
    },
    {
      id: 'code',
      x: 50,
      y: 60,
      art: [
        '  </>',
        ' {  }',
        '  ||',
        ' /  \\'
      ],
      hover: 'Code never sleeps'
    },
    {
      id: 'circuit',
      x: 85,
      y: 70,
      art: [
        '  ─┬─┬─',
        '   │ │',
        '  ─┴─┴─',
        '   │ │',
        '  ─┬─┬─'
      ],
      hover: 'Circuit dreams'
    }
  ];

  // Floating particles
  const particles = useRef([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Initialize particles
    particles.current = Array.from({ length: 50 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      char: ['.', '·', '•', '○', '◦', '∘'][Math.floor(Math.random() * 6)],
      speed: 0.2 + Math.random() * 0.5,
      opacity: 0.1 + Math.random() * 0.3
    }));

    let animationFrame;

    const animate = () => {
      ctx.fillStyle = 'rgba(10, 10, 15, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw floating particles
      particles.current.forEach(particle => {
        ctx.fillStyle = `rgba(255, 255, 255, ${particle.opacity})`;
        ctx.font = '14px monospace';
        ctx.fillText(particle.char, particle.x, particle.y);

        particle.y -= particle.speed;
        if (particle.y < 0) {
          particle.y = canvas.height;
          particle.x = Math.random() * canvas.width;
        }
      });

      animationFrame = requestAnimationFrame(animate);
    };

    animate();

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationFrame);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const handleElementClick = (element) => {
    if (element.clickable && element.notification) {
      setNotification(element.notification);
      setTimeout(() => setNotification(null), 3000);
    }
  };

  return (
    <div className="ascii-background">
      <canvas ref={canvasRef} className="ascii-canvas" />
      
      <div className="ascii-elements">
        {asciiElements.map((element) => (
          <div
            key={element.id}
            className={`ascii-element ${element.clickable ? 'clickable' : ''} ${
              hoveredElement === element.id ? 'hovered' : ''
            }`}
            style={{
              left: `${element.x}%`,
              top: `${element.y}%`,
            }}
            onClick={() => handleElementClick(element)}
            onMouseEnter={() => setHoveredElement(element.id)}
            onMouseLeave={() => setHoveredElement(null)}
          >
            <pre className="ascii-art">
              {element.art.join('\n')}
            </pre>
            {hoveredElement === element.id && element.hover && (
              <div className="ascii-tooltip">{element.hover}</div>
            )}
          </div>
        ))}
      </div>

      {notification && (
        <div className="retro-notification">
          <pre>{notification}</pre>
        </div>
      )}
    </div>
  );
};

export default AsciiBackground;
