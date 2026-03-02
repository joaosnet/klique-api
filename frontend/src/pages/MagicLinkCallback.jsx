import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';

export default function MagicLinkCallback() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const { loginWithMagicLink } = useAuth();
    const navigate = useNavigate();
    const { t } = useTranslation();
    const [status, setStatus] = useState(t('magicLink.verifying'));

    useEffect(() => {
        if (!token) {
            // eslint-disable-next-line react-hooks/set-state-in-effect
            setStatus(t('magicLink.tokenNotFound'));
            return;
        }

        const verifyToken = async () => {
            try {
                await loginWithMagicLink(token);
                navigate('/');
            } catch {
                setStatus(t('magicLink.invalidOrExpired'));
            }
        };

        verifyToken();
    }, [token, loginWithMagicLink, navigate, t]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-900 px-4">
            <div className="max-w-md w-full text-center space-y-4 rounded-xl p-8" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.2)' }}>
                <h1 className="font-title text-xl text-white tracking-widest uppercase">{t('magicLink.title')}</h1>
                <p className="text-gray-400 text-sm">{status}</p>
                {status !== t('magicLink.verifying') && (
                    <button
                        onClick={() => navigate('/login')}
                        className="mt-6 py-2 px-6 rounded-lg text-xs font-semibold uppercase tracking-widest text-white hover:opacity-90 transition-opacity"
                        style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)' }}
                    >
                        {t('magicLink.backToLogin')}
                    </button>
                )}
            </div>
        </div>
    );
}
