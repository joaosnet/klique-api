import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { StatusBar, Style } from '@capacitor/status-bar';
import { Capacitor } from '@capacitor/core';

export function useDynamicStatusBar() {
    const location = useLocation();

    useEffect(() => {
        let timeoutId;

        const updateStatusBar = async () => {
            try {
                const isDark = document.documentElement.getAttribute('data-theme') === 'dark' ||
                    (!document.documentElement.hasAttribute('data-theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);

                const rootStyles = getComputedStyle(document.documentElement);
                // Fallback to a dark color if somehow var not parsed correctly
                let bgColor = rootStyles.getPropertyValue('--bg-app').trim() || (isDark ? '#12121a' : '#f8fafc');

                // Update Web Meta Tag
                let metaThemeColor = document.querySelector('meta[name="theme-color"]');
                if (!metaThemeColor) {
                    metaThemeColor = document.createElement('meta');
                    metaThemeColor.name = 'theme-color';
                    document.head.appendChild(metaThemeColor);
                }
                metaThemeColor.setAttribute('content', bgColor);

                // Update Capacitor Status Bar (Android/iOS only)
                if (Capacitor.isNativePlatform()) {
                    await StatusBar.setBackgroundColor({ color: bgColor });
                    await StatusBar.setStyle({ style: isDark ? Style.Dark : Style.Light });
                }
            } catch (e) {
                console.warn('Error updating status bar:', e);
            }
        };

        const handleUpdate = () => {
            // Debounce slightly to ensure CSS changes have been applied
            clearTimeout(timeoutId);
            timeoutId = setTimeout(updateStatusBar, 50);
        };

        handleUpdate();

        // Listen for theme attribute changes to adapt dynamically 
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'data-theme' || mutation.attributeName === 'style') {
                    handleUpdate();
                }
            });
        });

        observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'style'] });

        return () => {
            clearTimeout(timeoutId);
            observer.disconnect();
        };
    }, [location.pathname]);
}
