import React, { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useGoogleLogin } from '@react-oauth/google';
import { useAuth } from '../../context/AuthContext';
import { IconGoogle } from '../Icons/AuthIcons';
import { getErrorMessage } from '../../utils/errorHandler';
import { isNativePlatform, googleSignInNative, isGoogleAuthValid } from '../../utils/socialAuth';

function WebGoogleLoginButton({ setLoading, setError, isRegister = false }) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { loginWithGoogle } = useAuth();
    const prefix = isRegister ? 'register' : 'login';

    const loginWithGoogleWeb = useGoogleLogin({
        flow: 'implicit',
        onSuccess: async (tokenResponse) => {
            setError('');
            setLoading(true);
            try {
                await loginWithGoogle(tokenResponse.access_token);
                navigate('/dominios');
            } catch (err) {
                setError(getErrorMessage(err, t(`${prefix}.error_google`)));
            } finally {
                setLoading(false);
            }
        },
        onError: () => setError(t(`${prefix}.error_google`)),
    });

    return (
        <button
            type="button"
            onClick={() => { setLoading(true); loginWithGoogleWeb(); }}
            className="flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-semibold text-[var(--text-main)] transition-all hover:bg-[var(--bg-card-inner)]"
            style={{
                border: '1px solid var(--border-color)',
                background: 'transparent',
            }}
        >
            <IconGoogle className="w-4 h-4" />
            {t(`${prefix}.google`)}
        </button>
    );
}

function NativeGoogleLoginButton({ setLoading, setError, isRegister = false }) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { loginWithGoogle } = useAuth();
    const prefix = isRegister ? 'register' : 'login';

    const handleNative = useCallback(async () => {
        setError('');
        setLoading(true);
        try {
            const idToken = await googleSignInNative();
            await loginWithGoogle(idToken);
            navigate('/dominios');
        } catch (err) {
            setError(getErrorMessage(err, t(`${prefix}.error_google`)));
            setLoading(false);
        }
    }, [loginWithGoogle, navigate, setError, setLoading, t, prefix]);

    return (
        <button
            type="button"
            onClick={handleNative}
            className="flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-semibold text-[var(--text-main)] transition-all hover:bg-[var(--bg-card-inner)]"
            style={{
                border: '1px solid var(--border-color)',
                background: 'transparent',
            }}
        >
            <IconGoogle className="w-4 h-4" />
            {t(`${prefix}.google`)}
        </button>
    );
}

export default function GoogleLoginButton({ setLoading, setError, isRegister = false }) {
    if (isNativePlatform()) {
        return <NativeGoogleLoginButton setLoading={setLoading} setError={setError} isRegister={isRegister} />;
    }

    if (!isGoogleAuthValid()) {
        return null;
    }

    return <WebGoogleLoginButton setLoading={setLoading} setError={setError} isRegister={isRegister} />;
}
