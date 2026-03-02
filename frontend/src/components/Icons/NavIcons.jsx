import React from 'react';

// Common SVG props to maintain consistency
const defaultProps = {
    width: 28,
    height: 28,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 2,
    strokeLinecap: "round",
    strokeLinejoin: "round"
};

export const IconDomains = ({ className = '', active = false, ...props }) => (
    <svg
        {...defaultProps}
        className={`transition-all duration-300 ${active ? 'scale-110 drop-shadow-[0_0_8px_rgba(167,139,250,0.6)] text-[#a78bfa]' : 'text-gray-400'} ${className}`}
        {...props}
    >
        {/* Definições de gradiente e filtros para o modo ativo */}
        <defs>
            <linearGradient id="domains-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#c4b5fd" />
                <stop offset="100%" stopColor="#7c3aed" />
            </linearGradient>
            <filter id="domains-glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="2" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
        </defs>

        {/* Fundo isométrico / base do cartão */}
        <path
            d="M12 3l9 6-9 6-9-6 9-6z"
            fill={active ? "url(#domains-grad)" : "transparent"}
            stroke={active ? "url(#domains-grad)" : "currentColor"}
            strokeWidth={active ? "1.5" : "2"}
            className="transition-all duration-500 origin-center"
            style={active ? { transform: 'translateY(-2px)' } : {}}
        />
        {/* Camadas inferiores */}
        <path
            d="M3 14l9 6 9-6"
            stroke={active ? "#7c3aed" : "currentColor"}
            strokeWidth="2"
            strokeOpacity={active ? "0.7" : "1"}
            className="transition-all duration-300"
        />
        <path
            d="M3 9l9 6 9-6"
            stroke={active ? "rgba(255,255,255,0.8)" : "currentColor"}
            strokeWidth={active ? "1" : "2"}
            strokeOpacity={active ? "0.9" : "0"}
            className="transition-all duration-300 transform-gpu"
            style={active ? { transform: 'scale(0.8) translateY(-2px)' } : {}}
            transform-origin="center"
        />
    </svg>
);

export const IconTrain = ({ className = '', active = false, ...props }) => (
    <svg
        {...defaultProps}
        className={`transition-all duration-300 ${active ? 'scale-110 drop-shadow-[0_0_8px_rgba(245,158,11,0.6)] text-[#f59e0b]' : 'text-gray-400'} ${className}`}
        {...props}
    >
        <defs>
            <linearGradient id="train-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#fcd34d" />
                <stop offset="100%" stopColor="#d97706" />
            </linearGradient>
        </defs>
        {/* Raio/Energia */}
        <path
            d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"
            fill={active ? "url(#train-grad)" : "transparent"}
            stroke={active ? "url(#train-grad)" : "currentColor"}
            strokeWidth={active ? "1.5" : "2"}
            strokeLinejoin="miter"
            className="transition-all duration-500 origin-center"
            style={active ? { transform: 'rotate(10deg) scale(1.1)' } : {}}
        />
        {/* Detalhe interior */}
        <path
            d="M11 6L5 13h5l-1 5 7-9h-5l1-5z"
            fill="rgba(255,255,255,0.4)"
            stroke="none"
            className={`transition-opacity duration-300 ${active ? 'opacity-100' : 'opacity-0'}`}
            style={{ transform: active ? 'rotate(10deg) scale(1.1)' : 'none', transformOrigin: 'center' }}
        />
    </svg>
);

