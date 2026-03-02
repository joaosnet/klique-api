import { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { CustomSymbolTemplate } from '../Icons/ThemeIcons';
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
    shortLabel: 'if_then',
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
    shortLabel: 'payoff_matrix',
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
    shortLabel: 'black_swan',
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



function ContextMenuOverlay({ onClose, children }) {
  const { t } = useTranslation();
  return (
    <div
      onClick={(e) => { e.stopPropagation(); onClose(); }}
      style={{
        position: 'absolute', inset: 0, zIndex: 999,
        background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(8px)',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        padding: '24px', animation: 'fadeIn 0.2s ease-out', borderRadius: 16
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '100%', maxWidth: 240, display: 'flex', flexDirection: 'column', gap: 12,
          animation: 'scaleUp 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
        }}
      >
        <p style={{ color: '#fff', fontSize: 13, textAlign: 'center', fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 16 }}>{t('gameCard.actions')}</p>

        {children}

        <button
          onClick={(e) => { e.stopPropagation(); onClose(); }}
          style={{
            marginTop: 8, padding: '12px 0', borderRadius: 8, border: '1px solid rgba(255,255,255,0.2)',
            background: 'transparent', color: '#ccc', cursor: 'pointer', fontSize: 12, fontWeight: 600, textTransform: 'uppercase'
          }}
        >
          {t('gameCard.cancel')}
        </button>
      </div>
    </div>
  );
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
  customSvg,
}) {
  const tmpl = TEMPLATES[card.template_type] || TEMPLATES.if_then;
  const { t } = useTranslation();
  const heat = card.probability_heat_score;

  // Swipe / drag-to-flip state
  const dragRef = useRef(null);
  const [dragOffset, setDragOffset] = useState(0);
  const SWIPE_THRESHOLD = 40;

  // Context Menu state
  const pressTimer = useRef(null);
  const [showMenu, setShowMenu] = useState(false);

  // Stop any pending long-press if movement occurs or interaction ends
  const cancelPress = () => {
    if (pressTimer.current) {
      clearTimeout(pressTimer.current);
      pressTimer.current = null;
    }
  };

  const startPress = () => {
    cancelPress();
    pressTimer.current = setTimeout(() => {
      setShowMenu(true);
    }, 500); // 500ms long press threshold
  };

  const onPointerDown = (e) => {
    dragRef.current = { startX: e.clientX, startY: e.clientY, moved: false };
    startPress();
  };

  const onPointerMove = (e) => {
    if (!dragRef.current) return;
    const dx = e.clientX - dragRef.current.startX;
    const dy = e.clientY - dragRef.current.startY;
    if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
      dragRef.current.moved = true;
      cancelPress(); // Cancel long press if user moves pointer
    }
    if (Math.abs(dx) > Math.abs(dy)) setDragOffset(dx);
  };

  const onPointerUp = (e) => {
    cancelPress();
    if (!dragRef.current) return;
    const dx = e.clientX - dragRef.current.startX;
    const dy = e.clientY - dragRef.current.startY;
    const wasDragging = dragRef.current.moved;
    dragRef.current = null;
    setDragOffset(0);
    // Ignore swipe events acting as reveals if showing menu
    if (showMenu) return;

    if (wasDragging && Math.abs(dx) >= SWIPE_THRESHOLD && Math.abs(dx) > Math.abs(dy) * 1.5) {
      if (onReveal) onReveal();
    }
  };

  const onPointerLeave = () => {
    cancelPress();
    dragRef.current = null;
    setDragOffset(0);
  };

  const handleContextMenu = (e) => {
    e.preventDefault();
    setShowMenu(true);
  };

  const handleCardClick = () => {
    if (showMenu) return; // Disallow flip if menu is active
    if (dragRef.current?.moved) return;
    if (onReveal) onReveal();
  };

  const artVisual = customSvg
    ? <div className="w-full h-full absolute inset-0 z-0" dangerouslySetInnerHTML={{ __html: customSvg }} style={{ background: '#000' }} />
    : card.media_urls && card.media_urls[0]
      ? <img src={`${import.meta.env.VITE_API_URL || ''}${card.media_urls[0]}`} className="w-full h-full object-cover absolute inset-0 z-0 opacity-90" />
      : <div className="w-full h-full absolute inset-0 z-0 flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${tmpl.darkColor}, ${tmpl.color})` }}>
        <CustomSymbolTemplate type={card.template_type} width={120} height={120} color={tmpl.accentColor} opacity={0.3} />
      </div>;

  const renderActionButtons = () => {
    if (footer !== undefined) return footer;
    if (!onSave && !onDiscard) return null;
    return (
      <>
        <button
          onClick={(e) => { e.stopPropagation(); setShowMenu(false); onSave(); }}
          style={{
            width: '100%', padding: '14px 0', borderRadius: 8, border: 'none',
            background: tmpl.btnBg, color: '#fff', cursor: 'pointer',
            fontSize: 13, fontWeight: 700, letterSpacing: 2,
            textTransform: 'uppercase', fontFamily: '"Inter", system-ui, sans-serif',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
          }}
        >
          {t('gameCard.save')}
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); setShowMenu(false); onDiscard(); }}
          style={{
            width: '100%', padding: '14px 0', borderRadius: 8,
            border: '1px solid rgba(239, 68, 68, 0.4)', background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', cursor: 'pointer',
            fontSize: 13, fontWeight: 700, letterSpacing: 2,
            textTransform: 'uppercase', fontFamily: '"Inter", system-ui, sans-serif'
          }}
          title={t('gameCard.discard')}
        >
          {t('gameCard.discard')}
        </button>
      </>
    );
  };

  return (
    <div
      className="unmatched-card"
      style={{
        maxWidth: 380, width: '100%', cursor: 'grab', userSelect: 'none', touchAction: 'pan-y', margin: '0 auto',
        transition: swiping ? 'transform 0.35s ease, opacity 0.35s ease' : 'transform 0.15s ease, opacity 0.35s ease',
        transform:
          swiping === 'right' ? 'translateX(120%) rotate(12deg)'
            : swiping === 'left' ? 'translateX(-120%) rotate(-12deg)'
              : dragOffset !== 0 ? `translateX(${dragOffset * 0.08}px) rotate(${dragOffset * 0.015}deg)`
                : 'none',
        opacity: swiping ? 0 : 1, perspective: '1500px', position: 'relative'
      }}
      onClick={handleCardClick} onContextMenu={handleContextMenu} onPointerDown={onPointerDown} onPointerMove={onPointerMove} onPointerUp={onPointerUp} onPointerLeave={onPointerLeave}
    >
      <style dangerouslySetInnerHTML={{
        __html: `
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes scaleUp { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
      `}} />
      {showMenu && (
        <div style={{ position: 'absolute', inset: 0, zIndex: 9999, pointerEvents: 'auto' }}>
          <ContextMenuOverlay onClose={() => setShowMenu(false)}>
            {renderActionButtons()}
          </ContextMenuOverlay>
        </div>
      )}
      {/* 3D Flipper Container */}
      <div style={{ width: '100%', height: '100%', transition: 'transform 0.6s cubic-bezier(0.4, 0.2, 0.2, 1)', transformStyle: 'preserve-3d', transform: revealed ? 'rotateY(180deg)' : 'rotateY(0deg)', display: 'grid' }}>

        {/* FRONT FACE */}
        <div style={{ gridArea: '1 / 1 / 2 / 2', backfaceVisibility: 'hidden' }} className="relative w-full h-full card-inner-bg overflow-hidden flex flex-col">
          {/* Topo: Arte e Hexágono */}
          <div className="w-full relative overflow-hidden bg-gray-900 border-b-2 border-white" style={{ height: '55%' }}>
            {artVisual}
            <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/30 to-transparent z-0"></div>

            {/* Tag Superior Esquerda (Rank) */}
            <div className="absolute top-0 left-0 w-12 h-32 z-10 drop-shadow-[0_4px_6px_rgba(0,0,0,0.8)]">
              <svg viewBox="0 0 40 105" className="w-full h-full">
                <polygon points="0,0 40,0 40,90 20,105 0,90" fill={tmpl.color} />
                <g transform="translate(10, 10)">
                  <CustomSymbolTemplate type={card.template_type} width={20} height={20} color="#fff" />
                </g>
                <text x="20" y="60" fontFamily="'Anton', sans-serif" fontSize="28" fill="white" textAnchor="middle">{heat}</text>
                <text x="20" y="75" fontFamily="Courier New, monospace" fontSize="8" fill="rgba(255,255,255,0.8)" textAnchor="middle" fontWeight="bold">HEAT</text>
              </svg>
            </div>

            {/* Boost Marker */}
            <div className="absolute bottom-[-10px] right-3 z-20 w-8 h-8 rounded-full bg-black border-2 border-white flex items-center justify-center shadow-lg">
              <span className="font-title text-white text-sm mt-0.5">{tmpl.shortLabel[0]}</span>
            </div>
          </div>

          {/* Texto da Carta */}
          <div className="w-full text-white p-3 flex flex-col relative z-10 bg-black flex-grow">
            <h2 className="font-title text-xl tracking-wider leading-none mb-1 uppercase truncate" style={{ color: tmpl.color }}>
              {t(`gameCard.${tmpl.shortLabel}`)}
            </h2>
            <div className="w-full h-[1px] bg-gray-700 mb-2"></div>

            <div className="flex-grow flex flex-col justify-start space-y-2 overflow-hidden">
              <p className="text-xs font-bold text-gray-200 uppercase" style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                ► {card.scenario_context}
              </p>
              <p className="text-sm leading-tight text-white font-semibold flex-grow" style={{ display: '-webkit-box', WebkitLineClamp: 4, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                {card.question}
              </p>
            </div>

            {/* Hint to click */}
            <div style={{
              width: '100%', padding: '6px 0', borderRadius: 4, border: `1px dashed ${tmpl.color}55`, background: `${tmpl.color}11`,
              color: tmpl.accentColor, textAlign: 'center', fontSize: 9, fontWeight: 700, letterSpacing: 2, textTransform: 'uppercase',
              fontFamily: 'Courier New, monospace', marginTop: 'auto', marginBottom: 6, animation: 'card-pulse 2s infinite',
            }}>
              ◈ {t('gameCard.reveal_oracle')}
            </div>
          </div>
        </div>

        {/* BACK FACE */}
        <div style={{ gridArea: '1 / 1 / 2 / 2', backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }} className="relative w-full h-full card-inner-bg overflow-hidden flex flex-col">
          {/* Small Top Header for Back Face */}
          <div className="w-full relative overflow-hidden flex-shrink-0" style={{ height: '22%', background: `linear-gradient(135deg, ${tmpl.darkColor} 0%, #050505 100%)`, borderBottom: `2px solid ${tmpl.color}66` }}>
            {/* Background Symbol */}
            <div className="absolute inset-0 flex items-center justify-center opacity-10">
              <CustomSymbolTemplate type={card.template_type} width={100} height={100} color={tmpl.accentColor} />
            </div>
            <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
              <CustomSymbolTemplate type={card.template_type} width={24} height={24} color={tmpl.accentColor} style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.5))' }} />
              <h2 className="font-title text-xl tracking-widest text-white uppercase mt-1" style={{ textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>{t('gameCard.oracle')}</h2>
              <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: 9, letterSpacing: 2, textTransform: 'uppercase', fontFamily: '"Courier New", monospace', marginTop: 2 }}>
                {t(`gameCard.${tmpl.shortLabel}`)}
              </p>
            </div>
          </div>

          <div className="w-full text-white p-3 flex flex-col bg-black flex-grow overflow-y-auto no-scrollbar">

            <div style={{ background: 'rgba(34,197,94,0.1)', borderLeft: '3px solid #22c55e', borderRadius: '0 8px 8px 0', padding: '10px 12px', marginBottom: 12 }}>
              <p style={{ color: '#4ade80', fontSize: 9, letterSpacing: 2, textTransform: 'uppercase', fontFamily: 'Courier New, monospace', margin: '0 0 4px', fontWeight: 800 }}>
                ▸ {t('gameCard.predicted_outcome')}
              </p>
              <p style={{ color: '#f8fafc', fontSize: 13, lineHeight: 1.6, margin: 0, fontWeight: 500 }}>
                {card.predicted_outcome}
              </p>
            </div>

            <div style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, padding: '10px 12px', marginBottom: 10, flexGrow: 1 }}>
              <p style={{ color: 'var(--text-muted)', fontSize: 9, letterSpacing: 2, textTransform: 'uppercase', fontFamily: 'Courier New, monospace', margin: '0 0 4px', fontWeight: 800 }}>
                ▸ {t('gameCard.analysis')}
              </p>
              <p style={{ color: '#cbd5e1', fontSize: 12, lineHeight: 1.6, margin: 0 }}>
                {card.game_theory_explanation}
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

