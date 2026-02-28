import { useState, useEffect } from 'react';
import './GamifiedLoader.css';

const LORE_TIPS = [
    "O Oráculo está a calcular as tuas próximas jogadas...",
    "A analisar padrões nas tuas respostas recentes...",
    "Domínios de alto nível requerem máxima precisão...",
    "O teu streak define o teu ritmo de evolução...",
    "Preparando o terreno para a próxima simulação...",
    "Sincronizando as tuas sinapses com o servidor central...",
    "A forjar novas conexões de memória a longo prazo..."
];

export default function GamifiedLoader({ fullScreen = true, label = null }) {
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
