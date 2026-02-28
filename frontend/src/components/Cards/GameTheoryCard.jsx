// GameTheoryCard — physical trading card design for Game Theory scenarios
import { useRef, useState } from 'react';
// Props:
//   card: { template_type, probability_heat_score, scenario_context, question,
//            predicted_outcome, game_theory_explanation }
//   revealed: bool
//   onReveal: () => void
//   onSave: () => void
//   onDiscard: () => void
//   swiping: 'left' | 'right' | null  (undefined = no animation)

const TEMPLATES = {
  if_then: {
    shortLabel: 'SE / ENTÃO',
    labelWidth: 105,
    color: '#60a5fa',
    darkColor: '#1e3a8a',
    outerBg: 'var(--gt-if-outer)',
    innerBg: 'var(--gt-if-inner)',
    accentColor: '#93c5fd',
    glowColor: 'rgba(59,130,246,0.35)',
    symbol: '⚖',
    gradStart: '#1e3a8a',
    gradEnd: 'var(--gt-if-inner)',
    btnBg: 'linear-gradient(135deg, #1d4ed8, #3b82f6)',
  },
  payoff_matrix: {
    shortLabel: 'RECOMPENSA',
    labelWidth: 105,
    color: '#fbbf24',
    darkColor: '#92400e',
    outerBg: 'var(--gt-payoff-outer)',
    innerBg: 'var(--gt-payoff-inner)',
    accentColor: '#fcd34d',
    glowColor: 'rgba(245,158,11,0.35)',
    symbol: '◈',
    gradStart: '#78350f',
    gradEnd: 'var(--gt-payoff-inner)',
    btnBg: 'linear-gradient(135deg, #b45309, #f59e0b)',
  },
  black_swan: {
    shortLabel: 'CISNE NEGRO',
    labelWidth: 115,
    color: '#f87171',
    darkColor: '#7f1d1d',
    outerBg: 'var(--gt-swan-outer)',
    innerBg: 'var(--gt-swan-inner)',
    accentColor: '#fca5a5',
    glowColor: 'rgba(239,68,68,0.35)',
    symbol: '✦',
    gradStart: '#7f1d1d',
    gradEnd: 'var(--gt-swan-inner)',
    btnBg: 'linear-gradient(135deg, #991b1b, #ef4444)',
  },
};

function heatColor(score) {
  return score >= 67 ? '#ef4444' : score >= 34 ? '#f59e0b' : '#22c55e';
}

