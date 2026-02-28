import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { profileAPI } from '../services/api';
import './ProfilePage.css';
import './ToggleTheme.css';

const API_URL = import.meta.env.VITE_API_URL || '';

export default function ProfilePage() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [currentTheme, setCurrentTheme] = useState(
        document.documentElement.getAttribute('data-theme') || 'dark'
    );

    // Profile data
    const [profile, setProfile] = useState(null);
    const [profileLoading, setProfileLoading] = useState(true);

    // Avatar section state
    const [avatarSection, setAvatarSection] = useState(null); // null | 'generate' | 'upload'
    const [generatePrompt, setGeneratePrompt] = useState('');
    const [improveToggle, setImproveToggle] = useState(false);
    const [stylePrompt, setStylePrompt] = useState('');
    const [avatarLoading, setAvatarLoading] = useState(false);
    const [avatarMsg, setAvatarMsg] = useState('');
    const fileInputRef = useRef(null);

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

    useEffect(() => {
        profileAPI.getMe()
            .then(data => setProfile(data))
            .catch(() => setProfile(null))
            .finally(() => setProfileLoading(false));
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

    const handleGenerateAvatar = async () => {
        if (!generatePrompt.trim()) return;
        setAvatarLoading(true);
        setAvatarMsg('');
        try {
            await profileAPI.generateAvatar(generatePrompt);
            setAvatarMsg('Avatar a ser gerado em background. Volta em instantes para ver o resultado.');
            setGeneratePrompt('');
            setAvatarSection(null);
        } catch (e) {
            setAvatarMsg('Erro ao gerar avatar: ' + (e.message || ''));
        } finally {
            setAvatarLoading(false);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        setAvatarLoading(true);
        setAvatarMsg('');
        try {
            await profileAPI.uploadAvatar(file, improveToggle, stylePrompt);
            // Refresh profile to get new avatar_url
            const updated = await profileAPI.getMe();
            setProfile(updated);
            setAvatarMsg(improveToggle ? 'Foto carregada. Melhoria em curso, atualiza em breve.' : 'Avatar atualizado com sucesso.');
            setAvatarSection(null);
        } catch (e) {
            setAvatarMsg('Erro ao carregar avatar: ' + (e.message || ''));
        } finally {
            setAvatarLoading(false);
        }
    };

    const handleRemoveAvatar = async () => {
        if (!window.confirm('Remover avatar?')) return;
        try {
            await profileAPI.removeAvatar();
            setProfile(prev => prev ? { ...prev, avatar_url: null } : prev);
        } catch (e) {
            console.error(e);
        }
    };

    const avatarUrl = profile?.avatar_url
        ? (profile.avatar_url.startsWith('http') ? profile.avatar_url : `${API_URL}${profile.avatar_url}`)
        : null;

    const displayName = profile?.name || profile?.nickname || user?.name || '';
    const displayEmail = user?.email || '';
    const initials = (displayName || displayEmail).charAt(0).toUpperCase() || 'U';

    return (
        <div className="profile-container p-6 pb-24 max-w-md mx-auto fade-in-up mt-8">
            <h1 className="text-3xl font-title text-center mb-8 text-[var(--text-main)]">Meu Perfil</h1>

            {/* Avatar card */}
            <div className="profile-card" style={{ flexDirection: 'column', alignItems: 'center', gap: 12 }}>
                {/* Avatar display */}
                <div style={{ position: 'relative', display: 'inline-block' }}>
                    {avatarUrl ? (
                        <img
                            src={avatarUrl}
                            alt="Avatar"
                            style={{ width: 80, height: 80, borderRadius: '50%', objectFit: 'cover', border: '3px solid var(--accent)' }}
                        />
                    ) : (
                        <div className="profile-avatar" style={{ width: 80, height: 80, fontSize: 32, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            {initials}
                        </div>
                    )}
                </div>

                {displayName && <h2 style={{ color: 'var(--text-highlight)', fontSize: 16, fontWeight: 700, margin: 0 }}>{displayName}</h2>}
                <h2 className="profile-email">{displayEmail}</h2>

                {/* Avatar action buttons */}
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', justifyContent: 'center', marginTop: 4 }}>
                    <button
                        onClick={() => setAvatarSection(avatarSection === 'generate' ? null : 'generate')}
                        style={{ padding: '5px 12px', borderRadius: 6, border: '1px solid #7c3aed', background: avatarSection === 'generate' ? '#7c3aed22' : 'transparent', color: '#a78bfa', fontSize: 11, cursor: 'pointer', fontWeight: 600 }}
                    >
                        Gerar Avatar IA
                    </button>
                    <button
                        onClick={() => setAvatarSection(avatarSection === 'upload' ? null : 'upload')}
                        style={{ padding: '5px 12px', borderRadius: 6, border: '1px solid var(--border-color)', background: avatarSection === 'upload' ? 'var(--bg-card-inner)' : 'transparent', color: 'var(--text-muted)', fontSize: 11, cursor: 'pointer', fontWeight: 600 }}
                    >
                        Upload Foto
                    </button>
                    {avatarUrl && (
                        <button
                            onClick={handleRemoveAvatar}
                            style={{ padding: '5px 12px', borderRadius: 6, border: '1px solid #ef444433', background: 'transparent', color: '#ef4444', fontSize: 11, cursor: 'pointer', fontWeight: 600 }}
                        >
                            Remover
                        </button>
                    )}
                </div>

                {/* Generate Avatar section */}
                {avatarSection === 'generate' && (
                    <div style={{ width: '100%', marginTop: 8 }}>
                        <textarea
                            value={generatePrompt}
                            onChange={e => setGeneratePrompt(e.target.value)}
                            placeholder="Descreve o teu avatar ideal... Ex: retrato masculino com estilo cyberpunk, fundo neon azul"
                            rows={3}
                            style={{ width: '100%', background: 'var(--bg-card-inner)', border: '1px solid var(--border-color)', color: 'var(--text-main)', borderRadius: 6, padding: '8px 10px', fontSize: 12, outline: 'none', boxSizing: 'border-box', resize: 'vertical' }}
                        />
                        <button
                            onClick={handleGenerateAvatar}
                            disabled={avatarLoading || !generatePrompt.trim()}
                            style={{ marginTop: 6, width: '100%', padding: '8px 0', borderRadius: 6, background: '#7c3aed', border: 'none', color: '#fff', fontSize: 12, fontWeight: 700, cursor: 'pointer', opacity: (!generatePrompt.trim() || avatarLoading) ? 0.5 : 1 }}
                        >
                            {avatarLoading ? 'A gerar...' : 'Gerar Avatar'}
                        </button>
                    </div>
                )}

                {/* Upload section */}
                {avatarSection === 'upload' && (
                    <div style={{ width: '100%', marginTop: 8 }}>
                        <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', color: 'var(--text-muted)', fontSize: 12, marginBottom: 8 }}>
                            <input
                                type="checkbox"
                                checked={improveToggle}
                                onChange={e => setImproveToggle(e.target.checked)}
                                style={{ accentColor: 'var(--accent)' }}
                            />
                            Melhorar foto com IA
                        </label>
                        {improveToggle && (
                            <input
                                value={stylePrompt}
                                onChange={e => setStylePrompt(e.target.value)}
                                placeholder="Estilo artístico... Ex: anime, retrato cinematográfico, óleo"
                                style={{ width: '100%', background: 'var(--bg-card-inner)', border: '1px solid var(--border-color)', color: 'var(--text-main)', borderRadius: 6, padding: '7px 10px', fontSize: 12, outline: 'none', boxSizing: 'border-box', marginBottom: 8 }}
                            />
                        )}
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            disabled={avatarLoading}
                            style={{ width: '100%', padding: '8px 0', borderRadius: 6, background: 'var(--accent)', border: 'none', color: '#fff', fontSize: 12, fontWeight: 700, cursor: 'pointer', opacity: avatarLoading ? 0.5 : 1 }}
                        >
                            {avatarLoading ? 'A carregar...' : 'Escolher Foto'}
                        </button>
                        <input ref={fileInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={handleFileUpload} />
                    </div>
                )}

                {avatarMsg && (
                    <p style={{ color: avatarMsg.startsWith('Erro') ? '#ef4444' : '#22c55e', fontSize: 11, textAlign: 'center', margin: '4px 0 0' }}>
                        {avatarMsg}
                    </p>
                )}
            </div>

            {/* Settings */}
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
