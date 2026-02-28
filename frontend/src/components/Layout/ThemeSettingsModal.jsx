import { useState, useEffect } from 'react';

const COLORS = [
    { name: 'Roxo (Padrão)', value: '#7c3aed', light: '#a855f7', dark: '#6b21a8' },
    { name: 'Azul', value: '#2563eb', light: '#3b82f6', dark: '#1d4ed8' },
    { name: 'Verde', value: '#16a34a', light: '#22c55e', dark: '#15803d' },
    { name: 'Laranja', value: '#ea580c', light: '#f97316', dark: '#c2410c' },
    { name: 'Rosa', value: '#db2777', light: '#ec4899', dark: '#be185d' },
];

export default function ThemeSettingsModal({ onClose }) {
    const [theme, setTheme] = useState(localStorage.getItem('app_theme') || 'auto');
    const [accent, setAccent] = useState(localStorage.getItem('app_accent') || '#7c3aed');

    useEffect(() => {
        // Escuta a tecla ESC
        const handleKeyDown = (e) => {
            if (e.key === 'Escape') onClose();
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [onClose]);

    const handleThemeChange = (newTheme) => {
        setTheme(newTheme);
        localStorage.setItem('app_theme', newTheme);
        // Resolve 'auto' to the actual system preference
        const resolved = newTheme === 'auto'
            ? (window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
            : newTheme;
        document.documentElement.setAttribute('data-theme', resolved);
    };

    const handleAccentChange = (colorObj) => {
        setAccent(colorObj.value);
        localStorage.setItem('app_accent', colorObj.value);
        document.documentElement.style.setProperty('--accent', colorObj.value);
        document.documentElement.style.setProperty('--accent-light', colorObj.light);
        document.documentElement.style.setProperty('--accent-dark', colorObj.dark);
    };

    return (
        <div
            style={{
                position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999,
                backdropFilter: 'blur(4px)'
            }}
            onClick={onClose}
        >
            <div
                style={{
                    background: 'var(--bg-card)', border: '1px solid var(--accent-dark)', borderRadius: 12,
                    padding: '2rem', width: '100%', maxWidth: 420,
                    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)'
                }}
                onClick={(e) => e.stopPropagation()}
            >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                    <h2 style={{ color: 'var(--text-highlight)', fontSize: 18, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase', margin: 0 }}>
                        Configuração Visual
                    </h2>
                    <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 24 }}>
                        &times;
                    </button>
                </div>

                {/* Theme Mode — SVG Slider */}
                {(() => {
                    const MODES = [
                        { key: 'light', icon: '☀', label: 'Light' },
                        { key: 'auto', icon: '◐', label: 'Auto' },
                        { key: 'dark', icon: '🌙', label: 'Dark' },
                    ];
                    const activeIdx = MODES.findIndex(m => m.key === theme);
                    const W = 360, H = 52, PAD = 4;
                    const segW = (W - PAD * 2) / MODES.length;
                    const thumbX = PAD + activeIdx * segW;
                    const thumbW = segW;
                    return (
                        <div style={{ marginBottom: 24 }}>
                            <label style={{ color: 'var(--text-muted)', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase', display: 'block', marginBottom: 8 }}>
                                Modo
                            </label>
                            <svg
                                viewBox={`0 0 ${W} ${H}`}
                                width="100%"
                                style={{ display: 'block', cursor: 'pointer', borderRadius: H / 2, overflow: 'visible' }}
                            >
                                <defs>
                                    <linearGradient id="slider-track" x1="0" y1="0" x2="1" y2="0">
                                        <stop offset="0%" stopColor="var(--bg-card-inner)" />
                                        <stop offset="100%" stopColor="var(--border-color)" />
                                    </linearGradient>
                                    <filter id="thumb-glow">
                                        <feGaussianBlur stdDeviation="4" result="blur" />
                                        <feMerge>
                                            <feMergeNode in="blur" />
                                            <feMergeNode in="SourceGraphic" />
                                        </feMerge>
                                    </filter>
                                </defs>

                                {/* Track */}
                                <rect x="0" y="0" width={W} height={H} rx={H / 2}
                                    fill="url(#slider-track)" stroke="var(--border-color)" strokeWidth="1" />

                                {/* Thumb — animated pill */}
                                <rect
                                    x={thumbX} y={PAD} width={thumbW} height={H - PAD * 2}
                                    rx={(H - PAD * 2) / 2}
                                    fill="var(--accent)"
                                    fillOpacity="0.25"
                                    stroke="var(--accent-light)"
                                    strokeWidth="1.5"
                                    filter="url(#thumb-glow)"
                                    style={{ transition: 'x 0.35s cubic-bezier(0.34, 1.56, 0.64, 1)' }}
                                />

                                {/* Hit areas + labels */}
                                {MODES.map((m, i) => {
                                    const cx = PAD + i * segW + segW / 2;
                                    const isActive = i === activeIdx;
                                    return (
                                        <g key={m.key} onClick={() => handleThemeChange(m.key)} style={{ cursor: 'pointer' }}>
                                            <rect x={PAD + i * segW} y="0" width={segW} height={H} fill="transparent" />
                                            <text
                                                x={cx} y={H / 2 - 4}
                                                textAnchor="middle" dominantBaseline="middle"
                                                fontSize="16"
                                                style={{ transition: 'opacity 0.3s', pointerEvents: 'none' }}
                                                opacity={isActive ? 1 : 0.5}
                                            >
                                                {m.icon}
                                            </text>
                                            <text
                                                x={cx} y={H / 2 + 13}
                                                textAnchor="middle" dominantBaseline="middle"
                                                fontSize="9" fontWeight="700" letterSpacing="1.5"
                                                fontFamily="Courier New, monospace"
                                                fill={isActive ? 'var(--accent-light)' : 'var(--text-muted)'}
                                                style={{ transition: 'fill 0.3s, opacity 0.3s', pointerEvents: 'none' }}
                                                opacity={isActive ? 1 : 0.6}
                                            >
                                                {m.label.toUpperCase()}
                                            </text>
                                        </g>
                                    );
                                })}
                            </svg>
                        </div>
                    );
                })()}

                {/* Accent Color */}
                <div>
                    <label style={{ color: 'var(--text-muted)', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase', display: 'block', marginBottom: 8 }}>
                        Cor de Destaque
                    </label>
                    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                        {COLORS.map((c) => (
                            <button
                                key={c.value}
                                onClick={() => handleAccentChange(c)}
                                title={c.name}
                                style={{
                                    width: 36, height: 36, borderRadius: '50%', cursor: 'pointer',
                                    background: c.value,
                                    border: accent === c.value ? '3px solid var(--text-main)' : '2px solid transparent',
                                    outline: accent === c.value ? `2px solid ${c.value}` : 'none',
                                    outlineOffset: 2,
                                    transition: 'transform 0.2s',
                                    transform: accent === c.value ? 'scale(1.1)' : 'scale(1)'
                                }}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
