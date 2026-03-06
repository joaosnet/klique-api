import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { srsAPI } from '../services/api';
import GamifiedLoader from '../components/Layout/GamifiedLoader';
import GameTheoryCard from '../components/Cards/GameTheoryCard';
import DeckPileDisplay from '../components/Cards/DeckPileDisplay';
import { IconSparkBoost } from '../components/Icons/ActionIcons';

const RATING_LABELS = [
  { rating: 0, label: 'training.rating_0', color: '#ef4444' },
  { rating: 1, label: 'training.rating_1', color: '#f97316' },
  { rating: 2, label: 'training.rating_2', color: '#f59e0b' },
  { rating: 3, label: 'training.rating_3', color: '#eab308' },
  { rating: 4, label: 'training.rating_4', color: '#84cc16' },
  { rating: 5, label: 'training.rating_5', color: '#22c55e' },
];

export default function TrainingPage() {
  const { t } = useTranslation();
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
    return <GamifiedLoader label={t('training.loading')} />;
  }

  if (done) {
    return (
      <div style={{ minHeight: 'calc(100vh - 56px)', background: 'var(--bg-app)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 16, padding: '2rem' }}>
        <div style={{ textAlign: 'center' }}><IconSparkBoost width={56} height={56} /></div>
        <h2 style={{ color: 'var(--text-highlight)', fontSize: 22, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase', margin: 0 }}>
          {t('training.finish')}
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: 14, textAlign: 'center', maxWidth: 320 }}>
          {t('training.results', { count: dueCards.length || 0 })}
        </p>
        {stats && (
          <div style={{ display: 'flex', gap: 24, marginTop: 16 }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: 'var(--accent)', fontSize: 28, fontWeight: 800 }}>{stats.total_trained}</div>
              <div style={{ color: 'var(--text-muted)', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase' }}>{t('training.cards_reviewed')}</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: '#f59e0b', fontSize: 28, fontWeight: 800 }}>{stats.streak_days}</div>
              <div style={{ color: 'var(--text-muted)', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase' }}>{t('training.streak')}</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: '#22c55e', fontSize: 28, fontWeight: 800 }}>{stats.cards_mastered}</div>
              <div style={{ color: 'var(--text-muted)', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase' }}>{t('training.mastered')}</div>
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
            {t('training.title')}
          </h1>
          {started && (
            <p style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>
              {t('training.progress', { current: currentIndex + 1, total: dueCards.length })}
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
                      {t('training.rating_prompt')}
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
                          {t(label)}
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
