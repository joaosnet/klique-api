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

export const IconClose = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-gray-400 hover:text-white transition-colors ${className}`} {...props}>
        <path d="M18 6L6 18" />
        <path d="M6 6l12 12" />
    </svg>
);

export const IconDelete = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-white ${className}`} {...props}>
        <defs>
            <linearGradient id="delete-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#fca5a5" />
                <stop offset="100%" stopColor="#ef4444" />
            </linearGradient>
        </defs>
        <path d="M3 6h18" stroke="url(#delete-grad)" strokeWidth="2.5" />
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke="url(#delete-grad)" strokeWidth="2" />
        <line x1="10" y1="11" x2="10" y2="17" stroke="#fee2e2" />
        <line x1="14" y1="11" x2="14" y2="17" stroke="#fee2e2" />
    </svg>
);

export const IconPhoto = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-indigo-400 ${className}`} {...props}>
        <defs>
            <linearGradient id="photo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#818cf8" />
                <stop offset="100%" stopColor="#6366f1" />
            </linearGradient>
        </defs>
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" fill="rgba(99,102,241,0.15)" stroke="url(#photo-grad)" />
        <circle cx="8.5" cy="8.5" r="1.5" fill="url(#photo-grad)" stroke="none" />
        <polyline points="21 15 16 10 5 21" stroke="url(#photo-grad)" strokeWidth="2.5" />
    </svg>
);

export const IconStrategy = ({ type, className = '', ...props }) => {
    const iconProps = { ...defaultProps, className, ...props };
    switch (type) {
        case 'cooperate':
            return (
                <svg {...iconProps} className={`text-green-400 ${className}`}>
                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" stroke="#4ade80" strokeWidth="2.5" />
                </svg>
            );
        case 'defect':
            return (
                <svg {...iconProps} className={`text-red-400 ${className}`}>
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" fill="rgba(248,113,113,0.3)" stroke="#f87171" strokeWidth="2" />
                </svg>
            );
        case 'withdraw':
            return (
                <svg {...iconProps} className={`text-gray-400 ${className}`}>
                    <circle cx="12" cy="12" r="10" stroke="#9ca3af" strokeWidth="2" fill="rgba(156,163,175,0.1)" />
                    <path d="M4.93 4.93l14.14 14.14" stroke="#9ca3af" strokeWidth="2" />
                </svg>
            );
        default:
            return null;
    }
};

export const IconGiftQuest = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-amber-300 ${className}`} {...props}>
        <defs>
            <linearGradient id="gift-quest-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#fde047" />
                <stop offset="100%" stopColor="#f97316" />
            </linearGradient>
        </defs>
        <rect x="3" y="9" width="18" height="12" rx="2" fill="rgba(253,224,71,0.15)" stroke="url(#gift-quest-grad)" />
        <path d="M12 9v12M3 13h18" stroke="url(#gift-quest-grad)" strokeWidth="2.2" />
        <path d="M12 9s-3.2-1.2-3.2-3A1.8 1.8 0 0 1 12 6m0 3s3.2-1.2 3.2-3A1.8 1.8 0 0 0 12 6" stroke="url(#gift-quest-grad)" />
        <path d="M18.5 3.5l.6 1.2 1.3.2-.9.9.2 1.3-1.2-.6-1.2.6.2-1.3-.9-.9 1.3-.2z" fill="#fff3bf" stroke="none" />
    </svg>
);

export const IconTicketPass = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-yellow-300 ${className}`} {...props}>
        <defs>
            <linearGradient id="ticket-pass-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#facc15" />
                <stop offset="100%" stopColor="#f59e0b" />
            </linearGradient>
        </defs>
        <path d="M3 9a2 2 0 0 0 2-2h14a2 2 0 0 0 2 2v2a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2H5a2 2 0 0 0-2-2v-2a2 2 0 0 0 2-2z" fill="rgba(250,204,21,0.12)" stroke="url(#ticket-pass-grad)" />
        <path d="M12 7v10" stroke="url(#ticket-pass-grad)" strokeDasharray="2 2" />
        <circle cx="9" cy="12" r="1" fill="#fef3c7" stroke="none" />
        <circle cx="15" cy="12" r="1" fill="#fef3c7" stroke="none" />
    </svg>
);

export const IconSparkBoost = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-violet-300 ${className}`} {...props}>
        <defs>
            <linearGradient id="spark-boost-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f0abfc" />
                <stop offset="100%" stopColor="#a78bfa" />
            </linearGradient>
        </defs>
        <path d="M12 2l2.3 5.2L20 9l-4.2 3.4L17 18l-5-3-5 3 1.2-5.6L4 9l5.7-1.8z" fill="rgba(167,139,250,0.18)" stroke="url(#spark-boost-grad)" />
        <circle cx="12" cy="10" r="1.5" fill="#faf5ff" stroke="none" />
    </svg>
);

