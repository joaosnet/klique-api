import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { profileAPI, resolveApiUrl } from '../services/api';
import { IconLogout } from '../components/Icons/StatIcons';
import './ProfilePage.css';
import { useTranslation } from 'react-i18next';

export default function ProfilePage() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const { t } = useTranslation();

    // Profile data
    const [profile, setProfile] = useState(null);
    const [, setProfileLoading] = useState(true);

    // Avatar section state
    const [avatarSection, setAvatarSection] = useState(null); // null | 'generate' | 'upload'
    const [generatePrompt, setGeneratePrompt] = useState('');
    const [improveToggle, setImproveToggle] = useState(false);
    const [stylePrompt, setStylePrompt] = useState('');
    const [avatarLoading, setAvatarLoading] = useState(false);
    const [avatarMsg, setAvatarMsg] = useState('');
    const fileInputRef = useRef(null);

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

    const handleGenerateAvatar = async () => {
        if (!generatePrompt.trim()) return;
        setAvatarLoading(true);
        setAvatarMsg('');
        try {
            await profileAPI.generateAvatar(generatePrompt);
            setAvatarMsg(t('profile.avatar_generating'));
            setGeneratePrompt('');
            setAvatarSection(null);
        } catch (e) {
            setAvatarMsg(t('profile.avatar_error') + ': ' + (e.message || ''));
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
            setAvatarMsg(improveToggle ? t('profile.avatar_success') : t('profile.avatar_success'));
            setAvatarSection(null);
        } catch (e) {
            setAvatarMsg(t('profile.avatar_error') + ': ' + (e.message || ''));
        } finally {
            setAvatarLoading(false);
        }
    };

    const handleRemoveAvatar = async () => {
        if (!window.confirm(t('profile.change_avatar'))) return;
        try {
            await profileAPI.removeAvatar();
            setProfile(prev => prev ? { ...prev, avatar_url: null } : prev);
        } catch (e) {
            console.error(e);
        }
    };

    const avatarUrl = profile?.avatar_url
        ? resolveApiUrl(profile.avatar_url)
        : null;

    const displayName = profile?.name || profile?.nickname || user?.name || '';
    const displayEmail = user?.email || '';
    const initials = (displayName || displayEmail).charAt(0).toUpperCase() || 'U';

    return (
        <div className="profile-container p-6 pb-24 max-w-md mx-auto fade-in-up mt-8">
            <h1 className="text-3xl font-title text-center mb-8 text-[var(--text-main)]">{t('profile.title')}</h1>

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
                        style={{ padding: '5px 12px', borderRadius: 6, border: '1px solid var(--accent)', background: avatarSection === 'generate' ? 'color-mix(in srgb, var(--accent) 13%, transparent)' : 'transparent', color: 'var(--accent-light)', fontSize: 11, cursor: 'pointer', fontWeight: 600 }}
                    >
                        {t('profile.change_avatar')}
                    </button>
                    <button
                        onClick={() => setAvatarSection(avatarSection === 'upload' ? null : 'upload')}
                        style={{ padding: '5px 12px', borderRadius: 6, border: '1px solid var(--border-color)', background: avatarSection === 'upload' ? 'var(--bg-card-inner)' : 'transparent', color: 'var(--text-muted)', fontSize: 11, cursor: 'pointer', fontWeight: 600 }}
                    >
                        {t('profile.edit')}
                    </button>
                    {avatarUrl && (
                        <button
                            onClick={handleRemoveAvatar}
                            style={{ padding: '5px 12px', borderRadius: 6, border: '1px solid #ef444433', background: 'transparent', color: '#ef4444', fontSize: 11, cursor: 'pointer', fontWeight: 600 }}
                        >
                            {t('profile.cancel')}
                        </button>
                    )}
                </div>

                {/* Generate Avatar section */}
                {avatarSection === 'generate' && (
                    <div style={{ width: '100%', marginTop: 8 }}>
                        <textarea
                            value={generatePrompt}
                            onChange={e => setGeneratePrompt(e.target.value)}
                            placeholder={t('profile.avatar_prompt')}
                            rows={3}
                            style={{ width: '100%', background: 'var(--bg-card-inner)', border: '1px solid var(--border-color)', color: 'var(--text-main)', borderRadius: 6, padding: '8px 10px', fontSize: 12, outline: 'none', boxSizing: 'border-box', resize: 'vertical' }}
                        />
                        <button
                            onClick={handleGenerateAvatar}
                            disabled={avatarLoading || !generatePrompt.trim()}
                            style={{ marginTop: 6, width: '100%', padding: '8px 0', borderRadius: 6, background: 'var(--accent)', border: 'none', color: '#fff', fontSize: 12, fontWeight: 700, cursor: 'pointer', opacity: (!generatePrompt.trim() || avatarLoading) ? 0.5 : 1 }}
                        >
                            {avatarLoading ? t('common.loading') : t('profile.change_avatar')}
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
                            {t('profile.improve_photo')}
                        </label>
                        {improveToggle && (
                            <input
                                value={stylePrompt}
                                onChange={e => setStylePrompt(e.target.value)}
                                placeholder={t('profile.style_prompt')}
                                style={{ width: '100%', background: 'var(--bg-card-inner)', border: '1px solid var(--border-color)', color: 'var(--text-main)', borderRadius: 6, padding: '7px 10px', fontSize: 12, outline: 'none', boxSizing: 'border-box', marginBottom: 8 }}
                            />
                        )}
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            disabled={avatarLoading}
                            style={{ width: '100%', padding: '8px 0', borderRadius: 6, background: 'var(--accent)', border: 'none', color: '#fff', fontSize: 12, fontWeight: 700, cursor: 'pointer', opacity: avatarLoading ? 0.5 : 1 }}
                        >
                            {avatarLoading ? t('common.loading') : t('profile.edit')}
                        </button>
                        <input ref={fileInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={handleFileUpload} />
                    </div>
                )}

                {avatarMsg && (
                    <p style={{ color: avatarMsg.startsWith(t('profile.avatar_error')) ? '#ef4444' : '#22c55e', fontSize: 11, textAlign: 'center', margin: '4px 0 0' }}>
                        {avatarMsg}
                    </p>
                )}
            </div>

            {/* Settings */}
            <div className="profile-settings mt-8 space-y-4">
                <button
                    onClick={handleLogout}
                    className="w-full flex items-center justify-center space-x-2 p-4 rounded-xl bg-red-500/10 text-red-500 border border-red-500/20 hover:bg-red-500/20 transition-colors font-medium text-lg mt-8"
                >
                    <IconLogout width={20} height={20} />
                    <span>{t('profile.logout')}</span>
                </button>
            </div>
        </div>
    );
}
