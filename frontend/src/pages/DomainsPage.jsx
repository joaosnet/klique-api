import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { domainsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { DEMO_DOMAINS } from '../utils/demoData';
import DomainSVGCard from '../components/Cards/DomainSVGCard';
import DomainEditModal from '../components/Domains/DomainEditModal';
import { getErrorMessage } from '../utils/errorHandler';
import GamifiedLoader from '../components/Layout/GamifiedLoader';

const THEMES = [
  { value: 'dating', label: 'Dinâmicas de Encontros' },
  { value: 'office', label: 'Política do Escritório' },
  { value: 'finance', label: 'Mercado Financeiro' },
  { value: 'negotiation', label: 'Negociação' },
  { value: 'geopolitics', label: 'Geopolítica' },
  { value: 'social', label: 'Dinâmicas Sociais' },
  { value: 'custom', label: 'Outro (personalizado)' },
];

function HeatBadge({ score }) {
  const color = score >= 67 ? '#ef4444' : score >= 34 ? '#f59e0b' : '#22c55e';
  return (
    <span style={{ background: color + '22', color, border: `1px solid ${color}55`, borderRadius: 4, padding: '1px 6px', fontSize: 11, fontWeight: 700, letterSpacing: 1 }}>
      HEAT {score}
    </span>
  );
}

function NewDomainModal({ onClose, onCreate }) {
  const [name, setName] = useState('');
  const [theme, setTheme] = useState('dating');
  const [customTheme, setCustomTheme] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    const finalTheme = theme === 'custom' ? customTheme.trim() || 'personalizado' : theme;
    setLoading(true);
    setError('');
    try {
      await onCreate(name.trim(), finalTheme);
      onClose();
    } catch (err) {
      setError(getErrorMessage(err, 'Erro ao criar domínio'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}
      onClick={onClose}
    >
      <div
        style={{ background: 'var(--bg-card)', border: '1px solid var(--accent-dark)', borderRadius: 12, padding: '2rem', width: '100%', maxWidth: 420 }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{ color: 'var(--text-highlight)', fontSize: 18, fontWeight: 700, marginBottom: 20, letterSpacing: 2, textTransform: 'uppercase' }}>
          Novo Domínio
        </h2>
        <form onSubmit={handleSubmit}>
          <label style={{ color: 'var(--text-muted)', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase', display: 'block', marginBottom: 4 }}>Nome do Domínio</label>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Ex: Dinâmicas de Escritório Q4" required
            style={{ width: '100%', background: 'var(--bg-card-inner)', border: '1px solid var(--border-color)', color: 'var(--text-main)', borderRadius: 6, padding: '8px 12px', fontSize: 14, outline: 'none', marginBottom: 16, boxSizing: 'border-box' }}
          />
          <label style={{ color: 'var(--text-muted)', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase', display: 'block', marginBottom: 4 }}>Tema</label>
          <select value={theme} onChange={(e) => setTheme(e.target.value)}
            style={{ width: '100%', background: 'var(--bg-card-inner)', border: '1px solid var(--border-color)', color: 'var(--text-main)', borderRadius: 6, padding: '8px 12px', fontSize: 14, outline: 'none', marginBottom: theme === 'custom' ? 8 : 24, boxSizing: 'border-box' }}
          >
            {THEMES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
          {theme === 'custom' && (
            <input value={customTheme} onChange={(e) => setCustomTheme(e.target.value)} placeholder="Descreva o tema..."
              style={{ width: '100%', background: 'var(--bg-card-inner)', border: '1px solid var(--border-color)', color: 'var(--text-main)', borderRadius: 6, padding: '8px 12px', fontSize: 14, outline: 'none', marginBottom: 24, boxSizing: 'border-box' }}
            />
          )}
          {error && <p style={{ color: '#ef4444', fontSize: 13, marginBottom: 12 }}>{error}</p>}
          <div style={{ display: 'flex', gap: 8 }}>
            <button type="button" onClick={onClose}
              style={{ flex: 1, padding: '9px 0', borderRadius: 6, border: '1px solid var(--border-color)', color: 'var(--text-muted)', background: 'transparent', cursor: 'pointer', fontSize: 13 }}
            >
              Cancelar
            </button>
            <button type="submit" disabled={loading}
              style={{ flex: 2, padding: '9px 0', borderRadius: 6, border: 'none', background: 'var(--accent)', color: '#fff', cursor: 'pointer', fontSize: 13, fontWeight: 700, letterSpacing: 1, opacity: loading ? 0.6 : 1 }}
            >
              {loading ? 'Criando...' : 'Criar Domínio'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function DomainsPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingDomain, setEditingDomain] = useState(null);

  const loadDomains = async () => {
    setLoading(true);
    try {
      if (!isAuthenticated) {
        setDomains(DEMO_DOMAINS);
      } else {
        const data = await domainsAPI.list();
        setDomains(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadDomains(); }, [isAuthenticated]);

  const handleCreate = async (name, theme) => {
    await domainsAPI.create(name, theme);
    await loadDomains();
  };

  const handleDelete = async (domainId) => {
    if (!window.confirm('Tens a certeza? Esta ação irá apagar o domínio e todos os seus cards.')) return;
    try {
      await domainsAPI.remove(domainId);
      await loadDomains();
    } catch (e) {
      console.error(e);
    }
  };

  const handleEditSave = async () => {
    setEditingDomain(null);
    await loadDomains();
  };

  return (
    <div style={{ minHeight: 'calc(100vh - 56px)', padding: '2rem 1rem' }}>
      <div style={{ maxWidth: 900, margin: '0 auto' }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
          <div>
            <h1 style={{ color: 'var(--text-highlight)', fontSize: 24, fontWeight: 800, letterSpacing: 3, textTransform: 'uppercase', margin: 0 }}>
              Domínios de Jogo
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 4 }}>
              Cada domínio é um campo de batalha. Escolhe o teu e treina os reflexos.
            </p>
          </div>
          {isAuthenticated ? (
            <button
              onClick={() => setShowModal(true)}
              style={{ background: 'var(--accent)', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 20px', fontSize: 13, fontWeight: 700, letterSpacing: 1, cursor: 'pointer', textTransform: 'uppercase' }}
            >
              + Novo Domínio
            </button>
          ) : (
            <div style={{ background: 'var(--bg-card-inner)', border: '1px solid var(--accent)', borderRadius: 8, padding: '8px 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ color: 'var(--accent)', fontSize: 12, fontWeight: 700, letterSpacing: 2, textTransform: 'uppercase' }}>MODO DEMO</span>
              <Link to="/register" style={{ color: 'var(--text-highlight)', fontSize: 12, fontWeight: 600, textDecoration: 'underline' }}>
                Criar Conta Grátis →
              </Link>
            </div>
          )}
        </div>

        {loading ? (
          <GamifiedLoader label="A carregar domínios..." />
        ) : domains.length === 0 ? (
          <div style={{ textAlign: 'center', marginTop: 80 }}>
            <p style={{ color: 'var(--text-muted)', fontSize: 48, marginBottom: 16 }}>⚡</p>
            <p style={{ color: 'var(--text-muted)', fontSize: 16, marginBottom: 8 }}>Nenhum domínio criado ainda.</p>
            <p style={{ color: 'var(--border-color)', fontSize: 13 }}>Cria o teu primeiro domínio para começar a treinar.</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 20 }}>
            {domains.map(({ domain, stats }) => (
              <div key={domain.id} style={{ position: 'relative' }}>
                <DomainSVGCard
                  domain={domain}
                  stats={stats}
                  onClick={() => navigate(`/criar/${domain.id}`)}
                />
                {/* Edit / Delete overlay — only for authenticated */}
                {isAuthenticated && (
                  <div style={{ position: 'absolute', top: 8, right: 8, display: 'flex', gap: 4, zIndex: 10 }}>
                    <button
                      onClick={(e) => { e.stopPropagation(); setEditingDomain(domain); }}
                      title="Editar domínio"
                      style={{ padding: '4px 8px', borderRadius: 6, background: 'rgba(0,0,0,0.6)', border: '1px solid var(--border-color)', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 13, backdropFilter: 'blur(4px)' }}
                    >
                      ✏
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDelete(domain.id); }}
                      title="Apagar domínio"
                      style={{ padding: '4px 8px', borderRadius: 6, background: 'rgba(0,0,0,0.6)', border: '1px solid #ef444433', color: '#ef4444', cursor: 'pointer', fontSize: 13, backdropFilter: 'blur(4px)' }}
                    >
                      🗑
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {showModal && (
        <NewDomainModal onClose={() => setShowModal(false)} onCreate={handleCreate} />
      )}

      {editingDomain && (
        <DomainEditModal
          domain={editingDomain}
          onSave={handleEditSave}
          onClose={() => setEditingDomain(null)}
        />
      )}
    </div>
  );
}
