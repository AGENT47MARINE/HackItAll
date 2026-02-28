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

    // Initialize cursor trail particles
    particles.current = Array.from({ length: 30 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      char: ['█', '▓', '▒', '░'][Math.floor(Math.random() * 4)],
      speedX: (Math.random() - 0.5) * 1.5, // Horizontal movement
      speedY: (Math.random() - 0.5) * 1.5, // Vertical movement
      opacity: 0.3 + Math.random() * 0.4,
      maxOpacity: 0.3 + Math.random() * 0.4,
      fadeSpeed: 0.002 + Math.random() * 0.003,
      trail: [] // Store previous positions for trail effect
    }));

    let animationFrame;

    const animate = () => {
      ctx.fillStyle = 'rgba(10, 10, 15, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw cursor trail particles
      particles.current.forEach(particle => {
        // Draw the trail (fading previous positions)
        particle.trail.forEach((pos, index) => {
          const trailOpacity = (particle.opacity * (index + 1)) / (particle.trail.length + 1);
          ctx.fillStyle = `rgba(0, 240, 255, ${trailOpacity * 0.3})`;
          ctx.font = '16px monospace';
          ctx.fillText(particle.char, pos.x, pos.y);
        });

        // Draw the main cursor
        ctx.fillStyle = `rgba(0, 240, 255, ${particle.opacity})`;
        ctx.font = '16px monospace';
        ctx.fillText(particle.char, particle.x, particle.y);

        // Update trail (keep last 3-5 positions)
        particle.trail.push({ x: particle.x, y: particle.y });
        if (particle.trail.length > 4) {
          particle.trail.shift();
        }

        // Move particle
        particle.x += particle.speedX;
        particle.y += particle.speedY;

        // Fade in and out effect
        particle.opacity -= particle.fadeSpeed;
        if (particle.opacity <= 0) {
          particle.opacity = particle.maxOpacity;
          particle.trail = []; // Reset trail on respawn
        }

        // Wrap around screen edges
        if (particle.x < -20) particle.x = canvas.width + 20;
        if (particle.x > canvas.width + 20) particle.x = -20;
        if (particle.y < -20) particle.y = canvas.height + 20;
        if (particle.y > canvas.height + 20) particle.y = -20;
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
