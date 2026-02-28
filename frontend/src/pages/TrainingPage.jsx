import { useState, useEffect } from 'react';
import { srsAPI } from '../services/api';
import GamifiedLoader from '../components/Layout/GamifiedLoader';
import GameTheoryCard from '../components/Cards/GameTheoryCard';
import DeckPileDisplay from '../components/Cards/DeckPileDisplay';

const RATING_LABELS = [
  { rating: 0, label: 'Sem ideia', color: '#ef4444' },
  { rating: 1, label: 'Quase nada', color: '#f97316' },
  { rating: 2, label: 'Errei feio', color: '#f59e0b' },
  { rating: 3, label: 'Com dificuldade', color: '#eab308' },
  { rating: 4, label: 'Quase perfeito', color: '#84cc16' },
  { rating: 5, label: 'Acertei em cheio', color: '#22c55e' },
];

export default function TrainingPage() {
  const [dueCards, setDueCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [stats, setStats] = useState(null);
  const [done, setDone] = useState(false);
  const [started, setStarted] = useState(false);

  useEffect(() => {
    loadDue();
  }, []);

  const loadDue = async () => {
    setLoading(true);
    try {
      const [due, srsStats] = await Promise.all([srsAPI.getDue(), srsAPI.getStats()]);
      setDueCards(due);
      setStats(srsStats);
      if (due.length === 0) setDone(true);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleRate = async (rating) => {
    const current = dueCards[currentIndex];
    if (!current || submitting) return;
    setSubmitting(true);
    try {
      await srsAPI.submitReview(current.card.id, rating);
      const nextIndex = currentIndex + 1;
      if (nextIndex >= dueCards.length) {
        setDone(true);
      } else {
        setCurrentIndex(nextIndex);
        setRevealed(false);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSubmitting(false);
    }
  };

  const current = dueCards[currentIndex];
  const progress = dueCards.length > 0 ? (currentIndex / dueCards.length) * 100 : 0;

  if (loading) {
    <GamifiedLoader label="A carregar fila de treino..." />
  }

  if (done) {
    return (
      <div style={{ minHeight: 'calc(100vh - 56px)', background: '#12121a', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 16, padding: '2rem' }}>
        <div style={{ fontSize: 56, textAlign: 'center' }}>⚡</div>
        <h2 style={{ color: '#e9d5ff', fontSize: 22, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase', margin: 0 }}>
          Treino Concluído
        </h2>
        <p style={{ color: '#6b7280', fontSize: 14, textAlign: 'center', maxWidth: 320 }}>
          Todos os {dueCards.length || 0} cenários de hoje foram revistos. O Oráculo actualiza o teu calendário.
        </p>
        {stats && (
          <div style={{ display: 'flex', gap: 24, marginTop: 16 }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: '#7c3aed', fontSize: 28, fontWeight: 800 }}>{stats.total_trained}</div>
              <div style={{ color: '#6b7280', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase' }}>Total Treinado</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: '#f59e0b', fontSize: 28, fontWeight: 800 }}>{stats.streak_days}</div>
              <div style={{ color: '#6b7280', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase' }}>Dias Streak</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: '#22c55e', fontSize: 28, fontWeight: 800 }}>{stats.cards_mastered}</div>
              <div style={{ color: '#6b7280', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase' }}>Dominados</div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div style={{ minHeight: 'calc(100vh - 56px)', background: 'var(--bg-app)', padding: '2rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div style={{ maxWidth: 520, width: '100%' }}>
        {/* Header */}
        <div style={{ marginBottom: '1.25rem' }}>
          <h1 style={{ color: 'var(--text-highlight)', fontSize: 20, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase', margin: 0 }}>
            Simulação Diária
          </h1>
          {started && (
            <p style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>
              {currentIndex + 1} de {dueCards.length} cenários
            </p>
          )}
        </div>

        {!started ? (
          /* Deck pile intro screen */
          <DeckPileDisplay count={dueCards.length} onStart={() => setStarted(true)} />
        ) : (
          <>
            {/* Progress bar */}
            <div style={{ background: 'var(--border-color)', borderRadius: 4, height: 4, marginBottom: 24, overflow: 'hidden' }}>
              <div style={{ width: `${progress}%`, background: 'var(--accent)', height: '100%', borderRadius: 4, transition: 'width 0.4s ease' }} />
            </div>

            {current && (
              <>
                <GameTheoryCard
                  card={current.card}
                  revealed={revealed}
                  onReveal={() => setRevealed(r => !r)}
                />

                {/* SRS rating — shown after reveal */}
                {revealed && (
                  <div style={{ marginTop: 16 }}>
                    <p style={{ color: 'var(--text-muted)', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 10, textAlign: 'center' }}>
                      Como acertaste na tua previsão?
                    </p>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
                      {RATING_LABELS.map(({ rating, label, color }) => (
                        <button
                          key={rating}
                          onClick={() => handleRate(rating)}
                          disabled={submitting}
                          style={{
                            padding: '8px 4px', borderRadius: 6, border: `1px solid ${color}44`,
                            background: color + '11', color, cursor: submitting ? 'default' : 'pointer',
                            fontSize: 11, fontWeight: 600, lineHeight: 1.3,
                          }}
                        >
                          <div style={{ fontSize: 16, marginBottom: 2 }}>{rating}</div>
                          {label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
