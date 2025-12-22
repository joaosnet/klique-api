import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import logo from '../../assets/logo.svg';
import './Header.css';

export default function Header() {
    const { user, credits, isAuthenticated, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const handleLogout = async () => {
        await logout();
        setMobileMenuOpen(false);
        navigate('/login');
    };

    const closeMobileMenu = () => setMobileMenuOpen(false);

    const isActive = (path) => location.pathname === path;

    return (
        <header className="header">
            <div className="header-container">
                <Link to="/" className="logo" onClick={closeMobileMenu}>
                    <img src={logo} alt="Klique Natal" className="logo-image" />
                    <span className="logo-text">Klique Natal</span>
                </Link>

                {/* Hamburger Button - Mobile Only */}
                <button
                    className={`hamburger ${mobileMenuOpen ? 'open' : ''}`}
                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                    aria-label="Menu"
                >
                    <span></span>
                    <span></span>
                    <span></span>
                </button>

                <nav className={`nav ${mobileMenuOpen ? 'nav-open' : ''}`}>
                    {/* Links de navegação principais - sempre visíveis */}
                    <Link
                        to="/"
                        className={`nav-link ${isActive('/') ? 'active' : ''}`}
                        onClick={closeMobileMenu}
                    >
                        🎄 Criar Avatar
                    </Link>

                    {isAuthenticated ? (
                        <>
                            <Link
                                to="/credits"
                                className={`credits-badge ${isActive('/credits') ? 'active' : ''}`}
                                onClick={closeMobileMenu}
                            >
                                <span className="credits-icon">🎟️</span>
                                <span className="credits-count">{credits.total}</span>
                                <span className="credits-label">créditos</span>
                            </Link>

                            <div className="user-menu">
                                <span className="user-name">👤 {user?.name?.split(' ')[0]}</span>
                                <button onClick={handleLogout} className="btn-logout">
                                    Sair
                                </button>
                            </div>
                        </>
                    ) : (
                        <div className="auth-buttons">
                            <Link to="/login" className="btn-login" onClick={closeMobileMenu}>
                                Entrar
                            </Link>
                            <Link to="/register" className="btn-register" onClick={closeMobileMenu}>
                                Cadastrar
                            </Link>
                        </div>
                    )}
                </nav>

                {/* Overlay for mobile menu */}
                {mobileMenuOpen && (
                    <div className="nav-overlay" onClick={closeMobileMenu}></div>
                )}
            </div>
        </header>
    );
}

