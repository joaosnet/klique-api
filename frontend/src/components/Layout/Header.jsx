import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import logo from '../../assets/logo.svg';
import './Header.css';
import { IconCameraShot, IconTicketPass, IconUserBadge } from '../Icons/ActionIcons';

export default function Header() {
    const { user, credits, isAuthenticated, logout } = useAuth();
    const { t } = useTranslation();
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
                    <img src={logo} alt="OmniFlash" className="logo-image" />
                    <span className="logo-text">{t('header.omniflash')}</span>
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
                        <IconCameraShot className="nav-link-icon" width={18} height={18} />
                        {t('header.create_avatar')}
                    </Link>

                    {isAuthenticated ? (
                        <>
                            <Link
                                to="/credits"
                                className={`credits-badge ${isActive('/credits') ? 'active' : ''}`}
                                onClick={closeMobileMenu}
                            >
                                <IconTicketPass className="credits-icon" width={20} height={20} />
                                <span className="credits-count">{credits.total}</span>
                                <span className="credits-label">{t('header.credits')}</span>
                            </Link>

                            <div className="user-menu">
                                <span className="user-name">
                                    <IconUserBadge width={16} height={16} />
                                    {user?.name?.split(' ')[0]}
                                </span>
                                <button onClick={handleLogout} className="btn-logout">
                                    {t('header.logout')}
                                </button>
                            </div>
                        </>
                    ) : (
                        <div className="auth-buttons">
                            <Link to="/login" className="btn-login" onClick={closeMobileMenu}>
                                {t('header.login')}
                            </Link>
                            <Link to="/register" className="btn-register" onClick={closeMobileMenu}>
                                {t('header.register')}
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

