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
