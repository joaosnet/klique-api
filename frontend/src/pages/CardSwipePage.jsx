import { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { domainsAPI, cardsAPI, modelsAPI } from '../services/api';
import GameTheoryCard from '../components/Cards/GameTheoryCard';
import ConcursoCard from '../components/Cards/ConcursoCard';
import FlashcardBasic from '../components/Cards/FlashcardBasic';
import CardEditModal from '../components/Cards/CardEditModal';
import { useAuth } from '../context/AuthContext';
import { DEMO_CARDS, DEMO_DOMAINS } from '../utils/demoData';
import { IconDeckCard, IconDelete, IconEditPen, IconSparkBoost } from '../components/Icons/ActionIcons';

const API_URL = import.meta.env.VITE_API_URL || '';

const TEMPLATE_COLORS = {
  if_then: '#3b82f6',
  payoff_matrix: '#f59e0b',
  black_swan: '#ef4444',
};

export default function CardSwipePage() {
  const { t } = useTranslation();
  const { domainId } = useParams();
  const navigate = useNavigate();

  const [domain, setDomain] = useState(null);
  const [card, setCard] = useState(null);
  const [revealed, setRevealed] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState('');
  const [swiping, setSwiping] = useState(null);
  const [context, setContext] = useState('');
  const [cardFormat, setCardFormat] = useState('concurso_certo_errado');

  const [showCreateView, setShowCreateView] = useState(false);
  const [showFabMenu, setShowFabMenu] = useState(false);
  const [showAITools, setShowAITools] = useState(false);
  const [savedCards, setSavedCards] = useState([]);
  const [loadingCards, setLoadingCards] = useState(false);
  const [generateImage, setGenerateImage] = useState(true);

  const [showEditModal, setShowEditModal] = useState(false);
  const [editingCard, setEditingCard] = useState(null); // { card, cardId }
  const [pendingImageAction, setPendingImageAction] = useState(null);

  const [revealedCards, setRevealedCards] = useState({});
  const toggleReveal = (id) => setRevealedCards(prev => ({ ...prev, [id]: !prev[id] }));

  // Custom SVG model state
  const [customSvg, setCustomSvg] = useState(null);
  const [generatingSvg, setGeneratingSvg] = useState(false);
  const svgFileInputRef = useRef(null);

  const { isAuthenticated } = useAuth();
  const [demoIndex, setDemoIndex] = useState(0);
  const [showCTAModal, setShowCTAModal] = useState(false);
  const [demoComplete, setDemoComplete] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      const demoDomain = DEMO_DOMAINS.find(d => d.domain.id === domainId);
      setDomain(demoDomain ? demoDomain.domain : DEMO_DOMAINS[0].domain);
      setSavedCards(DEMO_CARDS); // Load demo cards straight to the deck
      return;
    }
    domainsAPI.getOne(domainId)
      .then((data) => setDomain(data.domain))
      .catch(() => navigate('/'));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [domainId, isAuthenticated]);

  const loadSavedCards = async () => {
    if (!isAuthenticated) return;
    setLoadingCards(true);
    try {
      const data = await cardsAPI.list(domainId);
      setSavedCards(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingCards(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) loadSavedCards();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, domainId]);

  const generateCard = async () => {
    setGenerating(true);
    setCard(null);
    setRevealed(false);
    setError('');
    setProgress(null);
    setPendingImageAction(null);

    try {
      if (!isAuthenticated) {
        if (demoIndex < DEMO_CARDS.length) {
          setTimeout(() => {
            setCard(DEMO_CARDS[demoIndex]);
            setDemoIndex(prev => prev + 1);
            setGenerating(false);
          }, 800);
        } else {
          setDemoComplete(true);
          setGenerating(false);
        }
        return;
      }

      const requestBody = { domain_id: domainId, context: context || null, card_format: cardFormat };
      const result = await cardsAPI.generateStream(requestBody, (p) => setProgress(p));
      if (result?.card) {
        setCard(result.card);
      } else {
        setError(t('training.unexpectedResponse'));
      }
    } catch (e) {
      setError(e.message || t('training.generationError'));
    } finally {
      setGenerating(false);
      setProgress(null);
    }
  };

  const handleUploadSvgModel = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setGeneratingSvg(true);
    setError('');

    try {
      const result = await modelsAPI.generateSVG(file);
      if (result.success && result.svg) {
        setCustomSvg(result.svg);
      } else {
        throw new Error('Falha ao gerar o modelo SVG');
      }
    } catch (err) {
      setError(err.message || 'Erro ao gerar o modelo da carta com IA.');
      console.error(err);
    } finally {
      setGeneratingSvg(false);
      // Reset input so the same file can be selected again
      if (svgFileInputRef.current) svgFileInputRef.current.value = '';
    }
  };

  const handleSwipe = async (action) => {
    if (!card) return;
    setSwiping(action === 'save' ? 'right' : 'left');

    if (!isAuthenticated) {
      setTimeout(() => setShowCTAModal(true), 350);
      return;
    }

    try {
      if (action === 'save') {
        const doGenerate = pendingImageAction ? pendingImageAction.type === 'generate' : generateImage;
        const result = await cardsAPI.swipe(card, domainId, action, doGenerate);
        const newCardId = result?.card_id;

        // Execute pending image action after save
        if (newCardId && pendingImageAction && pendingImageAction.type !== 'generate') {
          try {
            if (pendingImageAction.type === 'improve' && pendingImageAction.stylePrompt) {
              await cardsAPI.improveImage(newCardId, pendingImageAction.stylePrompt);
            } else if (pendingImageAction.type === 'upload' && pendingImageAction.file) {
              await cardsAPI.uploadImage(newCardId, pendingImageAction.file);
            }
          } catch (imgErr) {
            console.error('Erro na ação de imagem pendente:', imgErr);
          }
        }

        await loadSavedCards();
      } else {
        await cardsAPI.swipe(card, domainId, action, false);
      }
    } catch (e) {
      console.error(e);
    }

    setTimeout(() => {
      setSwiping(null);
      setCard(null);
      setRevealed(false);
      setPendingImageAction(null);
    }, 350);
  };

  const handleCreateManual = () => {
    setShowCreateView(true);
    setEditingCard({
      cardId: null,
      card: {
        template_type: 'if_then',
        scenario_context: '',
        question: '',
        predicted_outcome: '',
        game_theory_explanation: '',
        probability_heat_score: 50,
        visual_prompt_idea: '',
      }
    });
    setShowEditModal(true);
  };

  const handleEditCard = (cardToEdit, cardId) => {
    setEditingCard({ card: cardToEdit, cardId });
    setShowEditModal(true);
  };

  const handleEditSave = (updatedCard, imgAction) => {
    if (!editingCard.cardId) {
      // Pre-save edit
      setCard(updatedCard);
      if (imgAction) setPendingImageAction(imgAction);
    } else {
      // Edit of saved card - refresh list
      loadSavedCards();
    }
    setShowEditModal(false);
    setEditingCard(null);
  };

  const handleDeleteCard = async (cardId) => {
    if (!window.confirm(t('cards.confirmDelete'))) return;
    try {
      await cardsAPI.remove(cardId);
      setSavedCards(prev => prev.filter(c => c.id !== cardId));
    } catch (e) {
      console.error(e);
    }
  };

  const handleModalDismiss = () => {
    setShowCTAModal(false);
    setSwiping(null);
    setCard(null);
    setRevealed(false);
    if (demoIndex >= DEMO_CARDS.length) setDemoComplete(true);
  };

  if (demoComplete) {
    return (
      <div style={{ minHeight: 'calc(100vh - 56px)', background: '#12121a', padding: '2rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ maxWidth: 400, width: '100%', textAlign: 'center', background: 'var(--bg-card)', padding: '2rem', borderRadius: 16, border: '1px solid var(--border-color)' }}>
          <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'center' }}><IconDeckCard width={56} height={56} /></div>
          <h2 style={{ color: 'var(--text-highlight)', fontSize: 22, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 12 }}>{t('training.demoCompleteTitle')}</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: 14, lineHeight: 1.7, marginBottom: 28 }}>
            {t('training.demoCompleteDescription')}
          </p>
          <Link to="/register" style={{ display: 'block', width: '100%', padding: '14px 0', borderRadius: 10, boxSizing: 'border-box', background: 'var(--accent)', color: '#fff', textAlign: 'center', fontWeight: 800, fontSize: 13, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 12, textDecoration: 'none' }}>
            {t('training.activateOracle')}
          </Link>
          <button onClick={() => navigate('/')} style={{ display: 'block', width: '100%', background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 12, cursor: 'pointer', letterSpacing: 1, textTransform: 'uppercase' }}>
            {t('common.backToHome')}
          </button>
        </div>
      </div>
    );
  }

  // Not creating if unauth, show deck immediately
  const isCreating = isAuthenticated ? (savedCards.length === 0 || showCreateView) : false;

  return (
    <div style={{ minHeight: 'calc(100vh - 56px)', padding: '2rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
      <div style={{ width: '100%', maxWidth: isCreating ? 520 : 1200 }}>
        {/* Header */}
        <div style={{ marginBottom: '1.25rem' }}>
          <button onClick={() => navigate('/')} style={{ background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', fontSize: 13, padding: 0, marginBottom: 6 }}>
            ← {t('cards.domains')}
          </button>
          {domain && (
            <h1 style={{ color: 'var(--text-highlight)', fontSize: 20, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase', margin: 0 }}>
              {domain.name}
            </h1>
          )}
        </div>

        {/* ======================== CREATE / EMPTY STATE ======================== */}
        {isCreating && (
          <div style={{ width: '100%', maxWidth: 520, margin: '0 auto' }}>
            {savedCards.length > 0 && (
              <div style={{ marginBottom: '1rem' }}>
                <button
                  onClick={() => setShowCreateView(false)}
                  style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 13, padding: 0, display: 'flex', alignItems: 'center', gap: 6, opacity: 0.8 }}
                >
                  <span style={{ fontSize: 16 }}>←</span> {t('cards.backToDeck')}
                </button>
              </div>
            )}
            <p style={{ color: 'var(--text-muted)', fontSize: 12, marginBottom: '1rem', textAlign: 'center' }}>
              {t('cards.createOrUseOracle')}
            </p>

            {/* Main Create Button */}
            <div style={{ marginBottom: '2rem' }}>
              <button
                onClick={handleCreateManual}
                disabled={generating}
                style={{ width: '100%', padding: '16px 0', borderRadius: 12, border: 'none', background: 'var(--accent)', color: '#fff', fontSize: 14, fontWeight: 800, letterSpacing: 1, cursor: generating ? 'default' : 'pointer', textTransform: 'uppercase', boxShadow: '0 4px 12px rgba(0,0,0,0.2)', transition: 'transform 0.2s', transform: generating ? 'scale(0.98)' : 'scale(1)' }}
              >
                {t('cards.createManual')}
              </button>
            </div>

            {/* AI Tolls Toggle */}
            <div style={{ marginBottom: showAITools ? '1rem' : '2rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
              <button
                onClick={() => setShowAITools(!showAITools)}
                style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'none', border: 'none', color: 'var(--text-highlight)', fontSize: 13, fontWeight: 700, cursor: 'pointer', padding: 0 }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <IconSparkBoost width={16} height={16} />
                  <span>{t('training.useOracle')}</span>
                </div>
                <span style={{ transform: showAITools ? 'rotate(180deg)' : 'none', transition: 'transform 0.3s' }}>▼</span>
              </button>
            </div>

            {/* AI Tools Section */}
            {showAITools && (
              <div style={{ background: 'var(--bg-card)', padding: '1rem', borderRadius: 12, border: '1px solid var(--border-color)', marginBottom: '2rem', animation: 'fadeIn 0.3s ease-out' }}>
                <p style={{ color: 'var(--text-muted)', fontSize: 11, marginBottom: '1rem' }}>
                  {t('training.oracleDescription')}
                </p>

                {/* Context input */}
                <div style={{ marginBottom: '1rem' }}>
                  <input
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                    placeholder={t('training.contextPlaceholder')}
                    style={{ width: '100%', background: 'var(--bg-card-inner)', border: '1px solid var(--border-color)', color: 'var(--text-main)', borderRadius: 8, padding: '10px 12px', fontSize: 13, outline: 'none', boxSizing: 'border-box' }}
                  />
                </div>

                {/* Format selection */}
                <div style={{ marginBottom: '1.25rem' }}>
                  <p style={{ margin: '0 0 8px 0', fontSize: 12, color: 'var(--text-highlight)', fontWeight: 600 }}>Formato da Questão</p>
                  <select
                    value={cardFormat}
                    onChange={(e) => setCardFormat(e.target.value)}
                    style={{ width: '100%', background: 'var(--bg-card-inner)', border: '1px solid var(--border-color)', color: 'var(--text-main)', borderRadius: 8, padding: '10px 12px', fontSize: 13, outline: 'none' }}
                  >
                    <option value="concurso_certo_errado">Concurso (Certo/Errado)</option>
                    <option value="concurso_multipla_escolha">Concurso (Múltipla Escolha)</option>
                    <option value="flashcard_basico">Flashcard Básico (Frente/Verso)</option>
                    <option value="game_theory">Teoria dos Jogos (Avançado)</option>
                  </select>
                </div>

                {/* Custom SVG Background Generator */}
                {isAuthenticated && (
                  <div style={{ marginBottom: '1.25rem', padding: '12px', background: 'var(--bg-card-inner)', borderRadius: 8, border: '1px dashed var(--accent)' }}>
                    <p style={{ margin: '0 0 8px 0', fontSize: 12, color: 'var(--text-highlight)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}><IconSparkBoost width={14} height={14} /> {t('cards.createVisualModel')}</p>
                    <p style={{ margin: '0 0 10px 0', fontSize: 11, color: 'var(--text-muted)' }}>{t('cards.changeBackground')}</p>
                    <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                      <button
                        onClick={() => svgFileInputRef.current?.click()}
                        disabled={generatingSvg}
                        style={{ background: 'transparent', border: '1px solid var(--accent)', color: 'var(--accent)', padding: '6px 12px', borderRadius: 6, fontSize: 12, cursor: generatingSvg ? 'default' : 'pointer', fontWeight: 600, transition: 'all 0.2s', flexShrink: 0 }}
                      >
                        {generatingSvg ? t('common.processing') : t('cards.uploadImage')}
                      </button>
                      <input
                        type="file"
                        accept="image/*"
                        ref={svgFileInputRef}
                        style={{ display: 'none' }}
                        onChange={handleUploadSvgModel}
                      />
                      {customSvg && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ fontSize: 11, color: '#4ade80', fontWeight: 700 }}>✓ {t('cards.applied')}</span>
                          <button onClick={() => setCustomSvg(null)} style={{ background: 'none', border: 'none', color: '#ef4444', fontSize: 11, cursor: 'pointer', padding: 0 }}>{t('cards.remove')}</button>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* AI image toggle — only for authenticated */}
                {isAuthenticated && !card && (
                  <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', marginBottom: '1rem', color: 'var(--text-muted)', fontSize: 12 }}>
                    <input
                      type="checkbox"
                      checked={generateImage}
                      onChange={e => setGenerateImage(e.target.checked)}
                      style={{ accentColor: 'var(--accent)', width: 14, height: 14 }}
                    />
                    {t('cards.generateImageOnSave')}
                  </label>
                )}

                {/* Generate AI button */}
                <button
                  onClick={generateCard}
                  disabled={generating}
                  style={{ width: '100%', padding: '12px 0', borderRadius: 10, border: '1px solid var(--accent)', background: generating ? 'var(--bg-card-inner)' : 'transparent', color: 'var(--accent)', fontSize: 12, fontWeight: 700, letterSpacing: 1, cursor: generating ? 'default' : 'pointer', textTransform: 'uppercase', transition: 'background 0.2s' }}
                >
                  {generating ? (progress ? `${progress.message} (${progress.percent}%)` : t('training.generating')) : t('training.generateNewScenario')}
                </button>

                {error && (
                  <div style={{ background: '#7f1d1d', border: '1px solid #ef4444', borderRadius: 8, padding: '10px 14px', marginTop: 16, color: '#fca5a5', fontSize: 13 }}>
                    {error}
                  </div>
                )}
              </div>
            )}

            {/* Pending image action badge */}
            {pendingImageAction && (
              <div style={{ marginBottom: 16, padding: '8px 12px', borderRadius: 8, background: '#7c3aed22', border: '1px solid #7c3aed44', color: '#a78bfa', fontSize: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>{t('cards.pendingAction')}: {pendingImageAction.type === 'generate' ? t('cards.generateWithAI') : pendingImageAction.type === 'improve' ? t('cards.improve', { style: pendingImageAction.stylePrompt }) : pendingImageAction.type === 'upload' ? t('cards.uploadFile') : pendingImageAction.type}</span>
                <button onClick={() => setPendingImageAction(null)} style={{ background: 'none', border: 'none', color: '#a78bfa', cursor: 'pointer', fontSize: 16, padding: '0 4px' }}>&times;</button>
              </div>
            )}

            {/* Display Generated AI Card (for swiping) */}
            {card && (
              <div style={{ marginTop: '1rem' }}>
                {/* Edit button above card */}
                {isAuthenticated && (
                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 8, maxWidth: 380, margin: '0 auto 8px auto' }}>
                    <button
                      onClick={() => handleEditCard(card, null)}
                      style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--border-color)', color: 'var(--text-muted)', borderRadius: 6, padding: '6px 14px', fontSize: 11, cursor: 'pointer', letterSpacing: 1, fontWeight: 600 }}
                    >
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                        <IconEditPen width={14} height={14} /> {t('cardEdit.editScene')}
                      </span>
                    </button>
                  </div>
                )}

                <p style={{ color: 'var(--text-muted)', fontSize: 12, marginBottom: 16, textAlign: 'center' }}>
                  {t('cards.swipeInstruction')}
                </p>

                {(() => {
                  const props = {
                    card,
                    revealed,
                    onReveal: () => setRevealed(r => !r),
                    onSave: () => handleSwipe('save'),
                    onDiscard: () => handleSwipe('discard'),
                    swiping,
                    customSvg
                  };
                  if (card.card_format === 'concurso_certo_errado' || card.card_format === 'concurso_multipla_escolha') {
                    return <ConcursoCard {...props} />;
                  }
                  if (card.card_format === 'flashcard_basico') {
                    return <FlashcardBasic {...props} />;
                  }
                  return <GameTheoryCard {...props} />;
                })()}
              </div>
            )}

            {!card && !generating && (
              <div style={{ textAlign: 'center', marginTop: 60, color: 'var(--text-muted)' }}>
                <p style={{ marginBottom: 16, opacity: 0.75, display: 'flex', justifyContent: 'center' }}><IconDeckCard width={44} height={44} /></p>
                <p style={{ fontSize: 14 }}>{t('cards.createOrUseOracle')}</p>
              </div>
            )}
          </div>
        )}

        {/* ======================== DECK ======================== */}
        {!isCreating && (
          <div>
            {/* FAB wrapper */}
            {isAuthenticated && (
              <div style={{ position: 'fixed', bottom: '90px', right: '1.5rem', zIndex: 9999, display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 12 }}>

                {/* Mini buttons menu */}
                {showFabMenu && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10, alignItems: 'flex-end', animation: 'fadeInUp 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275)' }}>
                    <button
                      onClick={() => { setShowFabMenu(false); setShowCreateView(true); }}
                      style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', color: 'var(--text-main)', padding: '10px 16px', borderRadius: 20, fontSize: 13, fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 12px rgba(0,0,0,0.3)', display: 'flex', alignItems: 'center', gap: 8, transformOrigin: 'right center' }}
                    >
                      {t('training.generateOracleAI')}
                      <IconSparkBoost width={16} height={16} />
                    </button>
                    <button
                      onClick={() => { setShowFabMenu(false); handleCreateManual(); }}
                      style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', color: 'var(--text-main)', padding: '10px 16px', borderRadius: 20, fontSize: 13, fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 12px rgba(0,0,0,0.3)', display: 'flex', alignItems: 'center', gap: 8, transformOrigin: 'right center' }}
                    >
                      {t('cards.createManual')}
                      <IconEditPen width={16} height={16} />
                    </button>
                  </div>
                )}

                {/* Main FAB */}
                <button
                  onClick={() => setShowFabMenu(!showFabMenu)}
                  style={{
                    width: 60, height: 60, borderRadius: 30, background: 'var(--accent)', color: '#fff', fontSize: 28,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    boxShadow: '0 4px 16px rgba(0,0,0,0.4)', border: 'none', cursor: 'pointer',
                    transition: 'transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), background 0.2s',
                    transform: showFabMenu ? 'rotate(45deg)' : 'rotate(0deg)',
                    paddingBottom: 2
                  }}
                  title="Adicionar carta"
                >
                  +
                </button>

                <style dangerouslySetInnerHTML={{
                  __html: `
                  @keyframes fadeInUp {
                    from { opacity: 0; transform: translateY(20px) scale(0.9); }
                    to { opacity: 1; transform: translateY(0) scale(1); }
                  }
                `}} />
              </div>
            )}

            {loadingCards ? (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: 40 }}>{t('common.loading')}</p>
            ) : (
              <>
                <p style={{ color: 'var(--text-muted)', fontSize: 12, marginBottom: 20, textAlign: 'center' }}>
                  {t('cards.cardOptionsInstruction')}
                </p>
                <div className="flex overflow-x-auto snap-x snap-mandatory gap-6 pb-6 w-full px-2 sm:px-0 sm:flex-wrap sm:justify-center sm:gap-6 sm:overflow-visible sm:pb-0" style={{ scrollPadding: '1rem', WebkitOverflowScrolling: 'touch' }}>
                  {savedCards.map((c, idx) => {
                    const uniqueId = c.id ?? c._id ?? `card-${idx}`;
                    const props = {
                      card: c,
                      revealed: !!revealedCards[uniqueId],
                      onReveal: () => toggleReveal(uniqueId),
                      customSvg: c.customSvg,
                      footer: (
                        <>
                          <button
                            onClick={(e) => { e.stopPropagation(); document.body.click(); handleEditCard(c, c.id); }}
                            style={{
                              width: '100%', padding: '14px 0', borderRadius: 8, border: '1px solid var(--border-color)',
                              background: 'var(--bg-card-inner)', color: '#fff', cursor: 'pointer',
                              fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1,
                              marginBottom: 8
                            }}
                          >
                            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}><IconEditPen width={15} height={15} /> {t('cardEdit.editCard')}</span>
                          </button>
                          <button
                            onClick={(e) => { e.stopPropagation(); document.body.click(); handleDeleteCard(c.id); }}
                            style={{
                              width: '100%', padding: '14px 0', borderRadius: 8, border: '1px solid rgba(239, 68, 68, 0.4)',
                              background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', cursor: 'pointer',
                              fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1
                            }}
                          >
                            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}><IconDelete width={15} height={15} /> {t('cardEdit.deleteCard')}</span>
                          </button>
                        </>
                      )
                    };

                    let CardElem = GameTheoryCard;
                    if (c.card_format === 'concurso_certo_errado' || c.card_format === 'concurso_multipla_escolha') {
                      CardElem = ConcursoCard;
                    } else if (c.card_format === 'flashcard_basico') {
                      CardElem = FlashcardBasic;
                    }

                    return (
                      <div key={uniqueId} className="snap-center shrink-0 w-[85vw] max-w-[380px] sm:w-[calc(50%-12px)] lg:w-[calc(33.333%-16px)] xl:w-[calc(25%-18px)] flex flex-col items-center">
                        <CardElem {...props} />
                        {/* Fake Swipe Buttons for Demo */}
                        {!isAuthenticated && (
                          <div style={{ display: 'flex', gap: 12, marginTop: 16, width: '100%' }}>
                            <button
                              onClick={() => {
                                setSwiping('left');
                                setTimeout(() => setShowCTAModal(true), 350);
                              }}
                              style={{ flex: 1, padding: '14px 0', borderRadius: 8, border: '1px solid rgba(239, 68, 68, 0.4)', background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', cursor: 'pointer', fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1 }}
                            >
                              Descarta
                            </button>
                            <button
                              onClick={() => {
                                setSwiping('right');
                                setTimeout(() => setShowCTAModal(true), 350);
                              }}
                              style={{ flex: 1, padding: '14px 0', borderRadius: 8, border: '1px solid rgba(74, 222, 128, 0.4)', background: 'rgba(74, 222, 128, 0.15)', color: '#4ade80', cursor: 'pointer', fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1 }}
                            >
                              Guardar
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </>
            )}
          </div>
        )}

        {/* CTA Modal */}
        {showCTAModal && (
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200, padding: '1rem', backdropFilter: 'blur(4px)' }} onClick={handleModalDismiss}>
            <div style={{ background: 'var(--bg-card)', border: '1px solid var(--accent)', borderRadius: 16, padding: '2rem', maxWidth: 380, width: '100%' }} onClick={(e) => e.stopPropagation()}>
              <div style={{ textAlign: 'center', marginBottom: 12, display: 'flex', justifyContent: 'center' }}><IconSparkBoost width={40} height={40} /></div>
              <h2 style={{ color: 'var(--text-highlight)', fontSize: 20, fontWeight: 800, textAlign: 'center', letterSpacing: 2, textTransform: 'uppercase', marginBottom: 8 }}>{t('training.likeAnalysis')}</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: 13, textAlign: 'center', lineHeight: 1.7, marginBottom: 24 }}>
                {t('training.ctaDescription')}
              </p>
              <Link to="/register" style={{ display: 'block', padding: '13px 0', borderRadius: 10, background: 'var(--accent)', color: '#fff', textAlign: 'center', fontWeight: 800, fontSize: 13, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 10, textDecoration: 'none' }}>
                {t('training.createAccount')}
              </Link>
              <button onClick={handleModalDismiss} style={{ width: '100%', padding: '11px 0', borderRadius: 10, border: '1px solid var(--border-color)', background: 'transparent', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 12, letterSpacing: 1, textTransform: 'uppercase' }}>
                {t('common.close')}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Card Edit Modal */}
      {showEditModal && editingCard && (
        <CardEditModal
          card={editingCard.card}
          cardId={editingCard.cardId}
          onSave={handleEditSave}
          onClose={() => { setShowEditModal(false); setEditingCard(null); }}
        />
      )}
    </div>
  );
}
