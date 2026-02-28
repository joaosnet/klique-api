// DeckPileDisplay — animated stacked card pile for TrainingPage
// Props: count: number — total cards due for review today

import { useState } from 'react';

const PILE_COLORS = ['#7c3aed', '#5b21b6', '#4c1d95'];
const CARD_W = 260;
const CARD_H = 160;

export default function DeckPileDisplay({ count, onStart }) {
    const [hovered, setHovered] = useState(false);

    const offsets = [
        { dx: 0, dy: 0, rot: 0, z: 3 },
        { dx: -8, dy: 6, rot: -5, z: 2 },
        { dx: 8, dy: 10, rot: 6, z: 1 },
    ];

    return (
        <div style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center',
            gap: 32, padding: '2rem 0',
        }}>
            {/* Stack of cards */}
            <div
                style={{
                    position: 'relative',
                    width: CARD_W, height: CARD_H + 20,
                    cursor: 'pointer',
                }}
                onMouseEnter={() => setHovered(true)}
                onMouseLeave={() => setHovered(false)}
                onClick={onStart}
            >
                {offsets.map((o, i) => {
                    const color = PILE_COLORS[i];
                    const gradId = `deck-grad-${i}`;
                    const isTop = i === 0;
                    return (
                        <div
                            key={i}
                            style={{
                                position: 'absolute',
                                width: CARD_W,
                                height: CARD_H,
                                top: 0,
                                left: 0,
                                borderRadius: 12,
                                transition: 'transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s',
                                transform: hovered
                                    ? `translateX(${o.dx * 1.5}px) translateY(${isTop ? -10 : o.dy * 1.3}px) rotate(${o.rot * 1.4}deg)`
                                    : `translateX(${o.dx}px) translateY(${o.dy}px) rotate(${o.rot}deg)`,
                                boxShadow: isTop && hovered
                                    ? `0 0 30px ${color}66, 0 20px 40px rgba(0,0,0,0.5)`
                                    : `0 ${4 + i * 3}px ${12 + i * 6}px rgba(0,0,0,0.4)`,
                                zIndex: o.z,
                            }}
                        >
                            <svg width={CARD_W} height={CARD_H} viewBox={`0 0 ${CARD_W} ${CARD_H}`} style={{ borderRadius: 12, display: 'block' }}>
                                <defs>
                                    <linearGradient id={gradId} x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" stopColor={color} stopOpacity="0.9" />
                                        <stop offset="100%" stopColor={color} stopOpacity="0.4" />
                                    </linearGradient>
                                </defs>
                                <rect width={CARD_W} height={CARD_H} rx="12" fill={`url(#${gradId})`} />

                                {/* Grid lines */}
                                {[0, 65, 130, 195, 260].map(x => (
                                    <line key={x} x1={x} y1="0" x2={x} y2={CARD_H} stroke="#fff" strokeOpacity="0.05" strokeWidth="1" />
                                ))}
                                {[0, 53, 106, 160].map(y => (
                                    <line key={y} x1="0" y1={y} x2={CARD_W} y2={y} stroke="#fff" strokeOpacity="0.05" strokeWidth="1" />
                                ))}

                                {isTop && (
                                    <>
                                        {/* Orb glow */}
                                        <circle cx={CARD_W * 0.8} cy={CARD_H * 0.3} r="55" fill={color} fillOpacity="0.2" />
                                        <circle cx={CARD_W * 0.8} cy={CARD_H * 0.3} r="30" fill={color} fillOpacity="0.15" />

                                        {/* Count */}
                                        <text x="20" y="52" fill="#fff" fontSize="38" fontFamily="Courier New, monospace"
                                            fontWeight="800" opacity="0.95">
                                            {count}
                                        </text>
                                        <text x="20" y="68" fill="#fff" fontSize="9" fontFamily="Courier New, monospace"
                                            letterSpacing="3" opacity="0.7">
                                            CARTAS PARA TREINAR HOJE
                                        </text>

                                        {/* Oracle label */}
                                        <rect x="16" y="10" width="80" height="16" rx="8" fill="#fff" fillOpacity="0.12" />
                                        <text x="56" y="21" fill="#fff" fontSize="7.5" fontFamily="Courier New, monospace"
                                            fontWeight="700" letterSpacing="1.5" textAnchor="middle" dominantBaseline="middle">
                                            ORACLE DECK
                                        </text>

                                        {/* Start CTA */}
                                        <rect x="16" y={CARD_H - 36} width={CARD_W - 32} height="26" rx="8"
                                            fill="#fff" fillOpacity={hovered ? '0.2' : '0.12'} />
                                        <text x={CARD_W / 2} y={CARD_H - 19} fill="#fff" fontSize="10"
                                            fontFamily="Courier New, monospace" fontWeight="800" letterSpacing="2.5"
                                            textAnchor="middle" dominantBaseline="middle">
                                            INICIAR TREINO →
                                        </text>
                                    </>
                                )}
                            </svg>
                        </div>
                    );
                })}
            </div>

            {/* Label below */}
            <p style={{
                color: 'var(--text-muted)', fontSize: 12, letterSpacing: 2,
                textTransform: 'uppercase', fontFamily: 'Courier New, monospace',
                textAlign: 'center', margin: 0,
            }}>
                Clica no deck para começar a sessão de treino
            </p>
        </div>
    );
}
