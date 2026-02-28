// DomainSVGCard — premium animated SVG card for a Game Theory domain
// Props: domain: { id, name, theme }  |  stats: { cards_count, due_today, accuracy }
//        onClick: () => void

import { useState, useRef } from 'react';

const THEME_MAP = {
    dating: { icon: '♥', color: '#f472b6', dark: '#831843', grad: '#be185d', label: 'Dinâmicas' },
    office: { icon: '⚡', color: '#a78bfa', dark: '#4c1d95', grad: '#7c3aed', label: 'Escritório' },
    finance: { icon: '◈', color: '#fbbf24', dark: '#92400e', grad: '#b45309', label: 'Finanças' },
    negotiation: { icon: '⚖', color: '#34d399', dark: '#065f46', grad: '#059669', label: 'Negociação' },
    geopolitics: { icon: '✦', color: '#60a5fa', dark: '#1e3a8a', grad: '#2563eb', label: 'Geopolítica' },
    social: { icon: '◉', color: '#fb923c', dark: '#7c2d12', grad: '#ea580c', label: 'Social' },
    custom: { icon: '❈', color: '#e879f9', dark: '#701a75', grad: '#a21caf', label: 'Custom' },
};

function getTheme(themeValue) {
    const key = Object.keys(THEME_MAP).find(k => themeValue?.toLowerCase().includes(k));
    return THEME_MAP[key] || THEME_MAP.custom;
}

