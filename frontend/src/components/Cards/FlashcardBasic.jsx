import { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { CustomSymbolTemplate } from '../Icons/ThemeIcons';
import { ContextMenuOverlay } from './GameTheoryCard'; // Re-use the overlay

export default function FlashcardBasic({
    card,
    revealed,
    onReveal,
    onSave,
    onDiscard,
    swiping,
    footer,
}) {
    const { t } = useTranslation();

    // Swipe / drag-to-flip state
    const dragRef = useRef(null);
    const [dragOffset, setDragOffset] = useState(0);
    const SWIPE_THRESHOLD = 40;

    // Context Menu state
    const pressTimer = useRef(null);
    const [showMenu, setShowMenu] = useState(false);

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
        }, 500);
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
            cancelPress();
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
        if (showMenu) return;
        if (dragRef.current?.moved) return;
        if (onReveal) onReveal();
    };

    const renderActionButtons = () => {
        if (footer !== undefined) return footer;
        if (!onSave && !onDiscard) return null;
        return (
            <>
                <button
                    onClick={(e) => { e.stopPropagation(); setShowMenu(false); onSave(); }}
                    style={{
                        width: '100%', padding: '14px 0', borderRadius: 8, border: 'none',
                        background: 'linear-gradient(135deg, #1d4ed8, #3b82f6)', color: '#fff', cursor: 'pointer',
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
            {showMenu && (
                <div style={{ position: 'absolute', inset: 0, zIndex: 9999, pointerEvents: 'auto' }}>
                    <ContextMenuOverlay onClose={() => setShowMenu(false)}>
                        {renderActionButtons()}
                    </ContextMenuOverlay>
                </div>
            )}

            {/* 3D Flipper Container */}
            <div style={{ width: '100%', height: '100%', minHeight: '400px', transition: 'transform 0.6s cubic-bezier(0.4, 0.2, 0.2, 1)', transformStyle: 'preserve-3d', transform: revealed ? 'rotateY(180deg)' : 'rotateY(0deg)', position: 'relative' }}>

                {/* FRONT FACE */}
                <div style={{ backfaceVisibility: 'hidden', WebkitBackfaceVisibility: 'hidden' }} className="relative w-full h-full card-inner-bg overflow-hidden flex flex-col bg-white rounded-xl shadow-lg border border-gray-200">
                    <div className="w-full text-gray-800 p-6 flex flex-col items-center justify-center text-center relative z-10 flex-grow">
                        <h3 className="text-sm font-semibold text-blue-600 mb-4 uppercase tracking-widest">{t('flashcard.question')}</h3>
                        <p className="text-xl leading-relaxed font-medium">
                            {card.question}
                        </p>
                    </div>
                    <div className="w-full p-4 bg-gray-50 text-center text-xs text-gray-400 uppercase tracking-widest font-semibold border-t border-gray-100">
                        {t('flashcard.tap_to_flip', 'Toque para virar')}
                    </div>
                </div>

                {/* BACK FACE */}
                <div style={{ position: 'absolute', inset: 0, backfaceVisibility: 'hidden', WebkitBackfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }} className="relative w-full h-full card-inner-bg overflow-hidden flex flex-col bg-blue-50 rounded-xl shadow-lg border border-blue-200">
                    <div className="w-full text-gray-800 p-6 flex flex-col items-center justify-center text-center relative z-10 flex-grow">
                        <h3 className="text-sm font-semibold text-green-600 mb-4 uppercase tracking-widest">{t('flashcard.answer')}</h3>
                        <p className="text-2xl leading-relaxed font-bold text-blue-900 mb-4">
                            {card.correct_answer || card.predicted_outcome}
                        </p>
                        {card.explanation && (
                            <div className="mt-4 p-4 bg-white/60 rounded-lg text-sm text-gray-700 italic border border-blue-100">
                                {card.explanation}
                            </div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
}
