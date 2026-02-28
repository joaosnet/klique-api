import { useState, useEffect } from 'react';
import '../../pages/ToggleTheme.css';

const COLORS = [
    { name: 'Roxo (Padrão)', value: '#7c3aed', light: '#a855f7', dark: '#6b21a8' },
    { name: 'Azul', value: '#2563eb', light: '#3b82f6', dark: '#1d4ed8' },
    { name: 'Verde', value: '#16a34a', light: '#22c55e', dark: '#15803d' },
    { name: 'Laranja', value: '#ea580c', light: '#f97316', dark: '#c2410c' },
    { name: 'Rosa', value: '#db2777', light: '#ec4899', dark: '#be185d' },
];

export default function ThemeSettingsModal({ onClose }) {
    const [theme, setTheme] = useState(localStorage.getItem('app_theme') || 'auto');
    const [accent, setAccent] = useState(localStorage.getItem('app_accent') || '#7c3aed');

    useEffect(() => {
        // Escuta a tecla ESC
        const handleKeyDown = (e) => {
            if (e.key === 'Escape') onClose();
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [onClose]);

    const handleThemeChange = (newTheme) => {
        setTheme(newTheme);
        localStorage.setItem('app_theme', newTheme);
        // Resolve 'auto' to the actual system preference
        const resolved = newTheme === 'auto'
            ? (window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
            : newTheme;
        document.documentElement.setAttribute('data-theme', resolved);
    };

    const handleAccentChange = (colorObj) => {
        setAccent(colorObj.value);
        localStorage.setItem('app_accent', colorObj.value);
        document.documentElement.style.setProperty('--accent', colorObj.value);
        document.documentElement.style.setProperty('--accent-light', colorObj.light);
        document.documentElement.style.setProperty('--accent-dark', colorObj.dark);
    };

    return (
        <div
            style={{
                position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999,
                backdropFilter: 'blur(4px)'
            }}
            onClick={onClose}
        >
            <div
                style={{
                    background: 'var(--bg-card)', border: '1px solid var(--accent-dark)', borderRadius: 12,
                    padding: '2rem', width: '100%', maxWidth: 420,
                    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)'
                }}
                onClick={(e) => e.stopPropagation()}
            >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                    <h2 style={{ color: 'var(--text-highlight)', fontSize: 18, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase', margin: 0 }}>
                        Configuração Visual
                    </h2>
                    <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 24 }}>
                        &times;
                    </button>
                </div>

                {/* Theme Mode — CSS Slider */}
                {(() => {
                    const themeState = theme === 'light' ? 0 : theme === 'auto' ? 1 : 2;
                    const getThemeName = (ts) => ts === 0 ? 'light' : ts === 1 ? 'auto' : 'dark';

                    const cycleTheme = () => {
                        const nextState = (themeState + 1) % 3;
                        handleThemeChange(getThemeName(nextState));
                    };

                    return (
                        <div style={{ marginBottom: 24 }}>
                            <label style={{ color: 'var(--text-muted)', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase', display: 'block', marginBottom: 8 }}>
                                Modo
                            </label>

                            <div className={`day-night-toggle flex items-center gap-2`} title="Modo Visual">
                                <span className="text-xs uppercase font-bold" style={{ color: 'var(--text-secondary)', minWidth: 40, textAlign: 'left' }}>
                                    {getThemeName(themeState)}
                                </span>
                                <div
                                    className={`toggle-track theme-${getThemeName(themeState)}`}
                                    onClick={cycleTheme}
                                >
                                    <div className="toggle-bg-color"></div>

                                    {/* Visual elements */}
                                    <div className="cloud cloud-1"></div>
                                    <div className="cloud cloud-2"></div>

                                    <div className="star star-1"></div>
                                    <div className="star star-2"></div>
                                    <div className="star star-3"></div>

                                    {/* Knob */}
                                    <div className="toggle-knob">
                                        <span className="knob-content" style={{ color: '#1a1a2e' }}>A</span>
                                        <div className="moon-craters">
                                            <div className="crater crater-1"></div>
                                            <div className="crater crater-2"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    );
                })()}

                {/* Accent Color */}
                <div>
                    <label style={{ color: 'var(--text-muted)', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase', display: 'block', marginBottom: 8 }}>
                        Cor de Destaque
                    </label>
                    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                        {COLORS.map((c) => (
                            <button
                                key={c.value}
                                onClick={() => handleAccentChange(c)}
                                title={c.name}
                                style={{
                                    width: 36, height: 36, borderRadius: '50%', cursor: 'pointer',
                                    background: c.value,
                                    border: accent === c.value ? '3px solid var(--text-main)' : '2px solid transparent',
                                    outline: accent === c.value ? `2px solid ${c.value}` : 'none',
                                    outlineOffset: 2,
                                    transition: 'transform 0.2s',
                                    transform: accent === c.value ? 'scale(1.1)' : 'scale(1)'
                                }}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