export default function DomainSVGCard({ domain, stats, onClick }) {
    const t = getTheme(domain.theme);
    const cardRef = useRef(null);
    const [tilt, setTilt] = useState({ x: 0, y: 0 });
    const [hovered, setHovered] = useState(false);

    const accuracy = stats?.accuracy > 0 ? Math.round(stats.accuracy * 100) : null;

    // 3D tilt on mouse move
    const handleMouseMove = (e) => {
        const rect = cardRef.current?.getBoundingClientRect();
        if (!rect) return;
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const dx = (e.clientX - cx) / (rect.width / 2);
        const dy = (e.clientY - cy) / (rect.height / 2);
        setTilt({ x: -dy * 8, y: dx * 8 });
    };

    const handleMouseLeave = () => {
        setTilt({ x: 0, y: 0 });
        setHovered(false);
    };

    const gradId = `dom-grad-${domain.id}`;

    return (
        <div
            ref={cardRef}
            onClick={onClick}
            onMouseMove={handleMouseMove}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={handleMouseLeave}
            style={{
                cursor: 'pointer',
                borderRadius: 16,
                perspective: '800px',
                transition: 'box-shadow 0.3s ease',
                boxShadow: hovered
                    ? `0 0 40px ${t.color}55, 0 24px 48px rgba(0,0,0,0.5)`
                    : `0 4px 20px rgba(0,0,0,0.3)`,
            }}
        >
            <div
                style={{
                    borderRadius: 16,
                    overflow: 'hidden',
                    border: `1px solid ${hovered ? t.color + '88' : 'var(--border-color)'}`,
                    background: 'var(--bg-card)',
                    transition: 'transform 0.15s ease, border-color 0.3s',
                    transform: hovered
                        ? `rotateX(${tilt.x}deg) rotateY(${tilt.y}deg) scale(1.03)`
                        : 'rotateX(0deg) rotateY(0deg) scale(1)',
                    transformStyle: 'preserve-3d',
                }}
            >
                {/* ── SVG Header Art ── */}
                <svg viewBox="0 0 300 130" width="100%" style={{ display: 'block' }}>
                    <defs>
                        <linearGradient id={gradId} x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor={t.dark} stopOpacity="0.9" />
                            <stop offset="100%" stopColor={t.grad} stopOpacity="0.4" />
                        </linearGradient>
                        <radialGradient id={`${gradId}-glow`} cx="75%" cy="30%" r="60%">
                            <stop offset="0%" stopColor={t.color} stopOpacity="0.25" />
                            <stop offset="100%" stopColor={t.color} stopOpacity="0" />
                        </radialGradient>
                        <linearGradient id="imageOverlay" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="var(--bg-card)" stopOpacity="0.1" />
                            <stop offset="50%" stopColor="var(--bg-card)" stopOpacity="0.05" />
                            <stop offset="100%" stopColor="var(--bg-card)" stopOpacity="0.65" />
                        </linearGradient>
                        <clipPath id={`corners-${domain.id}`}>
                            <rect x="0" y="0" width="300" height="130" rx="0" />
                        </clipPath>
                    </defs>

                    {/* Base background or Image */}
                    <g clipPath={`url(#corners-${domain.id})`}>
                        {domain.image_url ? (
                            <>
                                <image
                                    href={`${import.meta.env.VITE_API_URL || ''}${domain.image_url}`}
                                    x="0" y="0" width="300" height="130"
                                    preserveAspectRatio="xMidYMid slice"
                                />
                                <rect width="300" height="130" fill="url(#imageOverlay)" />
                            </>
                        ) : (
                            <rect width="300" height="130" fill={`url(#${gradId})`} />
                        )}
                    </g>
                    {/* Glow radial — only without image */}
                    {!domain.image_url && <rect width="300" height="130" fill={`url(#${gradId}-glow)`} />}

                    {/* Grid lines — only without image */}
                    {!domain.image_url && [0, 60, 120, 180, 240, 300].map(x => (
                        <line key={x} x1={x} y1="0" x2={x} y2="130" stroke={t.color} strokeOpacity="0.06" strokeWidth="1" />
                    ))}
                    {!domain.image_url && [0, 43, 86, 130].map(y => (
                        <line key={y} x1="0" y1={y} x2="300" y2={y} stroke={t.color} strokeOpacity="0.06" strokeWidth="1" />
                    ))}

                    {/* Large background icon — only without image */}
                    {!domain.image_url && (
                        <text
                            x="230" y="105"
                            fontSize="90"
                            fontFamily="system-ui, sans-serif"
                            fill={t.color}
                            fillOpacity="0.12"
                            textAnchor="middle"
                        >
                            {t.icon}
                        </text>
                    )}

                    {/* Theme label chip */}
                    <rect x="12" y="10" width="70" height="18" rx="9" fill={t.color} fillOpacity="0.25" />
                    <rect x="12" y="10" width="70" height="18" rx="9" fill="none" stroke={t.color} strokeOpacity="0.5" strokeWidth="1" />
                    <text x="47" y="22" textAnchor="middle" dominantBaseline="middle"
                        fill={t.color} fontSize="8" fontFamily="Courier New, monospace"
                        fontWeight="800" letterSpacing="1">
                        {t.label.toUpperCase()}
                    </text>

                    {/* Domain name */}
                    <text
                        x="14" y="76"
                        fill="#fff"
                        fontSize="15"
                        fontFamily="system-ui, sans-serif"
                        fontWeight="800"
                    >
                        {domain.name.length > 22 ? domain.name.slice(0, 20) + '…' : domain.name}
                    </text>

                    {/* Stats row */}
                    {/* Cards */}
                    <text x="14" y="105" fill={t.color} fontSize="20" fontFamily="Courier New, monospace" fontWeight="800">
                        {stats?.cards_count ?? 0}
                    </text>
                    <text x="14" y="118" fill={t.color} fontSize="7" fontFamily="Courier New, monospace" fillOpacity="0.8" letterSpacing="1">
                        CARDS
                    </text>

                    {/* Due today */}
                    <text x="82" y="105" fill={stats?.due_today > 0 ? '#f59e0b' : '#4b5563'} fontSize="20"
                        fontFamily="Courier New, monospace" fontWeight="800">
                        {stats?.due_today ?? 0}
                    </text>
                    <text x="82" y="118" fill="#6b7280" fontSize="7" fontFamily="Courier New, monospace" letterSpacing="1">
                        HOJE
                    </text>

                    {/* Accuracy */}
                    <text x="150" y="105" fill={accuracy !== null ? '#22c55e' : '#4b5563'} fontSize="20"
                        fontFamily="Courier New, monospace" fontWeight="800">
                        {accuracy !== null ? `${accuracy}%` : '—'}
                    </text>
                    <text x="150" y="118" fill="#6b7280" fontSize="7" fontFamily="Courier New, monospace" letterSpacing="1">
                        ACERTO
                    </text>

                    {/* CTA arrow */}
                    <text x="284" y="118" fill={t.color} fontSize="18" fontFamily="system-ui" fillOpacity={hovered ? 1 : 0.5}
                        textAnchor="middle">
                        →
                    </text>
                </svg>

                {/* Bottom strip */}
                <div style={{
                    padding: '8px 14px 10px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    background: hovered ? `${t.color}0f` : 'transparent',
                    borderTop: `1px solid ${t.color}22`,
                    transition: 'background 0.3s',
                }}>
                    <span style={{
                        color: 'var(--text-muted)', fontSize: 10,
                        fontFamily: 'Courier New, monospace',
                        letterSpacing: 2, textTransform: 'uppercase',
                    }}>
                        {domain.theme}
                    </span>
                    <span style={{
                        color: t.color, fontSize: 10, fontWeight: 700,
                        fontFamily: 'Courier New, monospace', letterSpacing: 1,
                    }}>
                        Gerar Cards →
                    </span>
                </div>
            </div>
        </div>
    );
}
