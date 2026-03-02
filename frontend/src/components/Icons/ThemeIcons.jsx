import React from 'react';

const defaultProps = {
    width: 48,
    height: 48,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.5,
    strokeLinecap: "round",
    strokeLinejoin: "round"
};

// Componente genérico que adapta os svgs de acordo com o tema
export const ThemeIcon = ({ theme, className = '', color, gradientId, ...props }) => {
    const gId = gradientId || `theme-grad-${theme}`;

    const iconProps = {
        ...defaultProps,
        className,
        stroke: color || `url(#${gId})`,
        ...props
    };

    const gradientDef = (
        <defs>
            <linearGradient id={gId} x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor={color || "#c4b5fd"} />
                <stop offset="100%" stopColor="#000" stopOpacity="0.5" />
            </linearGradient>
            <filter id={`${gId}-glow`} x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="2" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
        </defs>
    );

    switch (theme?.toLowerCase()) {
        case 'dating':
        case 'amor':
            return (
                <svg {...iconProps}>
                    {gradientDef}
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" fill={`url(#${gId})`} fillOpacity="0.2" filter={`url(#${gId}-glow)`} />
                    <path d="M12 9v2M12 15h.01" stroke="#fff" strokeWidth="2" strokeOpacity="0.7" />
                </svg>
            );
        case 'office':
        case 'escritório':
            return (
                <svg {...iconProps}>
                    {gradientDef}
                    <rect x="4" y="2" width="16" height="20" rx="2" ry="2" fill={`url(#${gId})`} fillOpacity="0.1" />
                    <path d="M9 22v-4h6v4M8 6h.01M16 6h.01M12 6h.01M12 10h.01M16 10h.01M8 10h.01M12 14h.01M8 14h.01M16 14h.01" strokeWidth="2" filter={`url(#${gId}-glow)`} />
                </svg>
            );
        case 'finance':
        case 'finanças':
            return (
                <svg {...iconProps}>
                    {gradientDef}
                    <circle cx="12" cy="12" r="10" fill={`url(#${gId})`} fillOpacity="0.1" />
                    <path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8M12 18V6" strokeWidth="2" filter={`url(#${gId}-glow)`} />
                </svg>
            );
        case 'negotiation':
        case 'negociação':
            return (
                <svg {...iconProps}>
                    {gradientDef}
                    <path d="M12 3v18M5 8v2a7 7 0 0 0 14 0V8M5 13H2M22 13h-3" filter={`url(#${gId}-glow)`} />
                    <circle cx="5" cy="8" r="2" fill={`url(#${gId})`} fillOpacity="0.4" />
                    <circle cx="19" cy="8" r="2" fill={`url(#${gId})`} fillOpacity="0.4" />
                </svg>
            );
        case 'geopolitics':
        case 'geopolítica':
            return (
                <svg {...iconProps}>
                    {gradientDef}
                    <circle cx="12" cy="12" r="10" fill={`url(#${gId})`} fillOpacity="0.1" />
                    <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" filter={`url(#${gId}-glow)`} />
                </svg>
            );
        case 'social':
            return (
                <svg {...iconProps}>
                    {gradientDef}
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" fill={`url(#${gId})`} fillOpacity="0.1" />
                    <circle cx="9" cy="7" r="4" filter={`url(#${gId}-glow)`} />
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
            );
        default:
            // Custom / Game Theory Hexagon
            return (
                <svg {...iconProps}>
                    {gradientDef}
                    <path d="M12 2l8.66 5v10L12 22l-8.66-5V7L12 2z" fill={`url(#${gId})`} fillOpacity="0.1" filter={`url(#${gId}-glow)`} />
                    <circle cx="12" cy="12" r="3" fill={`url(#${gId})`} />
                </svg>
            );
    }
};

export const CustomSymbolTemplate = ({ type, color = "#fff", ...props }) => {
    const innerProps = { width: 32, height: 32, viewBox: "0 0 24 24", fill: "none", stroke: color, strokeWidth: 2, strokeLinecap: "round", strokeLinejoin: "round", ...props };

    switch (type) {
        case 'if_then':
            return (
                <svg {...innerProps}>
                    <path d="M21 8L12 16 3 8" strokeWidth="2.5" />
                    <path d="M12 2v14" opacity="0.5" />
                </svg>
            );
        case 'payoff_matrix':
            return (
                <svg {...innerProps}>
                    <rect x="3" y="3" width="18" height="18" rx="2" opacity="0.3" />
                    <path d="M3 12h18M12 3v18" strokeWidth="2" />
                    <circle cx="8" cy="8" r="1.5" fill={color} stroke="none" />
                    <circle cx="16" cy="16" r="1.5" fill={color} stroke="none" />
                </svg>
            );
        case 'black_swan':
            return (
                <svg {...innerProps}>
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" opacity="0.2" fill={color} stroke="none" />
                    <path d="M12 4v16M4 12h16" opacity="0.5" />
                    <path d="M8 8l8 8M16 8l-8 8" strokeWidth="2.5" />
                </svg>
            );
        default:
            return <ThemeIcon theme="custom" color={color} {...innerProps} />;
    }
};