// footer: optional JSX to replace the default save/discard button row
export default function GameTheoryCard({
  card,
  revealed,
  onReveal,
  onSave,
  onDiscard,
  swiping,
  footer,
}) {
  const tmpl = TEMPLATES[card.template_type] || TEMPLATES.if_then;
  const heat = card.probability_heat_score;
  const hc = heatColor(heat);
  const gradId = `gt-grad-${card.template_type}`;
  const heatFill = Math.round(338 * heat / 100);

  // Swipe / drag-to-flip state
  const dragRef = useRef(null); // { startX, startY, moved }
  const [dragOffset, setDragOffset] = useState(0); // live tilt in px during drag
  const SWIPE_THRESHOLD = 40; // px to trigger flip

  const onPointerDown = (e) => {
    dragRef.current = { startX: e.clientX, startY: e.clientY, moved: false };
  };

  const onPointerMove = (e) => {
    if (!dragRef.current) return;
    const dx = e.clientX - dragRef.current.startX;
    const dy = e.clientY - dragRef.current.startY;
    if (Math.abs(dx) > 5) dragRef.current.moved = true;
    // Only tilt if mostly horizontal
    if (Math.abs(dx) > Math.abs(dy)) {
      setDragOffset(dx);
    }
  };

  const onPointerUp = (e) => {
    if (!dragRef.current) return;
    const dx = e.clientX - dragRef.current.startX;
    const dy = e.clientY - dragRef.current.startY;
    const wasDragging = dragRef.current.moved;
    dragRef.current = null;
    setDragOffset(0);
    // Trigger flip if horizontal swipe threshold met and mostly horizontal
    if (wasDragging && Math.abs(dx) >= SWIPE_THRESHOLD && Math.abs(dx) > Math.abs(dy) * 1.5) {
      if (onReveal) onReveal();
    }
  };

  const onPointerLeave = () => {
    dragRef.current = null;
    setDragOffset(0);
  };

  const renderSVGHeader = (isBack = false) => (
    <svg
      viewBox="0 0 370 155"
      width="100%"
      style={{ display: 'block' }}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id={`${gradId}-${isBack ? 'back' : 'front'}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={tmpl.gradStart} stopOpacity="0.9" />
          <stop offset="100%" stopColor={tmpl.gradStart} stopOpacity="0" />
        </linearGradient>
      </defs>

      {/* Background — transparent so the CSS container bg shows through */}
      <rect width="370" height="155" fill={`url(#${gradId}-${isBack ? 'back' : 'front'})`} />

      {/* Diagonal accent lines */}
      <line x1="0" y1="0" x2="370" y2="155" stroke={tmpl.color} strokeOpacity="0.06" strokeWidth="1" />
      <line x1="370" y1="0" x2="0" y2="155" stroke={tmpl.color} strokeOpacity="0.06" strokeWidth="1" />
      <line x1="185" y1="0" x2="185" y2="155" stroke={tmpl.color} strokeOpacity="0.04" strokeWidth="1" />
      <line x1="0" y1="77" x2="370" y2="77" stroke={tmpl.color} strokeOpacity="0.04" strokeWidth="1" />

      {/* Decorative aura circles */}
      <circle cx="310" cy="40" r="85" fill={tmpl.color} fillOpacity="0.06" />
      <circle cx="310" cy="40" r="52" fill={tmpl.color} fillOpacity="0.07" />
      <circle cx="55" cy="125" r="65" fill={tmpl.color} fillOpacity="0.05" />

      {/* Large background symbol */}
      <text
        x="185" y="105"
        fill={tmpl.color}
        fontSize="78"
        fontFamily="system-ui, sans-serif"
        textAnchor="middle"
        opacity="0.18"
        transform={isBack ? "scale(-1, 1) translate(-370, 0)" : "none"}
      >
        {tmpl.symbol}
      </text>

      {/* ── Template label badge (top-left) ── */}
      <rect x="0" y="0" width={tmpl.labelWidth} height="22" fill={tmpl.color} fillOpacity="0.92" rx="0" />
      {/* bottom-right corner rounding only */}
      <rect x={tmpl.labelWidth - 8} y="0" width="8" height="22" fill={tmpl.color} fillOpacity="0.92" />
      {/* mask corner with transparent — inherits container bg via CSS */}
      <rect x={tmpl.labelWidth - 8} y="14" width="8" height="8" style={{ fill: tmpl.innerBg }} />
      <text
        x="10" y="15"
        fill="#000"
        fontSize="8"
        letterSpacing="2"
        fontFamily="Courier New, monospace"
        fontWeight="800"
      >
        {isBack ? 'VERSO' : tmpl.shortLabel}
      </text>

      {/* ── Heat score (top-right) ── */}
      <text
        x="358" y="15"
        fill={hc}
        fontSize="10"
        fontFamily="Courier New, monospace"
        fontWeight="700"
        textAnchor="end"
      >
        HEAT {heat}
      </text>

      {/* ── Corner symbols ── */}
      {/* bottom-left */}
      <text
        x="14" y="140"
        fill={tmpl.accentColor}
        fontSize="20"
        fontFamily="system-ui, sans-serif"
        fontWeight="700"
        opacity="0.6"
      >
        {tmpl.symbol}
      </text>
      {/* top-right (rotated 180°) */}
      <g transform="translate(356,25) rotate(180)">
        <text
          x="0" y="0"
          fill={tmpl.accentColor}
          fontSize="20"
          fontFamily="system-ui, sans-serif"
          fontWeight="700"
          opacity="0.6"
        >
          {tmpl.symbol}
        </text>
      </g>

      {/* ── Heat bar ── */}
      <rect x="16" y="147" width="338" height="3" rx="1.5" fill="rgba(255,255,255,0.08)" />
      <rect x="16" y="147" width={heatFill} height="3" rx="1.5" fill={hc} />
    </svg>
  );

  const renderActionButtons = () => {
    if (footer !== undefined) return footer;
    if (!onSave && !onDiscard) return null;
    return (
      <div style={{ display: 'flex', gap: 8 }}>
        <button
          onClick={(e) => { e.stopPropagation(); onDiscard(); }}
          style={{
            flex: 1, padding: '11px 0', borderRadius: 8,
            border: '1px solid #ef4444',
            background: '#ef444411', color: '#ef4444', cursor: 'pointer',
            fontSize: 18, fontWeight: 700,
          }}
          title="Descartar"
        >
          ✕
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onSave(); }}
          style={{
            flex: 3, padding: '11px 0', borderRadius: 8, border: 'none',
            background: 'linear-gradient(135deg, #7c3aed, #6d28d9)',
            color: '#fff', cursor: 'pointer',
            fontSize: 11, fontWeight: 700, letterSpacing: 2,
            textTransform: 'uppercase', fontFamily: 'Courier New, monospace',
          }}
        >
          Salvar no Deck →
        </button>
      </div>
    );
  };

  const handleCardClick = (e) => {
    // Suppress click if the pointer was dragged significantly
    if (dragRef.current?.moved) return;
    if (onReveal) {
      onReveal();
    }
  };

  return (
    <div
      style={{
        background: tmpl.outerBg,
        borderRadius: 14,
        padding: 5,
        boxShadow: `0 0 36px ${tmpl.glowColor}, 0 20px 48px rgba(0,0,0,0.85)`,
        maxWidth: 380,
        width: '100%',
        transition: swiping ? 'transform 0.35s ease, opacity 0.35s ease' : 'transform 0.15s ease, opacity 0.35s ease',
        transform:
          swiping === 'right'
            ? 'translateX(120%) rotate(12deg)'
            : swiping === 'left'
              ? 'translateX(-120%) rotate(-12deg)'
              : dragOffset !== 0
                ? `translateX(${dragOffset * 0.08}px) rotate(${dragOffset * 0.015}deg)`
                : 'none',
        opacity: swiping ? 0 : 1,
        perspective: '1500px',
        cursor: 'grab',
        userSelect: 'none',
        touchAction: 'pan-y',
      }}
      onClick={handleCardClick}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerLeave={onPointerLeave}
    >
      {/* 3D Flipper Container */}
      <div
        style={{
          width: '100%',
          transition: 'transform 0.6s cubic-bezier(0.4, 0.2, 0.2, 1)',
          transformStyle: 'preserve-3d',
          transform: revealed ? 'rotateY(180deg)' : 'rotateY(0deg)',
          display: 'grid',
        }}
      >
        {/* Front Face */}
        <div
          style={{
            gridArea: '1 / 1 / 2 / 2',
            backfaceVisibility: 'hidden',
            background: tmpl.innerBg,
            borderRadius: 10,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {renderSVGHeader(false)}

          <div style={{ padding: '14px 16px 16px', flex: 1, display: 'flex', flexDirection: 'column' }}>
            {/* Scenario */}
            <div style={{ marginBottom: 14 }}>
              <p style={{
                color: tmpl.accentColor, fontSize: 8, letterSpacing: 3,
                textTransform: 'uppercase', fontFamily: 'Courier New, monospace',
                margin: '0 0 5px', fontWeight: 700,
              }}>
                ▸ Cenário
              </p>
              <p style={{ color: 'var(--text-main)', fontSize: 13, lineHeight: 1.7, margin: 0 }}>
                {card.scenario_context}
              </p>
            </div>

            {/* Question */}
            <div style={{
              background: 'rgba(255,255,255,0.04)',
              border: `1px solid ${tmpl.color}44`,
              borderLeft: `3px solid ${tmpl.color}`,
              borderRadius: '0 8px 8px 0',
              padding: '11px 13px',
              marginBottom: 14,
            }}>
              <p style={{
                color: tmpl.accentColor, fontSize: 8, letterSpacing: 3,
                textTransform: 'uppercase', fontFamily: 'Courier New, monospace',
                margin: '0 0 5px', fontWeight: 700,
              }}>
                ▸ Pergunta Tática
              </p>
              <p style={{ color: 'var(--text-main)', fontSize: 14, fontWeight: 600, lineHeight: 1.6, margin: 0 }}>
                {card.question}
              </p>
            </div>

            {/* Hint to click */}
            <div style={{
              width: '100%', padding: '10px 0', borderRadius: 8,
              border: `1px dashed ${tmpl.color}55`,
              background: `${tmpl.color}11`,
              color: tmpl.accentColor, textAlign: 'center',
              fontSize: 10, fontWeight: 700, letterSpacing: 2,
              textTransform: 'uppercase', fontFamily: 'Courier New, monospace',
              marginTop: 'auto', marginBottom: 14,
              animation: 'card-pulse 2s infinite',
            }}>
              ◈ Clica para Revelar o Oráculo
            </div>

            {/* Spacer for Action Buttons equivalent height so grid cells match nicely, 
                or we can just render them on both sides to keep size uniform */}
            {renderActionButtons()}
          </div>
        </div>

        {/* Back Face */}
        <div
          style={{
            gridArea: '1 / 1 / 2 / 2',
            backfaceVisibility: 'hidden',
            background: tmpl.innerBg,
            borderRadius: 10,
            overflow: 'hidden',
            transform: 'rotateY(180deg)',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {renderSVGHeader(true)}

          <div style={{ padding: '14px 16px 16px', flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div style={{
              background: 'rgba(34,197,94,0.05)',
              border: '1px solid rgba(34,197,94,0.2)',
              borderRadius: 8, padding: '11px 13px', marginBottom: 14,
            }}>
              <p style={{
                color: '#6ee7b7', fontSize: 8, letterSpacing: 3,
                textTransform: 'uppercase', fontFamily: 'Courier New, monospace',
                margin: '0 0 5px', fontWeight: 700,
              }}>
                ▸ Resultado Provável
              </p>
              <p style={{ color: 'var(--text-main)', fontSize: 13, lineHeight: 1.7, margin: 0 }}>
                {card.predicted_outcome}
              </p>
            </div>

            <div style={{
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.07)',
              borderRadius: 8, padding: '11px 13px',
              marginBottom: 14,
            }}>
              <p style={{
                color: 'var(--text-muted)', fontSize: 8, letterSpacing: 3,
                textTransform: 'uppercase', fontFamily: 'Courier New, monospace',
                margin: '0 0 5px', fontWeight: 700,
              }}>
                ▸ Análise · Teoria dos Jogos
              </p>
              <p style={{ color: 'var(--text-main)', fontSize: 13, lineHeight: 1.75, margin: 0 }}>
                {card.game_theory_explanation}
              </p>
            </div>

            <div style={{ marginTop: 'auto' }}>
              {renderActionButtons()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

