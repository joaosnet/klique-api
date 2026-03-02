import { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ContextMenuOverlay } from './GameTheoryCard'; // Re-use the overlay

export default function ConcursoCard({
    card,
    revealed,
    onReveal,
    onSave,
    onDiscard,
    swiping,
    footer,
}) {
    const { t } = useTranslation();
    const isCE = card.card_format === 'concurso_certo_errado';
    const isME = card.card_format === 'concurso_multipla_escolha';

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
                        background: 'linear-gradient(135deg, #16a34a, #22c55e)', color: '#fff', cursor: 'pointer',
                        fontSize: 13, fontWeight: 700, letterSpacing: 2,
                        textTransform: 'uppercase', fontFamily: '"Inter", system-ui, sans-serif',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
                    }}
                >
                    {t('gameCard.save', 'Salvar na Revisão')}
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
                    {t('gameCard.discard', 'Descartar')}
                </button>
            </>
        );
    };

    const renderOptions = () => {
        if (!card.options || card.options.length === 0) return null;
        const labels = ['A', 'B', 'C', 'D', 'E'];
        return (
            <div className="flex flex-col gap-2 mt-4 w-full px-2" onClick={(e) => e.stopPropagation()}>
                {card.options.map((opt, i) => (
                    <button
                        key={i}
                        className="w-full text-left p-2.5 rounded border border-gray-200 hover:bg-gray-50 flex items-start gap-3 transition-colors text-sm"
                    >
                        <span className="font-bold text-gray-500 whitespace-nowrap">{labels[i]})</span>
                        <span className="text-gray-700">{opt}</span>
                    </button>
                ))}
            </div>
        );
    };

    const renderCEButtons = () => {
        return (
            <div className="flex justify-center gap-4 mt-6 w-full px-4" onClick={(e) => e.stopPropagation()}>
                <button className="flex-1 py-3 px-4 rounded-full border-2 border-green-500 text-green-700 font-bold hover:bg-green-50 transition-colors uppercase tracking-widest text-sm">
                    {t('concursoCard.correct')}
                </button>
                <button className="flex-1 py-3 px-4 rounded-full border-2 border-red-500 text-red-700 font-bold hover:bg-red-50 transition-colors uppercase tracking-widest text-sm">
                    {t('concursoCard.wrong')}
                </button>
            </div>
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
            <div style={{ width: '100%', height: '100%', minHeight: '440px', transition: 'transform 0.6s cubic-bezier(0.4, 0.2, 0.2, 1)', transformStyle: 'preserve-3d', transform: revealed ? 'rotateY(180deg)' : 'rotateY(0deg)', position: 'relative' }}>

                {/* FRONT FACE (Enunciado) */}
                <div style={{ backfaceVisibility: 'hidden', WebkitBackfaceVisibility: 'hidden' }} className="relative w-full h-full overflow-hidden flex flex-col bg-white rounded-xl shadow-md border border-gray-200">

                    <div className="w-full bg-slate-800 text-white py-2 px-4 shadow-sm flex items-center justify-between z-10">
                        <span className="text-xs font-bold uppercase tracking-widest text-slate-300">
                            {isCE ? t('concursoCard.styleCebraspe') : t('concursoCard.multipleChoice')}
                        </span>
                        <span className="text-[10px] bg-slate-700 px-2 py-0.5 rounded text-white font-mono">
                            {t('concursoCard.unpublishedQuestion')}
                        </span>
                    </div>

                    <div className="w-full text-gray-800 p-5 flex flex-col items-start justify-start text-left relative z-10 flex-grow bg-[url('https://www.transparenttextures.com/patterns/cream-paper.png')]">
                        {card.scenario_context && (
                            <p className="text-xs font-semibold text-gray-500 mb-3 border-l-2 border-blue-400 pl-2">
                                {card.scenario_context}
                            </p>
                        )}
                        <p className="text-[15px] leading-relaxed font-medium">
                            {card.question}
                        </p>

                        {isME && !revealed && renderOptions()}
                        {isCE && !revealed && renderCEButtons()}

                        {!isME && !isCE && (
                            <div className="mt-auto w-full text-center text-xs text-blue-500 font-semibold uppercase tracking-widest pt-4 animate-pulse">
                                {t('concursoCard.seeAnswer')}
                            </div>
                        )}
                    </div>
                </div>

                {/* BACK FACE (Gabarito) */}
                <div style={{ position: 'absolute', inset: 0, backfaceVisibility: 'hidden', WebkitBackfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }} className="relative w-full h-full overflow-hidden flex flex-col bg-slate-50 rounded-xl shadow-lg border border-slate-200">

                    <div className="w-full bg-slate-800 text-white py-2 px-4 shadow-sm flex items-center justify-center z-10">
                        <span className="text-xs font-bold uppercase tracking-widest text-green-400">{t('concursoCard.answerAndComments')}</span>
                    </div>

                    <div className="w-full text-gray-800 p-5 flex flex-col items-start justify-start text-left relative z-10 flex-grow overflow-y-auto no-scrollbar">

                        <div className="w-full bg-white rounded-lg border border-gray-200 p-4 shadow-sm mb-4">
                            <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider mb-1 block">{t('concursoCard.aiPrediction')}</span>
                            <p className="text-lg font-bold text-slate-800 break-words">
                                {card.correct_answer || (isCE ? card.predicted_outcome : 'N/A')}
                            </p>
                        </div>

                        <div className="w-full bg-blue-50/50 rounded-lg border border-blue-100 p-4">
                            <span className="text-[10px] uppercase font-bold text-blue-400 tracking-wider mb-2 block">{t('concursoCard.teacherExplanation')}</span>
                            <p className="text-sm font-medium text-slate-700 leading-relaxed whitespace-pre-wrap">
                                {card.explanation || card.game_theory_explanation}
                            </p>
                        </div>

                    </div>
                </div>

            </div>
        </div>
    );
}
