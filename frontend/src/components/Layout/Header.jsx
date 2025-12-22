import { useAuth } from '../../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import './Header.css';

export default function Header() {
    const { user, credits, isAuthenticated, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    return (
        <header className="header">
            <div className="header-container">
                <Link to="/" className="logo">
                    <span className="logo-icon">🎄</span>
                    <span className="logo-text">Klique Natal</span>
                </Link>

                <nav className="nav">
                    {isAuthenticated ? (
                        <>
                            <Link to="/credits" className="credits-badge">
                                <span className="credits-icon">🎟️</span>
                                <span className="credits-count">{credits.total}</span>
                                <span className="credits-label">créditos</span>
                            </Link>

                            <div className="user-menu">
                                <span className="user-name">{user?.name?.split(' ')[0]}</span>
                                <button onClick={handleLogout} className="btn-logout">
                                    Sair
                                </button>
                            </div>
                        </>
                    ) : (
                        <div className="auth-buttons">
                            <Link to="/login" className="btn-login">
                                Entrar
                            </Link>
                        </div>
                    )}
                </nav>
            </div>
        </header>
    );
}
