import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import ThemeSettingsModal from './ThemeSettingsModal';

const NAV_LINKS = [
  { to: '/dominios', label: 'Domínios', public: true, guestOnly: false },
  { to: '/treinar', label: 'Treinar', public: false, guestOnly: false },
  { to: '/oracle', label: 'Dashboard', public: false, guestOnly: false },
];

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [showThemeModal, setShowThemeModal] = useState(false);

  const handleLogout = async () => {
    await logout();
    setMenuOpen(false);
    navigate('/login');
  };

  const isActive = (path) =>
    path === '/' ? location.pathname === '/' : location.pathname.startsWith(path);

  return (
    <nav
      className="sticky top-0 z-50 w-full"
      style={{ background: 'var(--bg-card)', borderBottom: '2px solid var(--accent)', transition: 'background-color 0.3s ease' }}
    >
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link
          to="/"
          className="font-title text-xl tracking-widest transition-colors"
          style={{ color: 'var(--accent-light)' }}
          onClick={() => setMenuOpen(false)}
        >
          OMNIFLASH
        </Link>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-1">
          {NAV_LINKS.map(({ to, label, public: pub, guestOnly = false }) => {
            if (!pub && !isAuthenticated) return null;
            if (guestOnly && isAuthenticated) return null;
            return (
              <Link
                key={to}
                to={to}
                className={`px-3 py-1.5 rounded text-sm uppercase tracking-wider transition-colors font-medium`}
                style={{
                  color: isActive(to) ? 'var(--accent-light)' : 'var(--text-muted)',
                  background: isActive(to) ? 'var(--bg-card-inner)' : 'transparent',
                }}
              >
                {label}
              </Link>
            );
          })}
        </div>

        {/* Desktop auth */}
        <div className="hidden md:flex items-center gap-3">
          <button
            onClick={() => setShowThemeModal(true)}
            style={{
              background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer',
              fontSize: 16, padding: '4px 8px'
            }}
            title="Ajustes Visuais"
          >
            ⚙️
          </button>

          {isAuthenticated ? (
            <>
              <span className="text-xs truncate max-w-[120px]" style={{ color: 'var(--text-muted)' }}>
                {user?.name || user?.email}
              </span>
              <button
                onClick={handleLogout}
                className="px-3 py-1.5 text-xs uppercase tracking-wider rounded border transition-colors"
                style={{ borderColor: 'var(--accent-dark)', color: 'var(--accent-light)' }}
              >
                Sair
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="px-3 py-1.5 text-xs uppercase tracking-wider transition-colors"
                style={{ color: 'var(--text-main)' }}
              >
                Entrar
              </Link>
              <Link
                to="/register"
                className="px-3 py-1.5 text-xs uppercase tracking-wider rounded transition-colors"
                style={{ background: 'var(--accent)', color: '#fff' }}
              >
                Cadastrar
              </Link>
            </>
          )}
        </div>

        {/* Hamburger */}
        <button
          className="md:hidden flex flex-col gap-1.5 p-2 rounded transition-colors"
          style={{ background: menuOpen ? 'var(--bg-card-inner)' : 'transparent' }}
          onClick={() => setMenuOpen((o) => !o)}
          aria-label="Menu"
        >
          <span
            className={`block w-6 h-0.5 transition-transform duration-200 ${menuOpen ? 'translate-y-2 rotate-45' : ''}`}
            style={{ background: 'var(--text-main)' }}
          />
          <span
            className={`block w-6 h-0.5 transition-opacity duration-200 ${menuOpen ? 'opacity-0' : ''}`}
            style={{ background: 'var(--text-main)' }}
          />
          <span
            className={`block w-6 h-0.5 transition-transform duration-200 ${menuOpen ? '-translate-y-2 -rotate-45' : ''}`}
            style={{ background: 'var(--text-main)' }}
          />
        </button>
      </div>

      {/* Mobile drawer */}
      {menuOpen && (
        <div
          className="md:hidden border-t px-4 py-3 flex flex-col gap-2"
          style={{ background: 'var(--bg-card-inner)', borderColor: 'var(--border-color)' }}
        >
          {NAV_LINKS.map(({ to, label, public: pub, guestOnly = false }) => {
            if (!pub && !isAuthenticated) return null;
            if (guestOnly && isAuthenticated) return null;
            return (
              <Link
                key={to}
                to={to}
                onClick={() => setMenuOpen(false)}
                className={`px-3 py-2 rounded text-sm uppercase tracking-wider transition-colors`}
                style={{
                  color: isActive(to) ? 'var(--accent-light)' : 'var(--text-muted)',
                  background: isActive(to) ? 'var(--bg-app)' : 'transparent',
                }}
              >
                {label}
              </Link>
            );
          })}

          <div className="border-t mt-2 pt-2 flex flex-col gap-2" style={{ borderColor: 'var(--border-color)' }}>
            <button
              onClick={() => { setShowThemeModal(true); setMenuOpen(false); }}
              className="px-3 py-2 text-sm uppercase tracking-wider rounded text-left transition-colors"
              style={{ color: 'var(--text-main)' }}
            >
              ⚙️ Ajustes Visuais
            </button>

            {isAuthenticated ? (
              <>
                <span className="text-xs px-3" style={{ color: 'var(--text-muted)' }}>
                  {user?.name || user?.email}
                </span>
                <button
                  onClick={handleLogout}
                  className="px-3 py-2 text-sm uppercase tracking-wider rounded border text-left transition-colors"
                  style={{ borderColor: 'var(--accent-dark)', color: 'var(--accent-light)' }}
                >
                  Sair
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  onClick={() => setMenuOpen(false)}
                  className="px-3 py-2 text-sm uppercase tracking-wider rounded transition-colors"
                  style={{ color: 'var(--text-main)' }}
                >
                  Entrar
                </Link>
                <Link
                  to="/register"
                  onClick={() => setMenuOpen(false)}
                  className="px-3 py-2 text-sm uppercase tracking-wider rounded text-center transition-colors"
                  style={{ background: 'var(--accent)', color: '#fff' }}
                >
                  Cadastrar
                </Link>
              </>
            )}
          </div>
        </div>
      )}

      {showThemeModal && <ThemeSettingsModal onClose={() => setShowThemeModal(false)} />}
    </nav>
  );
}
