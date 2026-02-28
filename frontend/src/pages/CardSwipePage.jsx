import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { domainsAPI, cardsAPI } from '../services/api';
import GameTheoryCard from '../components/Cards/GameTheoryCard';
import CardEditModal from '../components/Cards/CardEditModal';
import { useAuth } from '../context/AuthContext';
import { DEMO_CARDS, DEMO_DOMAINS } from '../utils/demoData';

const API_URL = import.meta.env.VITE_API_URL || '';

const TEMPLATE_COLORS = {
  if_then: '#3b82f6',
  payoff_matrix: '#f59e0b',
  black_swan: '#ef4444',
};

function heatColor(score) {
  if (score >= 67) return '#ef4444';
  if (score >= 34) return '#f59e0b';
  return '#22c55e';
}

export default function CardSwipePage() {
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

  const [activeTab, setActiveTab] = useState('generate');
  const [savedCards, setSavedCards] = useState([]);
  const [loadingCards, setLoadingCards] = useState(false);
  const [generateImage, setGenerateImage] = useState(true);

  const [showEditModal, setShowEditModal] = useState(false);
  const [editingCard, setEditingCard] = useState(null); // { card, cardId }
  const [pendingImageAction, setPendingImageAction] = useState(null);

  const { isAuthenticated } = useAuth();
  const [demoIndex, setDemoIndex] = useState(0);
  const [showCTAModal, setShowCTAModal] = useState(false);
  const [demoComplete, setDemoComplete] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      const demoDomain = DEMO_DOMAINS.find(d => d.domain.id === domainId);
      setDomain(demoDomain ? demoDomain.domain : DEMO_DOMAINS[0].domain);
      return;
    }
    domainsAPI.getOne(domainId)
      .then((data) => setDomain(data.domain))
      .catch(() => navigate('/'));
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

      const result = await cardsAPI.generateStream(domainId, context || null, (p) => setProgress(p));
      if (result?.card) {
        setCard(result.card);
      } else {
        setError('Resposta inesperada da IA. Tente novamente.');
      }
    } catch (e) {
      setError(e.message || 'Erro ao gerar cenário. Verifica a ligação.');
    } finally {
      setGenerating(false);
      setProgress(null);
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
    if (!window.confirm('Tens a certeza que queres apagar este card?')) return;
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
          <div style={{ fontSize: 56, marginBottom: 16 }}>🎴</div>
          <h2 style={{ color: 'var(--text-highlight)', fontSize: 22, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 12 }}>Demo Concluída</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: 14, lineHeight: 1.7, marginBottom: 28 }}>
            Treinaste com cenários de Teoria dos Jogos. Com a tua conta podes gerar cards ilimitados para qualquer domínio da tua vida.
          </p>
          <Link to="/register" style={{ display: 'block', width: '100%', padding: '14px 0', borderRadius: 10, boxSizing: 'border-box', background: 'var(--accent)', color: '#fff', textAlign: 'center', fontWeight: 800, fontSize: 13, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 12, textDecoration: 'none' }}>
            Activar o Oráculo Completo →
          </Link>
          <button onClick={() => navigate('/')} style={{ display: 'block', width: '100%', background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 12, cursor: 'pointer', letterSpacing: 1, textTransform: 'uppercase' }}>
            Voltar à página inicial
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: 'calc(100vh - 56px)', padding: '2rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div style={{ maxWidth: 520, width: '100%' }}>
        {/* Header */}
        <div style={{ marginBottom: '1.25rem' }}>
          <button onClick={() => navigate('/')} style={{ background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', fontSize: 13, padding: 0, marginBottom: 6 }}>
            ← Domínios
          </button>
          {domain && (
            <h1 style={{ color: 'var(--text-highlight)', fontSize: 20, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase', margin: 0 }}>
              {domain.name}
            </h1>
          )}
        </div>

        {/* Tabs — only for authenticated users */}
        {isAuthenticated && (
          <div style={{ display: 'flex', gap: 0, marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)' }}>
            {[
              { key: 'generate', label: '⊕ Gerar' },
              { key: 'deck', label: `🃏 Meu Deck (${savedCards.length})` },
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                style={{
                  padding: '8px 16px', background: 'none', border: 'none', cursor: 'pointer',
                  color: activeTab === key ? 'var(--text-highlight)' : 'var(--text-muted)',
                  borderBottom: activeTab === key ? '2px solid var(--accent)' : '2px solid transparent',
                  fontSize: 13, fontWeight: 600, letterSpacing: 1,
                }}
              >
                {label}
              </button>
            ))}
          </div>
        )}

        {/* ======================== GENERATE TAB ======================== */}
        {activeTab === 'generate' && (
          <>
            <p style={{ color: 'var(--text-muted)', fontSize: 12, marginBottom: '1rem' }}>
              Desliza para a direita para salvar · Para a esquerda para descartar
            </p>

            {/* Context input */}
            <div style={{ marginBottom: '1rem' }}>
              <input
                value={context}
                onChange={(e) => setContext(e.target.value)}
                placeholder="Sub-tema ou contexto (opcional)..."
                style={{ width: '100%', background: 'var(--bg-card)', border: '1px solid var(--border-color)', color: 'var(--text-main)', borderRadius: 8, padding: '9px 12px', fontSize: 13, outline: 'none', boxSizing: 'border-box' }}
              />
            </div>

            {/* Generate button */}
            <button
              onClick={generateCard}
              disabled={generating}
              style={{ width: '100%', padding: '12px 0', borderRadius: 10, border: 'none', background: generating ? 'var(--bg-card-inner)' : 'var(--accent)', color: '#fff', fontSize: 14, fontWeight: 700, letterSpacing: 2, cursor: generating ? 'default' : 'pointer', textTransform: 'uppercase', marginBottom: '1rem', transition: 'background 0.2s' }}
            >
              {generating ? (progress ? `${progress.message} (${progress.percent}%)` : 'Gerando...') : 'Gerar Próximo Cenário'}
            </button>

            {/* AI image toggle — only for authenticated */}
            {isAuthenticated && !card && (
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', marginBottom: '1rem', color: 'var(--text-muted)', fontSize: 12 }}>
                <input
                  type="checkbox"
                  checked={generateImage}
                  onChange={e => setGenerateImage(e.target.checked)}
                  style={{ accentColor: 'var(--accent)', width: 14, height: 14 }}
                />
                Gerar imagem com IA ao salvar
              </label>
            )}

            {error && (
              <div style={{ background: '#7f1d1d', border: '1px solid #ef4444', borderRadius: 8, padding: '10px 14px', marginBottom: 16, color: '#fca5a5', fontSize: 13 }}>
                {error}
              </div>
            )}

            {/* Pending image action badge */}
            {pendingImageAction && (
              <div style={{ marginBottom: 8, padding: '6px 10px', borderRadius: 6, background: '#7c3aed22', border: '1px solid #7c3aed44', color: '#a78bfa', fontSize: 11 }}>
                Ação de imagem pendente: {pendingImageAction.type === 'generate' ? 'Gerar com IA' : pendingImageAction.type === 'improve' ? `Melhorar (${pendingImageAction.stylePrompt})` : pendingImageAction.type === 'upload' ? 'Upload de ficheiro' : pendingImageAction.type}
                <button onClick={() => setPendingImageAction(null)} style={{ background: 'none', border: 'none', color: '#a78bfa', cursor: 'pointer', marginLeft: 8, fontSize: 12 }}>✕</button>
              </div>
            )}

            {/* Card */}
            {card && (
              <>
                {/* Edit button above card */}
                {isAuthenticated && (
                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 8 }}>
                    <button
                      onClick={() => handleEditCard(card, null)}
                      style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--border-color)', color: 'var(--text-muted)', borderRadius: 6, padding: '5px 12px', fontSize: 11, cursor: 'pointer', letterSpacing: 1 }}
                    >
                      ✏ Editar Card
                    </button>
                  </div>
                )}
                <GameTheoryCard
                  card={card}
                  revealed={revealed}
                  onReveal={() => setRevealed(r => !r)}
                  onSave={() => handleSwipe('save')}
                  onDiscard={() => handleSwipe('discard')}
                  swiping={swiping}
                />
              </>
            )}

            {!card && !generating && !error && (
              <div style={{ textAlign: 'center', marginTop: 40, color: 'var(--text-muted)' }}>
                <p style={{ fontSize: 40, marginBottom: 12 }}>🎴</p>
                <p style={{ fontSize: 14 }}>Clica em "Gerar Próximo Cenário" para o Oráculo criar o teu primeiro card.</p>
              </div>
            )}
          </>
        )}

        {/* ======================== DECK TAB ======================== */}
        {activeTab === 'deck' && (
          <div>
            {loadingCards ? (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: 40 }}>A carregar cards...</p>
            ) : savedCards.length === 0 ? (
              <div style={{ textAlign: 'center', marginTop: 60 }}>
                <p style={{ fontSize: 36, marginBottom: 12 }}>📭</p>
                <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>Ainda não tens cards guardados neste domínio.</p>
                <button
                  onClick={() => setActiveTab('generate')}
                  style={{ marginTop: 16, padding: '10px 24px', borderRadius: 8, background: 'var(--accent)', border: 'none', color: '#fff', fontSize: 13, fontWeight: 700, cursor: 'pointer', letterSpacing: 1 }}
                >
                  Gerar o Primeiro Card
                </button>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {savedCards.map((c, idx) => {
                  const color = TEMPLATE_COLORS[c.template_type] || '#7c3aed';
                  const imgUrl = c.media_urls && c.media_urls[0] ? `${API_URL}${c.media_urls[0]}` : null;
                  return (
                    <div
                      key={c.id ?? c._id ?? idx}
                      style={{ background: 'var(--bg-card)', border: `1px solid ${color}33`, borderRadius: 10, padding: '12px 14px', display: 'flex', gap: 12, alignItems: 'flex-start' }}
                    >
                      {/* Thumbnail */}
                      <div style={{ width: 52, height: 52, borderRadius: 8, overflow: 'hidden', flexShrink: 0, background: color + '22', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {imgUrl
                          ? <img src={imgUrl} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                          : <span style={{ fontSize: 22 }}>{c.template_type === 'black_swan' ? '✦' : c.template_type === 'payoff_matrix' ? '◈' : '⚖'}</span>
                        }
                      </div>
                      {/* Content */}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                          <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase', color, border: `1px solid ${color}`, borderRadius: 3, padding: '1px 5px' }}>
                            {c.template_type === 'if_then' ? 'SE/ENTÃO' : c.template_type === 'payoff_matrix' ? 'RECOMPENSA' : 'CISNE NEGRO'}
                          </span>
                          <span style={{ fontSize: 10, fontWeight: 700, color: heatColor(c.probability_heat_score) }}>
                            HEAT {c.probability_heat_score}
                          </span>
                        </div>
                        <p style={{ color: 'var(--text-main)', fontSize: 12, margin: 0, lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                          {c.scenario_context}
                        </p>
                      </div>
                      {/* Actions */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 4, flexShrink: 0 }}>
                        <button
                          onClick={() => handleEditCard(c, c.id)}
                          title="Editar"
                          style={{ padding: '5px 10px', borderRadius: 6, background: 'var(--bg-card-inner)', border: '1px solid var(--border-color)', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 12 }}
                        >
                          ✏
                        </button>
                        <button
                          onClick={() => handleDeleteCard(c.id)}
                          title="Apagar"
                          style={{ padding: '5px 10px', borderRadius: 6, background: 'transparent', border: '1px solid #ef444433', color: '#ef4444', cursor: 'pointer', fontSize: 12 }}
                        >
                          🗑
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* CTA Modal */}
        {showCTAModal && (
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200, padding: '1rem', backdropFilter: 'blur(4px)' }} onClick={handleModalDismiss}>
            <div style={{ background: 'var(--bg-card)', border: '1px solid var(--accent)', borderRadius: 16, padding: '2rem', maxWidth: 380, width: '100%' }} onClick={(e) => e.stopPropagation()}>
              <div style={{ fontSize: 40, textAlign: 'center', marginBottom: 12 }}>⚡</div>
              <h2 style={{ color: 'var(--text-highlight)', fontSize: 20, fontWeight: 800, textAlign: 'center', letterSpacing: 2, textTransform: 'uppercase', marginBottom: 8 }}>Gostou da análise?</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: 13, textAlign: 'center', lineHeight: 1.7, marginBottom: 24 }}>
                Cria a tua conta gratuita para salvar este card no teu deck, treinar com repetição espaçada e gerar cenários personalizados para qualquer domínio.
              </p>
              <Link to="/register" style={{ display: 'block', padding: '13px 0', borderRadius: 10, background: 'var(--accent)', color: '#fff', textAlign: 'center', fontWeight: 800, fontSize: 13, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 10, textDecoration: 'none' }}>
                Criar Conta Grátis
              </Link>
              <button onClick={handleModalDismiss} style={{ width: '100%', padding: '11px 0', borderRadius: 10, border: '1px solid var(--border-color)', background: 'transparent', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 12, letterSpacing: 1, textTransform: 'uppercase' }}>
                {demoIndex < DEMO_CARDS.length ? 'Explorar Próximo Card' : 'Ver Conclusão da Demo'}
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
