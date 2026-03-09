import React from 'react';

/**
 * PixelIcon - Component that renders custom SVG-based pixel art icons
 * designed to replace standard emojis in the retro gaming interface.
 */
const PixelIcon = ({ name, size = 24, color, active = false, className = "" }) => {
    // Color palette from design system
    const colors = {
        bronze: '#cd7f32',
        silver: '#c0c0c0',
        gold: '#ffcc00',
        platinum: '#e5e4e2',
        diamond: '#b9f2ff',
        obsidian: '#9d50bb',
        green: '#00ff41',
        red: '#ff4b2b',
        white: '#ffffff',
    };

    const currentColor = color || '#fff';

    // SVG Icons shaped as pixel art (8-bit blocky style)
    const icons = {
        // 🛡️ Bronze Byte Shield
        shield: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M2 2h12v2h-1v7l-1 1-4 3-4-3-1-1V4H2V2zm2 3v5l1 1 3 2 3-2 1-1V5H4z" fillOpacity="0.8" />
                <rect x="7" y="5" width="2" height="4" />
            </svg>
        ),
        // 📜 Silver Script Scroll
        scroll: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M3 2h8v1H3V2zm9 1h1v11h-1V3zM3 13h8v1H3v-1zm-1-1h1V3H2v9z" />
                <path d="M4 4h6v1H4V4zm0 3h6v1H4V7zm0 3h4v1H4v-1z" fillOpacity="0.5" />
            </svg>
        ),
        // 🌀 Gold Gateway Portal
        portal: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M2 2h12v1H2V2zm0 11h12v1H2v-1zM2 3h1v10H2V3zm11 0h1v10h-1V3z" />
                <path d="M5 5h6v1H5V5zm0 10h6v1H5v-1zm0-4h1v3H5V6zm5 0h1v3h-1V6z" fillOpacity="0.7" />
                <rect x="7" y="7" width="2" height="2" fill="#fff" />
            </svg>
        ),
        // 🔌 Platinum Pixel Circuit
        circuit: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <rect x="4" y="4" width="8" height="8" />
                <path d="M7 2h2v2H7V2zm0 10h2v2H7v-2zM2 7h2v2H2V7zm10 0h2v2h-2V7z" fillOpacity="0.6" />
                <rect x="7" y="7" width="2" height="2" fill={colors.green} />
            </svg>
        ),
        // 💎 Diamond Debug Gem
        gem: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 2L13 5V11L8 14L3 11V5L8 2Z" />
                <path d="M8 4L11 6V10L8 12L5 10V6L8 4Z" fillOpacity="0.5" />
                <rect x="6" y="5" width="2" height="2" fill="#fff" opacity="0.6" />
            </svg>
        ),
        // 👑 Obsidian Overlord Crown
        crown: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M2 12h12v1H2v-1zM2 5l2 3 4-4 4 4 2-3v7H2V5z" />
                <rect x="7" y="10" width="2" height="1" fill={colors.gold} />
            </svg>
        ),
        // 🏆 Trophy
        trophy: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M4 2h8v5L8 10L4 7V2zm-1 1h1v3H3V3zm10 0h1v3h-1V3zM6 11h4v1H6v-1zm-1 2h6v1H5v-1z" />
                <rect x="7" y="10" width="2" height="1" />
            </svg>
        ),
        // 🔥 Flame (Streak)
        flame: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 2s-4 4-4 7c0 2.2 1.8 4 4 4s4-1.8 4-4-4-7-4-7z" fill="#ff4b2b" />
                <path d="M8 6s-2 2-2 4c0 1.1.9 2 2 2s2-.9 2-2-2-4-2-4z" fill="#ffcc00" />
            </svg>
        ),
        // 🏃 Runner
        runner: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <rect x="7" y="2" width="4" height="4" />
                <rect x="3" y="6" width="10" height="4" />
                <rect x="4" y="10" width="3" height="4" />
                <rect x="9" y="10" width="3" height="4" />
            </svg>
        ),
        // 🐛 Bug
        bug: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <rect x="5" y="4" width="6" height="8" />
                <path d="M3 5h2M3 8h2M3 11h2M11 5h2M11 8h2M11 11h2" stroke="currentColor" strokeWidth="2" />
                <rect x="7" y="2" width="2" height="2" />
            </svg>
        ),
        // 🧭 Compass
        compass: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 2a6 6 0 100 12 6 6 0 000-12zm0 10a4 4 0 110-8 4 4 0 010 8z" fillOpacity="0.4" />
                <path d="M8 4l2 4-2 4-2-4z" />
            </svg>
        ),
        // 🔍 Search
        search: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M6 3a4 4 0 100 8 4 4 0 000-8zM2 7a5 5 0 1110 0 5 5 0 01-10 0z" />
                <path d="M10 10l4 4" stroke="currentColor" strokeWidth="2" />
            </svg>
        ),
        // 📚 Books
        books: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <rect x="2" y="3" width="3" height="10" />
                <rect x="6" y="3" width="3" height="10" />
                <rect x="10" y="3" width="3" height="10" />
            </svg>
        ),
        // 🕷️ Spider (Scraper)
        spider: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <rect x="6" y="6" width="4" height="5" />
                <path d="M2 4l4 2M14 4l-4 2M2 8h4M14 8h-4M2 12l4-2M14 12l-4-2" stroke="currentColor" strokeWidth="1" />
                <rect x="7" y="4" width="2" height="2" />
            </svg>
        ),
        // 💀 Skull (Legendary)
        skull: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M4 4h8v5l-1 1v3H5v-3l-1-1V4z" />
                <path d="M6 6h1v2H6V6zm3 0h1v2H9V6z" fill="#000" />
                <rect x="6" y="10" width="4" height="1" fill="#000" />
            </svg>
        ),
        // 🥉 Medal
        medal: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M6 2l1 4h2l1-4h2v2l-4 6-4-6V2H6z" fillOpacity="0.4" />
                <circle cx="8" cy="10" r="4" />
                <circle cx="8" cy="10" r="2" fillOpacity="0.3" />
            </svg>
        ),
        // ✔️ Check
        check: (
            <svg viewBox="0 0 16 16" fill="none">
                <path d="M3 9l3 3l7-7" stroke="currentColor" strokeWidth="3" />
            </svg>
        ),
        // 🔔 Bell
        bell: (
            <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M4 11h8v1H4v-1zm1-1h6V6c0-1.7-1.3-3-3-3s-3 1.3-3 3v4zm2 3h2v1H7v-1z" />
                <rect x="7" y="12" width="2" height="1" fillOpacity="0.8" />
            </svg>
        )
    };

    return (
        <div
            className={`pixel-icon ${active ? 'active' : ''} ${className}`}
            style={{
                width: size,
                height: size,
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                filter: active ? `drop-shadow(0 0 5px ${currentColor})` : 'none'
            }}
        >
            {icons[name] || icons.shield}
        </div>
    );
};

export default PixelIcon;
