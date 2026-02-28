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

      </div>

      {/* Mobile Floating Menu (Replaces Hamburger) */}

      {/* Backdrop overlay */}
      <div
        className={`md:hidden fixed inset-0 z-40 transition-opacity duration-300 ${menuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
        style={{ background: 'rgba(0, 0, 0, 0.5)', backdropFilter: 'blur(3px)' }}
        onClick={() => setMenuOpen(false)}
      />

      <div className="md:hidden fixed bottom-6 right-6 z-50 flex flex-col items-end gap-4 pointer-events-none">

        {/* Menu Items */}
        <div
          className={`flex flex-col items-end gap-3 transition-all duration-300 origin-bottom ${menuOpen ? 'opacity-100 translate-y-0 pointer-events-auto' : 'opacity-0 translate-y-8 pointer-events-none'
            }`}
        >
          {/* Profile / User info */}
          {isAuthenticated && user && (
            <div className="px-5 py-2.5 rounded-full text-xs font-medium shadow-md mb-2" style={{ background: 'var(--bg-card)', color: 'var(--text-muted)', border: '1px solid var(--border-color)' }}>
              {user.name || user.email}
            </div>
          )}

          {/* Links */}
          {NAV_LINKS.map(({ to, label, public: pub, guestOnly = false }) => {
            if (!pub && !isAuthenticated) return null;
            if (guestOnly && isAuthenticated) return null;
            return (
              <Link
                key={to}
                to={to}
                onClick={() => setMenuOpen(false)}
                className="px-6 py-3 rounded-full text-sm font-bold tracking-widest uppercase shadow-lg transition-transform hover:scale-105 active:scale-95 flex items-center gap-2"
                style={{
                  color: isActive(to) ? '#fff' : 'var(--text-main)',
                  background: isActive(to) ? 'var(--accent)' : 'var(--bg-card)',
                  border: isActive(to) ? 'none' : '1px solid var(--border-color)',
                }}
              >
                {label}
              </Link>
            );
          })}

          {/* Auth / Settings Actions */}
          <div className="flex flex-col items-end gap-3 w-full mt-2">
            <button
              onClick={() => { setShowThemeModal(true); setMenuOpen(false); }}
              className="px-6 py-3 rounded-full text-sm font-bold tracking-widest uppercase shadow-lg transition-transform hover:scale-105 active:scale-95 flex items-center gap-2"
              style={{ background: 'var(--bg-card)', color: 'var(--text-main)', border: '1px solid var(--border-color)' }}
            >
              ⚙️ Ajustes Visuais
            </button>

            {isAuthenticated ? (
              <button
                onClick={handleLogout}
                className="px-6 py-3 rounded-full text-sm font-bold tracking-widest uppercase shadow-lg transition-transform hover:scale-105 active:scale-95 flex items-center gap-2"
                style={{ background: 'var(--bg-card)', color: 'var(--accent)', border: '1px solid var(--accent-dark)' }}
              >
                Sair
              </button>
            ) : (
              <>
                <Link
                  to="/login"
                  onClick={() => setMenuOpen(false)}
                  className="px-6 py-3 rounded-full text-sm font-bold tracking-widest uppercase shadow-lg transition-transform hover:scale-105 active:scale-95 flex items-center gap-2"
                  style={{ background: 'var(--bg-card)', color: 'var(--text-main)', border: '1px solid var(--border-color)' }}
                >
                  Entrar
                </Link>
                <Link
                  to="/register"
                  onClick={() => setMenuOpen(false)}
                  className="px-6 py-3 rounded-full text-sm font-bold tracking-widest uppercase shadow-lg transition-transform hover:scale-105 active:scale-95 flex items-center gap-2"
                  style={{ background: 'var(--accent)', color: '#fff', border: 'none' }}
                >
                  Cadastrar
                </Link>
              </>
            )}
          </div>
        </div>

        {/* FAB Button */}
        <button
          onClick={() => setMenuOpen((o) => !o)}
          className="w-16 h-16 rounded-full flex items-center justify-center shadow-2xl transition-transform duration-300 hover:scale-105 active:scale-95 pointer-events-auto relative"
          style={{
            background: 'var(--accent)',
            color: '#fff',
            boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
          }}
          aria-label="Menu"
        >
          <span
            className={`w-7 h-1 rounded-full bg-white absolute transition-transform duration-300 ${menuOpen ? 'rotate-45' : 'translate-y-[-8px]'}`}
          />
          <span
            className={`w-7 h-1 rounded-full bg-white absolute transition-opacity duration-300 ${menuOpen ? 'opacity-0' : 'opacity-100'}`}
          />
          <span
            className={`w-7 h-1 rounded-full bg-white absolute transition-transform duration-300 ${menuOpen ? '-rotate-45' : 'translate-y-[8px]'}`}
          />
        </button>

      </div>

      {showThemeModal && <ThemeSettingsModal onClose={() => setShowThemeModal(false)} />}
    </nav>
  );
}
