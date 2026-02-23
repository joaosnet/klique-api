import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const NAV_LINKS = [
  { to: '/',           label: 'Início',     public: true  },
  { to: '/simulador',  label: 'Simulador',  public: false },
  { to: '/mural',      label: 'Mural',      public: false },
  { to: '/dashboard',  label: 'Dashboard',  public: false },
  { to: '/portfolio',  label: 'Portfólio',  public: true  },
];

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

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
      style={{ background: '#111827', borderBottom: '2px solid #6b21a8' }}
    >
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link
          to="/"
          className="font-title text-xl tracking-widest text-purple-400 hover:text-purple-300 transition-colors"
          onClick={() => setMenuOpen(false)}
        >
          GAME THEORY
        </Link>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-1">
          {NAV_LINKS.map(({ to, label, public: pub }) => {
            if (!pub && !isAuthenticated) return null;
            return (
              <Link
                key={to}
                to={to}
                className={`px-3 py-1.5 rounded text-sm uppercase tracking-wider transition-colors font-medium ${
                  isActive(to)
                    ? 'text-purple-400 bg-purple-900/30'
                    : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800'
                }`}
              >
                {label}
              </Link>
            );
          })}
        </div>

        {/* Desktop auth */}
        <div className="hidden md:flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <span className="text-xs text-gray-400 truncate max-w-[120px]">
                {user?.name || user?.email}
              </span>
              <button
                onClick={handleLogout}
                className="px-3 py-1.5 text-xs uppercase tracking-wider rounded border border-purple-700 text-purple-400 hover:bg-purple-900/40 transition-colors"
              >
                Sair
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="px-3 py-1.5 text-xs uppercase tracking-wider text-gray-300 hover:text-white transition-colors"
              >
                Entrar
              </Link>
              <Link
                to="/register"
                className="px-3 py-1.5 text-xs uppercase tracking-wider rounded bg-purple-700 hover:bg-purple-600 text-white transition-colors"
              >
                Cadastrar
              </Link>
            </>
          )}
        </div>

        {/* Hamburger */}
        <button
          className="md:hidden flex flex-col gap-1.5 p-2 rounded hover:bg-gray-800 transition-colors"
          onClick={() => setMenuOpen((o) => !o)}
          aria-label="Menu"
        >
          <span
            className={`block w-6 h-0.5 bg-gray-300 transition-transform duration-200 ${menuOpen ? 'translate-y-2 rotate-45' : ''}`}
          />
          <span
            className={`block w-6 h-0.5 bg-gray-300 transition-opacity duration-200 ${menuOpen ? 'opacity-0' : ''}`}
          />
          <span
            className={`block w-6 h-0.5 bg-gray-300 transition-transform duration-200 ${menuOpen ? '-translate-y-2 -rotate-45' : ''}`}
          />
        </button>
      </div>

      {/* Mobile drawer */}
      {menuOpen && (
        <div
          className="md:hidden border-t border-gray-800 px-4 py-3 flex flex-col gap-2"
          style={{ background: '#0f172a' }}
        >
          {NAV_LINKS.map(({ to, label, public: pub }) => {
            if (!pub && !isAuthenticated) return null;
            return (
              <Link
                key={to}
                to={to}
                onClick={() => setMenuOpen(false)}
                className={`px-3 py-2 rounded text-sm uppercase tracking-wider transition-colors ${
                  isActive(to)
                    ? 'text-purple-400 bg-purple-900/30'
                    : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800'
                }`}
              >
                {label}
              </Link>
            );
          })}

          <div className="border-t border-gray-800 mt-2 pt-2 flex flex-col gap-2">
            {isAuthenticated ? (
              <>
                <span className="text-xs text-gray-500 px-3">
                  {user?.name || user?.email}
                </span>
                <button
                  onClick={handleLogout}
                  className="px-3 py-2 text-sm uppercase tracking-wider rounded border border-purple-700 text-purple-400 text-left hover:bg-purple-900/40 transition-colors"
                >
                  Sair
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  onClick={() => setMenuOpen(false)}
                  className="px-3 py-2 text-sm uppercase tracking-wider text-gray-300 hover:bg-gray-800 rounded transition-colors"
                >
                  Entrar
                </Link>
                <Link
                  to="/register"
                  onClick={() => setMenuOpen(false)}
                  className="px-3 py-2 text-sm uppercase tracking-wider rounded bg-purple-700 text-white text-center hover:bg-purple-600 transition-colors"
                >
                  Cadastrar
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
