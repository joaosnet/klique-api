// GameTheoryCard — physical trading card design for Game Theory scenarios
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
    outerBg: '#101e40',
    innerBg: '#060d1f',
    accentColor: '#93c5fd',
    glowColor: 'rgba(59,130,246,0.35)',
    symbol: '⚖',
    gradStart: '#1e3a8a',
    gradEnd: '#060d1f',
    btnBg: 'linear-gradient(135deg, #1d4ed8, #3b82f6)',
  },
  payoff_matrix: {
    shortLabel: 'RECOMPENSA',
    labelWidth: 105,
    color: '#fbbf24',
    darkColor: '#92400e',
    outerBg: '#2d1500',
    innerBg: '#0d0800',
    accentColor: '#fcd34d',
    glowColor: 'rgba(245,158,11,0.35)',
    symbol: '◈',
    gradStart: '#78350f',
    gradEnd: '#0d0800',
    btnBg: 'linear-gradient(135deg, #b45309, #f59e0b)',
  },
  black_swan: {
    shortLabel: 'CISNE NEGRO',
    labelWidth: 115,
    color: '#f87171',
    darkColor: '#7f1d1d',
    outerBg: '#1e0505',
    innerBg: '#0a0000',
    accentColor: '#fca5a5',
    glowColor: 'rgba(239,68,68,0.35)',
    symbol: '✦',
    gradStart: '#7f1d1d',
    gradEnd: '#0a0000',
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

  return (
    <div
      style={{
        background: tmpl.outerBg,
        borderRadius: 14,
        padding: 5,
        boxShadow: `0 0 36px ${tmpl.glowColor}, 0 20px 48px rgba(0,0,0,0.85)`,
        maxWidth: 380,
        width: '100%',
        transition: 'transform 0.35s ease, opacity 0.35s ease',
        transform:
          swiping === 'right'
            ? 'translateX(120%) rotate(12deg)'
            : swiping === 'left'
              ? 'translateX(-120%) rotate(-12deg)'
              : 'none',
        opacity: swiping ? 0 : 1,
      }}
    >
      {/* Inner card */}
      <div style={{ background: tmpl.innerBg, borderRadius: 10, overflow: 'hidden' }}>

        {/* ── SVG Art / Header Zone ── */}
        <svg
          viewBox="0 0 370 155"
          width="100%"
          style={{ display: 'block' }}
          aria-hidden="true"
        >
          <defs>
            <linearGradient id={gradId} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={tmpl.gradStart} />
              <stop offset="100%" stopColor={tmpl.gradEnd} />
            </linearGradient>
          </defs>

          {/* Background */}
          <rect width="370" height="155" fill={`url(#${gradId})`} />

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
          >
            {tmpl.symbol}
          </text>

          {/* ── Template label badge (top-left) ── */}
          <rect x="0" y="0" width={tmpl.labelWidth} height="22" fill={tmpl.color} fillOpacity="0.92" rx="0" />
          {/* bottom-right corner rounding only */}
          <rect x={tmpl.labelWidth - 8} y="0" width="8" height="22" fill={tmpl.color} fillOpacity="0.92" />
          <rect x={tmpl.labelWidth - 8} y="14" width="8" height="8" fill={tmpl.innerBg} />
          <text
            x="10" y="15"
            fill="#000"
            fontSize="8"
            letterSpacing="2"
            fontFamily="Courier New, monospace"
            fontWeight="800"
          >
            {tmpl.shortLabel}
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

        {/* ── HTML Content Area ── */}
        <div style={{ padding: '14px 16px 16px' }}>

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

          {/* Oracle reveal */}
          {!revealed ? (
            <button
              onClick={onReveal}
              style={{
                width: '100%', padding: '10px 0', borderRadius: 8,
                border: `1px solid ${tmpl.color}55`,
                background: `${tmpl.color}11`,
                color: tmpl.accentColor, cursor: 'pointer',
                fontSize: 10, fontWeight: 700, letterSpacing: 2,
                textTransform: 'uppercase', fontFamily: 'Courier New, monospace',
                marginBottom: 14,
              }}
            >
              ◈ Revelar Análise do Oráculo
            </button>
          ) : (
            <div style={{ marginBottom: 14 }}>
              <div style={{
                background: 'rgba(34,197,94,0.05)',
                border: '1px solid rgba(34,197,94,0.2)',
                borderRadius: 8, padding: '11px 13px', marginBottom: 8,
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
            </div>
          )}

          {/* Action buttons */}
          {footer ?? (onSave || onDiscard ? (
            <div style={{ display: 'flex', gap: 8 }}>
              <button
                onClick={onDiscard}
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
                onClick={onSave}
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
          ) : null)}
        </div>
      </div>
    </div>
  );
}