export const IconPixPortal = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-cyan-300 ${className}`} {...props}>
        <defs>
            <linearGradient id="pix-portal-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#67e8f9" />
                <stop offset="100%" stopColor="#06b6d4" />
            </linearGradient>
        </defs>
        <rect x="6" y="2.5" width="12" height="19" rx="2.2" fill="rgba(34,211,238,0.14)" stroke="url(#pix-portal-grad)" />
        <rect x="8.3" y="6" width="7.4" height="7.4" rx="1" stroke="url(#pix-portal-grad)" />
        <path d="M10 8h1.8M12.8 8h1.2M10 10.6h3.9M10 12.5h1.6" stroke="url(#pix-portal-grad)" strokeWidth="1.6" />
        <circle cx="12" cy="18" r="1" fill="#ecfeff" stroke="none" />
    </svg>
);

export const IconCheckShield = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-emerald-300 ${className}`} {...props}>
        <defs>
            <linearGradient id="check-shield-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#6ee7b7" />
                <stop offset="100%" stopColor="#10b981" />
            </linearGradient>
        </defs>
        <path d="M12 3l7 3v6c0 4.8-3.3 7.9-7 9-3.7-1.1-7-4.2-7-9V6l7-3z" fill="rgba(16,185,129,0.15)" stroke="url(#check-shield-grad)" />
        <path d="M8.8 12.2l2.2 2.2 4.2-4.4" stroke="url(#check-shield-grad)" strokeWidth="2.4" />
    </svg>
);

export const IconCopyRunes = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-slate-200 ${className}`} {...props}>
        <rect x="9" y="9" width="10" height="10" rx="2" fill="rgba(148,163,184,0.15)" stroke="currentColor" />
        <rect x="5" y="5" width="10" height="10" rx="2" fill="none" stroke="currentColor" opacity="0.8" />
        <path d="M8 10h4M8 13h4" stroke="currentColor" strokeWidth="1.7" opacity="0.8" />
    </svg>
);

export const IconWatermarkOff = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-rose-300 ${className}`} {...props}>
        <path d="M2 12s4-6 10-6 10 6 10 6-4 6-10 6-10-6-10-6z" fill="rgba(251,113,133,0.1)" stroke="currentColor" />
        <circle cx="12" cy="12" r="2.8" fill="none" stroke="currentColor" />
        <path d="M4 4l16 16" stroke="currentColor" strokeWidth="2.3" />
    </svg>
);

export const IconShareRocket = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-sky-300 ${className}`} {...props}>
        <path d="M5 19c1.2-3.5 2.8-5.5 6.3-6.8L17 6l1 6-6.1 5.8-2-1.8L8 18z" fill="rgba(56,189,248,0.16)" stroke="currentColor" />
        <path d="M12 12l6-6M14.5 5.5h4v4" stroke="currentColor" strokeWidth="2.2" />
    </svg>
);

export const IconFolderLoot = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-amber-200 ${className}`} {...props}>
        <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" fill="rgba(251,191,36,0.16)" stroke="currentColor" />
        <path d="M12 10v5M9.5 12.5H14.5" stroke="currentColor" strokeWidth="2.2" />
    </svg>
);

