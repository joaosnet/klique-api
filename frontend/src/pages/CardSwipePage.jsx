import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { domainsAPI, cardsAPI } from '../services/api';
import GameTheoryCard from '../components/Cards/GameTheoryCard';
import { useAuth } from '../context/AuthContext';
import { DEMO_CARDS, DEMO_DOMAINS } from '../utils/demoData';
import { Link } from 'react-router-dom';

export default function CardSwipePage() {
  const { domainId } = useParams();
  const navigate = useNavigate();

  const [domain, setDomain] = useState(null);
  const [card, setCard] = useState(null);
  const [revealed, setRevealed] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState('');
  const [swiping, setSwiping] = useState(null); // 'left' | 'right'
  const [context, setContext] = useState('');

  const { isAuthenticated } = useAuth();
  const [demoIndex, setDemoIndex] = useState(0);
  const [showCTAModal, setShowCTAModal] = useState(false);
  const [demoComplete, setDemoComplete] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      const demoDomain = DEMO_DOMAINS.find(d => d.domain.id === domainId);
      if (demoDomain) {
        setDomain(demoDomain.domain);
      } else {
        setDomain(DEMO_DOMAINS[0].domain); // fallback
      }
      return;
    }

    domainsAPI.getOne(domainId)
      .then((data) => setDomain(data.domain))
      .catch(() => navigate('/dominios'));
  }, [domainId, isAuthenticated]);

  const generateCard = async () => {
    setGenerating(true);
    setCard(null);
    setRevealed(false);
    setError('');
    setProgress(null);

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

      const result = await cardsAPI.generateStream(
        domainId,
        context || null,
        (p) => setProgress(p),
      );
      if (result?.card) {
        setCard(result.card);
      } else {
        setError('Resposta inesperada da IA. Tente novamente.');
      }
    } catch (e) {
      setError(e.message || 'Erro ao gerar cenário.');
    } finally {
      if (isAuthenticated) {
        setGenerating(false);
        setProgress(null);
      }
    }
  };

  const handleSwipe = async (action) => {
    if (!card) return;
    setSwiping(action === 'save' ? 'right' : 'left');

    if (!isAuthenticated) {
      setTimeout(() => {
        setShowCTAModal(true);
      }, 350);
      return;
    }

    try {
      await cardsAPI.swipe(card, domainId, action);
    } catch (e) {
      console.error(e);
    }
    setTimeout(() => {
      setSwiping(null);
      setCard(null);
      setRevealed(false);
    }, 350);
  };

  const handleModalDismiss = () => {
    setShowCTAModal(false);
    setSwiping(null);
    setCard(null);
    setRevealed(false);
    if (demoIndex >= DEMO_CARDS.length) {
      setDemoComplete(true);
    }
  };

  if (demoComplete) {
    return (
      <div style={{ minHeight: 'calc(100vh - 56px)', background: '#12121a', padding: '2rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ maxWidth: 400, width: '100%', textAlign: 'center', background: 'var(--bg-card)', padding: '2rem', borderRadius: 16, border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: 56, marginBottom: 16 }}>🎴</div>
          <h2 style={{ color: 'var(--text-highlight)', fontSize: 22, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 12 }}>
            Demo Concluída
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: 14, lineHeight: 1.7, marginBottom: 28 }}>
            Treinaste com cenários de Teoria dos Jogos. Com a tua conta podes gerar cards ilimitados para qualquer domínio da tua vida.
          </p>
          <Link
            to="/register"
            style={{
              display: 'block', width: '100%', padding: '14px 0', borderRadius: 10, boxSizing: 'border-box',
              background: 'var(--accent)', color: '#fff',
              textAlign: 'center', fontWeight: 800, fontSize: 13, letterSpacing: 2,
              textTransform: 'uppercase', marginBottom: 12, textDecoration: 'none',
            }}
          >
            Activar o Oráculo Completo →
          </Link>
          <button
            onClick={() => navigate('/')}
            style={{
              display: 'block', width: '100%', background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 12, cursor: 'pointer',
              letterSpacing: 1, textTransform: 'uppercase',
            }}
          >
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
        <div style={{ marginBottom: '1.5rem' }}>
          <button
            onClick={() => navigate('/dominios')}
            style={{ background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', fontSize: 13, padding: 0, marginBottom: 8 }}
          >
            ← Domínios
          </button>
          {domain && (
            <h1 style={{ color: 'var(--text-highlight)', fontSize: 20, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase', margin: 0 }}>
              {domain.name}
            </h1>
          )}
          <p style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>
            Desliza para a direita para salvar · Para a esquerda para descartar
          </p>
        </div>

        {/* Context input */}
        <div style={{ marginBottom: '1.25rem' }}>
          <input
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Sub-tema ou contexto (opcional)..."
            style={{
              width: '100%', background: 'var(--bg-card)', border: '1px solid var(--border-color)',
              color: 'var(--text-main)', borderRadius: 8, padding: '9px 12px', fontSize: 13,
              outline: 'none', boxSizing: 'border-box',
            }}
          />
        </div>

        {/* Generate button */}
        <button
          onClick={generateCard}
          disabled={generating}
          style={{
            width: '100%', padding: '12px 0', borderRadius: 10, border: 'none',
            background: generating ? 'var(--bg-card-inner)' : 'var(--accent)', color: '#fff',
            fontSize: 14, fontWeight: 700, letterSpacing: 2, cursor: generating ? 'default' : 'pointer',
            textTransform: 'uppercase', marginBottom: '1.5rem', transition: 'background 0.2s',
          }}
        >
          {generating ? (progress ? `${progress.message} (${progress.percent}%)` : 'Gerando...') : 'Gerar Próximo Cenário'}
        </button>

        {error && (
          <div style={{ background: '#7f1d1d', border: '1px solid #ef4444', borderRadius: 8, padding: '10px 14px', marginBottom: 16, color: '#fca5a5', fontSize: 13 }}>
            {error}
          </div>
        )}

        {/* Card */}
        {card && (
          <GameTheoryCard
            card={card}
            revealed={revealed}
            onReveal={() => setRevealed(r => !r)}
            onSave={() => handleSwipe('save')}
            onDiscard={() => handleSwipe('discard')}
            swiping={swiping}
          />
        )}

        {!card && !generating && !error && (
          <div style={{ textAlign: 'center', marginTop: 40, color: 'var(--text-muted)' }}>
            <p style={{ fontSize: 40, marginBottom: 12 }}>🎴</p>
            <p style={{ fontSize: 14 }}>Clica em "Gerar Próximo Cenário" para o Oráculo criar o teu primeiro card.</p>
          </div>
        )}
        {/* CTA Modal */}
        {showCTAModal && (
          <div
            style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200, padding: '1rem', backdropFilter: 'blur(4px)' }}
            onClick={handleModalDismiss}
          >
            <div
              style={{ background: 'var(--bg-card)', border: '1px solid var(--accent)', borderRadius: 16, padding: '2rem', maxWidth: 380, width: '100%' }}
              onClick={(e) => e.stopPropagation()}
            >
              <div style={{ fontSize: 40, textAlign: 'center', marginBottom: 12 }}>⚡</div>
              <h2 style={{ color: 'var(--text-highlight)', fontSize: 20, fontWeight: 800, textAlign: 'center', letterSpacing: 2, textTransform: 'uppercase', marginBottom: 8 }}>
                Gostou da análise?
              </h2>
              <p style={{ color: 'var(--text-muted)', fontSize: 13, textAlign: 'center', lineHeight: 1.7, marginBottom: 24 }}>
                Cria a tua conta gratuita para salvar este card no teu deck, treinar com repetição espaçada e gerar cenários personalizados para qualquer domínio.
              </p>
              <Link
                to="/register"
                style={{
                  display: 'block', padding: '13px 0', borderRadius: 10,
                  background: 'var(--accent)', color: '#fff',
                  textAlign: 'center', fontWeight: 800, fontSize: 13, letterSpacing: 2,
                  textTransform: 'uppercase', marginBottom: 10, textDecoration: 'none',
                }}
              >
                Criar Conta Grátis
              </Link>
              <button
                onClick={handleModalDismiss}
                style={{
                  width: '100%', padding: '11px 0', borderRadius: 10, border: '1px solid var(--border-color)',
                  background: 'transparent', color: 'var(--text-muted)', cursor: 'pointer',
                  fontSize: 12, letterSpacing: 1, textTransform: 'uppercase',
                }}
              >
                {demoIndex < DEMO_CARDS.length ? 'Explorar Próximo Card' : 'Ver Conclusão da Demo'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
