import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './GamifiedLoader.css';

export default function GamifiedLoader({ fullScreen = true, label = null }) {
    const { t } = useTranslation();
    const LORE_TIPS = [
        t('loader.tip1'),
        t('loader.tip2'),
        t('loader.tip3'),
        t('loader.tip4'),
        t('loader.tip5'),
        t('loader.tip6'),
        t('loader.tip7'),
    ];
    const [tipIndex, setTipIndex] = useState(0);

    useEffect(() => {
        // Change tip every 3.5 seconds
        const interval = setInterval(() => {
            setTipIndex((prev) => (prev + 1) % LORE_TIPS.length);
        }, 3500);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className={`gamified-loader-container ${fullScreen ? 'fullscreen' : ''}`}>
            <div className="loader-core">
                <div className="orbit orbit-1"></div>
                <div className="orbit orbit-2"></div>
                <div className="orbit orbit-3"></div>
                <div className="oracle-eye">
                    <div className="eye-core"></div>
                </div>
            </div>

            <div className="loader-text-area">
                {label && <div className="loader-label">{label}</div>}
                <div className="tips-container">
                    {LORE_TIPS.map((tip, index) => (
                        <div
                            key={index}
                            className={`lore-tip ${index === tipIndex ? 'active' : ''}`}
                        >
                            {tip}
                        </div>
                    ))}
                </div>
                <div className="progress-bar-container">
                    <div className="progress-bar-fill"></div>
                </div>
            </div>
        </div>
    );
}