export const IconCameraShot = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-indigo-200 ${className}`} {...props}>
        <path d="M4 8h3l1.2-2h7.6L17 8h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2z" fill="rgba(129,140,248,0.16)" stroke="currentColor" />
        <circle cx="12" cy="13" r="3.2" fill="none" stroke="currentColor" strokeWidth="2.2" />
        <circle cx="18" cy="10" r="1" fill="currentColor" stroke="none" />
    </svg>
);

export const IconDownloadDrop = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-white ${className}`} {...props}>
        <path d="M12 4v10" stroke="currentColor" strokeWidth="2.4" />
        <path d="M8 10l4 4 4-4" stroke="currentColor" strokeWidth="2.4" />
        <rect x="4" y="17" width="16" height="3" rx="1.5" fill="rgba(255,255,255,0.2)" stroke="currentColor" />
    </svg>
);

export const IconWhatsappQuest = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-emerald-200 ${className}`} {...props}>
        <path d="M4 20l1.4-4A8 8 0 1 1 20 12a8 8 0 0 1-11.9 7z" fill="rgba(37,211,102,0.18)" stroke="currentColor" />
        <path d="M10 9.8c.6 1.4 1.8 2.5 3.2 3.1" stroke="currentColor" strokeWidth="2.2" />
        <path d="M13.2 8.8l1.8 1.8-2.2 2.2-1.8-1.8z" fill="none" stroke="currentColor" strokeWidth="1.6" />
    </svg>
);

export const IconInstagramOrb = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-pink-200 ${className}`} {...props}>
        <rect x="4" y="4" width="16" height="16" rx="5" fill="rgba(236,72,153,0.15)" stroke="currentColor" />
        <circle cx="12" cy="12" r="3.5" fill="none" stroke="currentColor" strokeWidth="2.2" />
        <circle cx="16.5" cy="7.5" r="1" fill="currentColor" stroke="none" />
    </svg>
);

export const IconResetCycle = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-slate-500 ${className}`} {...props}>
        <path d="M20 6v5h-5" stroke="currentColor" strokeWidth="2.2" />
        <path d="M4 18v-5h5" stroke="currentColor" strokeWidth="2.2" />
        <path d="M19 11a7 7 0 0 0-12-3M5 13a7 7 0 0 0 12 3" stroke="currentColor" />
    </svg>
);

export const IconUserBadge = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-sky-200 ${className}`} {...props}>
        <circle cx="12" cy="8" r="3.5" fill="rgba(125,211,252,0.22)" stroke="currentColor" />
        <path d="M5 20a7 7 0 0 1 14 0" fill="none" stroke="currentColor" strokeWidth="2.2" />
        <path d="M18.5 5.5l.4.9.9.1-.7.6.2.9-.8-.4-.8.4.2-.9-.7-.6.9-.1z" fill="currentColor" stroke="none" />
    </svg>
);

export const IconEditPen = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-violet-300 ${className}`} {...props}>
        <path d="M4 20l4.2-1 9.6-9.6-3.2-3.2L5 15.8 4 20z" fill="rgba(167,139,250,0.16)" stroke="currentColor" />
        <path d="M13.8 6.2l3.2 3.2 1.6-1.6a1.4 1.4 0 0 0 0-2l-1.2-1.2a1.4 1.4 0 0 0-2 0z" fill="none" stroke="currentColor" />
    </svg>
);

export const IconDeckCard = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-fuchsia-200 ${className}`} {...props}>
        <rect x="6" y="5" width="12" height="15" rx="2" fill="rgba(217,70,239,0.14)" stroke="currentColor" />
        <rect x="3" y="8" width="12" height="13" rx="2" fill="none" stroke="currentColor" opacity="0.75" />
        <path d="M12 9l1.2 2.5L16 12l-2 1.8.5 2.7L12 15l-2.5 1.5.5-2.7L8 12l2.8-.5z" fill="currentColor" stroke="none" opacity="0.85" />
    </svg>
);

export const IconCutBlade = ({ className = '', ...props }) => (
    <svg {...defaultProps} className={`text-cyan-200 ${className}`} {...props}>
        <circle cx="7" cy="8" r="2.5" fill="rgba(125,211,252,0.18)" stroke="currentColor" />
        <circle cx="7" cy="16" r="2.5" fill="rgba(125,211,252,0.18)" stroke="currentColor" />
        <path d="M9 9.5L20 4M9 14.5L20 20" stroke="currentColor" strokeWidth="2" />
        <path d="M11.5 12h9" stroke="currentColor" strokeWidth="1.8" opacity="0.8" />
    </svg>
);
