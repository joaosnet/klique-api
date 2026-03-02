import React from 'react';

const defaultProps = {
    width: 24,
    height: 24,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 2,
    strokeLinecap: "round",
    strokeLinejoin: "round"
};

export const IconLogo = ({ className = '', ...props }) => (
    <svg {...defaultProps} viewBox="0 0 32 32" className={`text-purple-500 ${className}`} {...props}>
        <defs>
            <linearGradient id="logo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#c084fc" />
                <stop offset="50%" stopColor="#9333ea" />
                <stop offset="100%" stopColor="#4c1d95" />
            </linearGradient>
            <filter id="logo-glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
        </defs>

        {/* Hexágono exterior */}
        <path
            d="M16 2L2 10v12l14 8 14-8V10L16 2z"
            fill="url(#logo-grad)"
            fillOpacity="0.1"
            stroke="url(#logo-grad)"
            strokeWidth="1.5"
        />

        {/* Forma interna (raio modificado/ampulheta) */}
        <path
            d="M19 6L9 16h6l-2 10 10-10h-6l2-10z"
            fill="url(#logo-grad)"
            stroke="#fff"
            strokeWidth="1"
            filter="url(#logo-glow)"
        />
    </svg>
);

export const IconTime = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-blue-400 ${className}`} {...props}>
        <defs>
            <linearGradient id="time-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#60a5fa" />
                <stop offset="100%" stopColor="#1e40af" />
            </linearGradient>
        </defs>
        <circle cx="12" cy="12" r="10" fill="rgba(96,165,250,0.15)" stroke="url(#time-grad)" strokeWidth="2" />
        <path d="M12 6v6l4 2" stroke="url(#time-grad)" strokeWidth="2.5" />
        <circle cx="12" cy="12" r="2" fill="#fff" stroke="none" />
    </svg>
);

export const IconStudy = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-amber-400 ${className}`} {...props}>
        <defs>
            <linearGradient id="study-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#fbbf24" />
                <stop offset="100%" stopColor="#b45309" />
            </linearGradient>
        </defs>
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" stroke="url(#study-grad)" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" fill="rgba(251,191,36,0.15)" stroke="url(#study-grad)" />
        <path d="M16 6h-6" stroke="#fff" strokeOpacity="0.6" />
        <path d="M16 10h-6" stroke="#fff" strokeOpacity="0.6" />
        {/* Marcador */}
        <path d="M9 2v6l2-1 2 1V2H9z" fill="url(#study-grad)" stroke="none" />
    </svg>
);

export const IconQuestions = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-rose-400 ${className}`} {...props}>
        <defs>
            <linearGradient id="quest-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#fb7185" />
                <stop offset="100%" stopColor="#be123c" />
            </linearGradient>
        </defs>
        <circle cx="12" cy="12" r="10" fill="rgba(251,113,133,0.15)" stroke="url(#quest-grad)" />
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" stroke="url(#quest-grad)" strokeWidth="2.5" />
        <line x1="12" y1="17" x2="12.01" y2="17" stroke="url(#quest-grad)" strokeWidth="3" />
    </svg>
);

export const IconTarget = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-emerald-400 ${className}`} {...props}>
        <defs>
            <linearGradient id="target-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#34d399" />
                <stop offset="100%" stopColor="#047857" />
            </linearGradient>
        </defs>
        <circle cx="12" cy="12" r="10" fill="rgba(52,211,153,0.15)" stroke="url(#target-grad)" />
        <circle cx="12" cy="12" r="6" stroke="url(#target-grad)" strokeDasharray="3 3" />
        <circle cx="12" cy="12" r="2" fill="url(#target-grad)" stroke="none" />
        <path d="M12 2v2M12 20v2M2 12h2M20 12h2" stroke="url(#target-grad)" />
    </svg>
);

export const IconProgress = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-indigo-400 ${className}`} {...props}>
        <defs>
            <linearGradient id="prog-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#818cf8" />
                <stop offset="100%" stopColor="#4338ca" />
            </linearGradient>
        </defs>
        <path d="M3 3v18h18" stroke="url(#prog-grad)" strokeWidth="2.5" />
        <path d="M18 9l-5 5-4-4-5 5" stroke="url(#prog-grad)" strokeWidth="2.5" />
        <circle cx="18" cy="9" r="2" fill="#fff" stroke="none" />
        <path d="M18 9v4h-4" fill="rgba(129,140,248,0.2)" stroke="none" />
    </svg>
);

export const IconLog = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-pink-400 ${className}`} {...props}>
        <defs>
            <linearGradient id="log-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f472b6" />
                <stop offset="100%" stopColor="#be185d" />
            </linearGradient>
        </defs>
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" fill="rgba(244,114,182,0.15)" stroke="url(#log-grad)" />
        <path d="M14 2v6h6" stroke="url(#log-grad)" />
        <line x1="16" y1="13" x2="8" y2="13" stroke="url(#log-grad)" />
        <line x1="16" y1="17" x2="8" y2="17" stroke="url(#log-grad)" />
        <polyline points="10 9 9 9 8 9" stroke="url(#log-grad)" />
    </svg>
);

export const IconLogout = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-red-500 ${className}`} {...props}>
        <defs>
            <linearGradient id="logout-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f87171" />
                <stop offset="100%" stopColor="#b91c1c" />
            </linearGradient>
        </defs>
        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" stroke="url(#logout-grad)" strokeWidth="2.5" />
        <polyline points="16 17 21 12 16 7" stroke="url(#logout-grad)" strokeWidth="2.5" />
        <line x1="21" y1="12" x2="9" y2="12" stroke="url(#logout-grad)" strokeWidth="2.5" />
    </svg>
);
