import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import './ProfilePage.css';
import './ToggleTheme.css';

export default function ProfilePage() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [currentTheme, setCurrentTheme] = useState(
        document.documentElement.getAttribute('data-theme') || 'dark'
    );

    // Sync state if HTML attribute changes externally (optional, but good practice)
    useEffect(() => {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'data-theme') {
                    setCurrentTheme(document.documentElement.getAttribute('data-theme') || 'dark');
                }
            });
        });
        observer.observe(document.documentElement, { attributes: true });
        return () => observer.disconnect();
    }, []);

    const handleLogout = async () => {
        try {
            await logout();
            navigate('/login');
        } catch (e) {
            console.error(e);
        }
    };

    const toggleTheme = () => {
        const next = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        setCurrentTheme(next);
    };

    return (
        <div className="profile-container p-6 pb-24 max-w-md mx-auto fade-in-up mt-8">
            <h1 className="text-3xl font-title text-center mb-8 text-[var(--text-main)]">Meu Perfil</h1>

            <div className="profile-card">
                <div className="profile-avatar">
                    {user?.email ? user.email.charAt(0).toUpperCase() : 'U'}
                </div>
                <h2 className="profile-email">{user?.email || 'user@example.com'}</h2>
            </div>

            <div className="profile-settings mt-8 space-y-4">
                <div className="setting-item flex justify-between items-center p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                    <span className="text-[var(--text-main)] font-medium font-body text-lg">Modo Escuro</span>
                    <label className="theme-toggle" style={{ transform: 'scale(0.8)' }}>
                        <input
                            className="theme-toggle__checkbox"
                            type="checkbox"
                            checked={currentTheme === 'dark'}
                            onChange={toggleTheme}
                        />
                        <div className="theme-toggle__container">
                            <div className="theme-toggle__circle"></div>
                            <svg className="theme-toggle__moon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z"></path></svg>
                            <svg className="theme-toggle__star theme-toggle__star--1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path></svg>
                        </div>
                    </label>
                </div>

                <button
                    onClick={handleLogout}
                    className="w-full flex items-center justify-center space-x-2 p-4 rounded-xl bg-red-500/10 text-red-500 border border-red-500/20 hover:bg-red-500/20 transition-colors font-medium text-lg mt-8"
                >
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                        <polyline points="16 17 21 12 16 7"></polyline>
                        <line x1="21" y1="12" x2="9" y2="12"></line>
                    </svg>
                    <span>Sair da Conta</span>
                </button>
            </div>
        </div>
    );
}
