import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { domainsAPI, cardsAPI } from '../services/api';
import GameTheoryCard from '../components/Cards/GameTheoryCard';

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

  useEffect(() => {
    domainsAPI.getOne(domainId)
      .then((data) => setDomain(data.domain))
      .catch(() => navigate('/dominios'));
  }, [domainId]);

  const generateCard = async () => {
    setGenerating(true);
    setCard(null);
    setRevealed(false);
    setError('');
    setProgress(null);

    try {
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
      setGenerating(false);
      setProgress(null);
    }
  };

  const handleSwipe = async (action) => {
    if (!card) return;
    setSwiping(action === 'save' ? 'right' : 'left');
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

  return (
    <div style={{ minHeight: 'calc(100vh - 56px)', background: '#12121a', padding: '2rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div style={{ maxWidth: 520, width: '100%' }}>
        {/* Header */}
        <div style={{ marginBottom: '1.5rem' }}>
          <button
            onClick={() => navigate('/dominios')}
            style={{ background: 'none', border: 'none', color: '#7c3aed', cursor: 'pointer', fontSize: 13, padding: 0, marginBottom: 8 }}
          >
            ← Domínios
          </button>
          {domain && (
            <h1 style={{ color: '#e9d5ff', fontSize: 20, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase', margin: 0 }}>
              {domain.name}
            </h1>
          )}
          <p style={{ color: '#6b7280', fontSize: 12, marginTop: 4 }}>
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
              width: '100%', background: '#0f172a', border: '1px solid #374151',
              color: '#e5e7eb', borderRadius: 8, padding: '9px 12px', fontSize: 13,
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
            background: generating ? '#374151' : '#7c3aed', color: '#fff',
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
            onReveal={() => setRevealed(true)}
            onSave={() => handleSwipe('save')}
            onDiscard={() => handleSwipe('discard')}
            swiping={swiping}
          />
        )}

        {!card && !generating && !error && (
          <div style={{ textAlign: 'center', marginTop: 40, color: '#4b5563' }}>
            <p style={{ fontSize: 40, marginBottom: 12 }}>🎴</p>
            <p style={{ fontSize: 14 }}>Clica em "Gerar Próximo Cenário" para o Oráculo criar o teu primeiro card.</p>
          </div>
        )}
      </div>
    </div>
  );
}