export const IconDashboard = ({ className = '', active = false, ...props }) => (
    <svg
        {...defaultProps}
        className={`transition-all duration-300 ${active ? 'scale-110 drop-shadow-[0_0_8px_rgba(34,197,94,0.6)] text-[#22c55e]' : 'text-gray-400'} ${className}`}
        {...props}
    >
        <defs>
            <linearGradient id="dash-grad1" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#86efac" />
                <stop offset="100%" stopColor="#16a34a" />
            </linearGradient>
            <linearGradient id="dash-grad2" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#4ade80" />
                <stop offset="100%" stopColor="#15803d" />
            </linearGradient>
            <linearGradient id="dash-grad3" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#bbf7d0" />
                <stop offset="100%" stopColor="#22c55e" />
            </linearGradient>
        </defs>

        {/* Barras animadas */}
        <rect
            x="4" y={active ? "14" : "16"} width="4" height={active ? "6" : "4"} rx="1"
            fill={active ? "url(#dash-grad1)" : "transparent"}
            stroke={active ? "none" : "currentColor"}
            className="transition-all duration-300 origin-bottom"
        />
        <rect
            x="10" y={active ? "8" : "12"} width="4" height={active ? "12" : "8"} rx="1"
            fill={active ? "url(#dash-grad2)" : "transparent"}
            stroke={active ? "none" : "currentColor"}
            className="transition-all duration-300 delay-75 origin-bottom"
        />
        <rect
            x="16" y={active ? "4" : "8"} width="4" height={active ? "16" : "12"} rx="1"
            fill={active ? "url(#dash-grad3)" : "transparent"}
            stroke={active ? "none" : "currentColor"}
            className="transition-all duration-300 delay-150 origin-bottom"
        />

        {/* Base grid line when active */}
        <line
            x1="2" y1="21" x2="22" y2="21"
            stroke={active ? "#16a34a" : "transparent"}
            strokeWidth="2"
            strokeLinecap="round"
            className="transition-all duration-300"
        />
    </svg>
);

export const IconVisual = ({ className = '', active = false, ...props }) => (
    <svg
        {...defaultProps}
        className={`transition-all duration-300 ${active ? 'scale-110 drop-shadow-[0_0_8px_rgba(236,72,153,0.6)] text-[#ec4899]' : 'text-gray-400'} ${className}`}
        {...props}
    >
        <defs>
            <linearGradient id="visual-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f472b6" />
                <stop offset="100%" stopColor="#db2777" />
            </linearGradient>
        </defs>

        {/* Olho - Contorno */}
        <path
            d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"
            fill={active ? "rgba(236,72,153,0.15)" : "transparent"}
            stroke={active ? "#db2777" : "currentColor"}
            className="transition-all duration-500"
        />
        {/* Íris */}
        <circle
            cx="12" cy="12" r={active ? "4" : "3"}
            fill={active ? "url(#visual-grad)" : "transparent"}
            stroke={active ? "url(#visual-grad)" : "currentColor"}
            className="transition-all duration-300 origin-center"
        />
        {/* Brilho da Pupila */}
        <circle
            cx="13" cy="11" r="1"
            fill="white" stroke="none"
            className={`transition-opacity duration-300 ${active ? 'opacity-100' : 'opacity-0'}`}
        />
    </svg>
);

export const IconProfile = ({ className = '', active = false, ...props }) => (
    <svg
        {...defaultProps}
        className={`transition-all duration-300 ${active ? 'scale-110 drop-shadow-[0_0_8px_rgba(56,189,248,0.6)] text-[#38bdf8]' : 'text-gray-400'} ${className}`}
        {...props}
    >
        <defs>
            <linearGradient id="profile-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#7dd3fc" />
                <stop offset="100%" stopColor="#0284c7" />
            </linearGradient>
            <linearGradient id="profile-bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="rgba(56,189,248,0.2)" />
                <stop offset="100%" stopColor="rgba(2,132,199,0.05)" />
            </linearGradient>
        </defs>

        {/* Círculo de fundo que aparece quando ativo */}
        <circle
            cx="12" cy="12" r={active ? "11" : "0"}
            fill="url(#profile-bg)" stroke="none"
            className="transition-all duration-500 origin-center"
        />

        {/* Corpo */}
        <path
            d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"
            fill={active ? "rgba(2,132,199,0.3)" : "transparent"}
            stroke={active ? "url(#profile-grad)" : "currentColor"}
            className={`transition-all duration-300 origin-bottom ${active ? 'translate-y-[-1px]' : ''}`}
        />
        {/* Cabeça */}
        <circle
            cx="12" cy="7" r="4"
            fill={active ? "url(#profile-grad)" : "transparent"}
            stroke={active ? "url(#profile-grad)" : "currentColor"}
            className={`transition-all duration-300 origin-center ${active ? 'scale-110 translate-y-[1px]' : ''}`}
        />

        {/* Detalhe visor tipo capacete/tecnológico quando ativo */}
        <path
            d="M9 7h6"
            stroke="rgba(255,255,255,0.8)"
            strokeWidth="2"
            strokeLinecap="round"
            className={`transition-all duration-300 ${active ? 'opacity-100 scale-100' : 'opacity-0 scale-50'}`}
            style={{ transformOrigin: 'center 7px' }}
        />
    </svg>
);
