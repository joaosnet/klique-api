import { useEffect } from 'react';

const COLORS = {
    'Roxo (Padrão)': { value: '#7c3aed', light: '#a855f7', dark: '#6b21a8' },
    'Azul': { value: '#2563eb', light: '#3b82f6', dark: '#1d4ed8' },
    'Verde': { value: '#16a34a', light: '#22c55e', dark: '#15803d' },
    'Laranja': { value: '#ea580c', light: '#f97316', dark: '#c2410c' },
    'Rosa': { value: '#db2777', light: '#ec4899', dark: '#be185d' },
};

function getAccentObj(hexValue) {
    const found = Object.values(COLORS).find(c => c.value === hexValue);
    return found || COLORS['Roxo (Padrão)'];
}

/** Returns system preference: 'dark' or 'light' */
function getSystemTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    return 'light';
}

/**
 * Applies the correct theme to `<html data-theme="...">`.
 * - 'auto' (or missing): follow the system/browser preference
 * - 'dark' / 'light': use the explicit choice
 */
function applyTheme(storedValue) {
    const resolved = (!storedValue || storedValue === 'auto')
        ? getSystemTheme()
        : storedValue;
    document.documentElement.setAttribute('data-theme', resolved);
}

export function useThemeInit() {
    useEffect(() => {
        // 1. Theme Mode
        const storedTheme = localStorage.getItem('app_theme'); // null | 'auto' | 'dark' | 'light'
        applyTheme(storedTheme);

        // 2. Accent Color
        const storedAccent = localStorage.getItem('app_accent');
        if (storedAccent) {
            const colorObj = getAccentObj(storedAccent);
            document.documentElement.style.setProperty('--accent', colorObj.value);
            document.documentElement.style.setProperty('--accent-light', colorObj.light);
            document.documentElement.style.setProperty('--accent-dark', colorObj.dark);
        }

        // 3. Real-time listener — reacts whenever the OS changes its theme
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const handleChange = () => {
            const current = localStorage.getItem('app_theme');
            // Only follow the OS when in auto mode (or never configured)
            if (!current || current === 'auto') {
                applyTheme('auto');
            }
        };

        mediaQuery.addEventListener('change', handleChange);
        return () => mediaQuery.removeEventListener('change', handleChange);
    }, []);
}
