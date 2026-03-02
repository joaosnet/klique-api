import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DomainSVGCard from '../components/Cards/DomainSVGCard';
import GamifiedLoader from '../components/Layout/GamifiedLoader';
import { domainsAPI } from '../services/api';
import './ToggleTheme.css';
import './VisualPage.css';

const COLORS = [
  { name: 'Roxo (Padrao)', value: '#7c3aed', light: '#a855f7', dark: '#6b21a8' },
  { name: 'Azul', value: '#2563eb', light: '#3b82f6', dark: '#1d4ed8' },
  { name: 'Verde', value: '#16a34a', light: '#22c55e', dark: '#15803d' },
  { name: 'Laranja', value: '#ea580c', light: '#f97316', dark: '#c2410c' },
  { name: 'Rosa', value: '#db2777', light: '#ec4899', dark: '#be185d' },
];

export default function VisualPage() {
  const navigate = useNavigate();
  const [theme, setTheme] = useState(localStorage.getItem('app_theme') || 'auto');
  const [accent, setAccent] = useState(localStorage.getItem('app_accent') || '#7c3aed');

  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadDomains = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await domainsAPI.list();
        setDomains(Array.isArray(data) ? data : []);
      } catch (e) {
        setError(e?.message || 'Nao foi possivel carregar os decks.');
      } finally {
        setLoading(false);
      }
    };

    loadDomains();
  }, []);

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

  const themeState = theme === 'light' ? 0 : theme === 'auto' ? 1 : 2;

  const getThemeName = (state) => {
    if (state === 0) return 'light';
    if (state === 1) return 'auto';
    return 'dark';
  };

  const cycleTheme = () => {
    const nextState = (themeState + 1) % 3;
    handleThemeChange(getThemeName(nextState));
  };

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
          <h1>Visual do App</h1>
          <p>Personaliza o tema e acompanha como os teus decks e cartas aparecem no aplicativo.</p>
        </header>

        <section className="visual-grid" aria-label="Configuracao visual e decks">
          <article className="visual-panel visual-panel--settings">
            <h2>Aparencia Geral</h2>

            <div className="visual-field">
              <label>Modo</label>
              <div className="day-night-toggle" title="Modo Visual">
                <span className="visual-mode-label">{getThemeName(themeState)}</span>
                <div className={`toggle-track theme-${getThemeName(themeState)}`} onClick={cycleTheme}>
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
              <label>Cor de Destaque</label>
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
          </article>

          <article className="visual-panel visual-panel--decks">
            <h2>Decks e Cartas</h2>

            <div className="visual-stats">
              <div>
                <strong>{stats.totalDecks}</strong>
                <span>Decks</span>
              </div>
              <div>
                <strong>{stats.totalCards}</strong>
                <span>Cartas</span>
              </div>
              <div>
                <strong>{stats.dueToday}</strong>
                <span>Hoje</span>
              </div>
            </div>

            {loading ? (
              <GamifiedLoader label="A carregar visual dos decks..." />
            ) : error ? (
              <p className="visual-feedback visual-feedback--error">{error}</p>
            ) : domains.length === 0 ? (
              <p className="visual-feedback">Cria o teu primeiro dominio para ver as cartas e o estilo dos decks aqui.</p>
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
