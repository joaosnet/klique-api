import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import DomainSVGCard from '../components/Cards/DomainSVGCard';
import GamifiedLoader from '../components/Layout/GamifiedLoader';
import { domainsAPI } from '../services/api';
import './ToggleTheme.css';
import './VisualPage.css';

// COLORS agora é uma função que retorna os nomes traduzidos
function getColors(t) {
  return [
    { name: t('colors.purple_default'), value: '#7c3aed', light: '#a855f7', dark: '#6b21a8' },
    { name: t('colors.blue'), value: '#2563eb', light: '#3b82f6', dark: '#1d4ed8' },
    { name: t('colors.green'), value: '#16a34a', light: '#22c55e', dark: '#15803d' },
    { name: t('colors.orange'), value: '#ea580c', light: '#f97316', dark: '#c2410c' },
    { name: t('colors.pink'), value: '#db2777', light: '#ec4899', dark: '#be185d' },
  ];
}

export default function VisualPage() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [theme, setTheme] = useState(localStorage.getItem('app_theme') || 'auto');
  const [accent, setAccent] = useState(localStorage.getItem('app_accent') || '#7c3aed');

  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadDomains = async (silent = false) => {
    if (!silent) setLoading(true);
    setError('');
    try {
      const data = await domainsAPI.list();
      setDomains(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(e?.message || t('visual.error_load_decks'));
    } finally {
      if (!silent) setLoading(false);
    }
  };

  useEffect(() => {
    loadDomains();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (domains.length === 0) return;

    const hasPendingImages = domains.some(({ domain }) => !domain.image_url);
    if (!hasPendingImages) return;

    const intervalId = window.setInterval(() => {
      loadDomains(true);
    }, 5000);

    return () => window.clearInterval(intervalId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [domains]);

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
    localStorage.setItem('app_theme', newTheme);

    const resolved = newTheme === 'auto'
      ? (window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      : newTheme;

    document.documentElement.setAttribute('data-theme', resolved);
  };

  const handleAccentChange = (colorObj) => {
    setAccent(colorObj.value);
    localStorage.setItem('app_accent', colorObj.value);
    document.documentElement.style.setProperty('--accent', colorObj.value);
    document.documentElement.style.setProperty('--accent-light', colorObj.light);
    document.documentElement.style.setProperty('--accent-dark', colorObj.dark);
  };

  const THEMES = ['light', 'auto', 'dark'];
  const currentThemeKey = THEMES.includes(theme) ? theme : 'auto';
  const themeIndex = THEMES.indexOf(currentThemeKey);

  const getThemeLabel = (themeValue) => {
    if (themeValue === 'light') return t('visual.theme_light');
    if (themeValue === 'auto') return t('visual.theme_auto');
    return t('visual.theme_dark');
  };

  const cycleTheme = () => {
    const nextIndex = (themeIndex + 1) % 3;
    handleThemeChange(THEMES[nextIndex]);
  };

  const COLORS = getColors(t);

  const stats = useMemo(() => {
    const totalDecks = domains.length;
    const totalCards = domains.reduce((sum, item) => sum + (item?.stats?.cards_count || 0), 0);
    const dueToday = domains.reduce((sum, item) => sum + (item?.stats?.due_today || 0), 0);
    return { totalDecks, totalCards, dueToday };
  }, [domains]);

  return (
    <div className="visual-page">
      <div className="visual-page__bg" aria-hidden="true" />

      <div className="visual-page__content">
        <header className="visual-page__header">
          <h1>{t('visual.title')}</h1>
          <p>{t('visual.subtitle')}</p>
        </header>

        <section className="visual-grid" aria-label={t('visual.aria_label')}>
          <article className="visual-panel visual-panel--settings">
            <h2>{t('visual.appearance')}</h2>

            <div className="visual-field">
              <label>{t('visual.mode')}</label>
              <div className="day-night-toggle" title={t('visual.mode')}>
                <span className="visual-mode-label">{getThemeLabel(currentThemeKey)}</span>
                <div className={`toggle-track theme-${currentThemeKey}`} onClick={cycleTheme}>
                  <div className="toggle-bg-color" />
                  <div className="cloud cloud-1" />
                  <div className="cloud cloud-2" />
                  <div className="star star-1" />
                  <div className="star star-2" />
                  <div className="star star-3" />
                  <div className="toggle-knob">
                    <span className="knob-content" style={{ color: '#1a1a2e' }}>A</span>
                    <div className="moon-craters">
                      <div className="crater crater-1" />
                      <div className="crater crater-2" />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="visual-field">
              <label>{t('visual.accent_color')}</label>
              <div className="visual-accent-grid">
                {COLORS.map((c) => (
                  <button
                    key={c.value}
                    onClick={() => handleAccentChange(c)}
                    title={c.name}
                    className={`visual-accent ${accent === c.value ? 'is-active' : ''}`}
                    style={{ background: c.value }}
                  />
                ))}
              </div>
            </div>

            <div className="visual-field">
              <label>{t('visual.language')}</label>
              <div className="visual-accent-grid">
                <button
                  onClick={() => i18n.changeLanguage('en')}
                  title="English"
                  className={`visual-accent ${i18n.language?.startsWith('en') ? 'is-active' : ''}`}
                  style={{ background: '#2563eb', color: '#fff', fontSize: 12, fontWeight: 700 }}
                >
                  EN
                </button>
                <button
                  onClick={() => i18n.changeLanguage('pt')}
                  title="Português"
                  className={`visual-accent ${i18n.language?.startsWith('pt') ? 'is-active' : ''}`}
                  style={{ background: '#16a34a', color: '#fff', fontSize: 12, fontWeight: 700 }}
                >
                  PT
                </button>
              </div>
            </div>
          </article>

          <article className="visual-panel visual-panel--decks">
            <h2>{t('visual.decks_cards')}</h2>

            <div className="visual-stats">
              <div>
                <strong>{stats.totalDecks}</strong>
                <span>{t('visual.decks')}</span>
              </div>
              <div>
                <strong>{stats.totalCards}</strong>
                <span>{t('visual.cards')}</span>
              </div>
              <div>
                <strong>{stats.dueToday}</strong>
                <span>{t('common.today')}</span>
              </div>
            </div>

            {loading ? (
              <GamifiedLoader label={t('visual.loading_decks')} />
            ) : error ? (
              <p className="visual-feedback visual-feedback--error">{error}</p>
            ) : domains.length === 0 ? (
              <p className="visual-feedback">{t('visual.empty_decks')}</p>
            ) : (
              <div className="visual-domain-grid">
                {domains.slice(0, 4).map(({ domain, stats: domainStats }) => (
                  <DomainSVGCard
                    key={domain.id}
                    domain={domain}
                    stats={domainStats}
                    onClick={() => navigate(`/criar/${domain.id}`)}
                  />
                ))}
              </div>
            )}
          </article>
        </section>
      </div>
    </div>
  );
}
