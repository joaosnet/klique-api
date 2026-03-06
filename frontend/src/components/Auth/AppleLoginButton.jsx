import React, { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { IconApple } from '../Icons/AuthIcons';
import { getErrorMessage } from '../../utils/errorHandler';
import { isNativePlatform, appleSignInWeb, appleSignInNative, isAppleAuthValid } from '../../utils/socialAuth';

function WebAppleLoginButton({ setLoading, setError, isRegister = false }) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { loginWithApple } = useAuth();
    const prefix = isRegister ? 'register' : 'login';

    const handleWeb = useCallback(async () => {
        setError('');
        setLoading(true);
        try {
            const { idToken, name } = await appleSignInWeb();
            await loginWithApple(idToken, name);
            navigate('/dominios');
        } catch (err) {
            if (err?.message?.includes('popup') || err?.code === 'SIGN_IN_CANCELED') {
                setLoading(false);
                return;
            }
            setError(getErrorMessage(err, t(`${prefix}.error_apple`)));
        } finally {
            setLoading(false);
        }
    }, [loginWithApple, navigate, setError, setLoading, t, prefix]);

    return (
        <button
            type="button"
            onClick={handleWeb}
            className="flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-semibold text-[var(--text-main)] transition-all hover:bg-[var(--bg-card-inner)]"
            style={{
                border: '1px solid var(--border-color)',
                background: 'transparent',
            }}
        >
            <IconApple className="w-4 h-4" />
            {t(`${prefix}.apple`)}
        </button>
    );
}

function NativeAppleLoginButton({ setLoading, setError, isRegister = false }) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { loginWithApple } = useAuth();
    const prefix = isRegister ? 'register' : 'login';

    const handleNative = useCallback(async () => {
        setError('');
        setLoading(true);
        try {
            const { idToken, name } = await appleSignInNative();
            await loginWithApple(idToken, name);
            navigate('/dominios');
        } catch (err) {
            if (err?.message?.includes('popup') || err?.code === 'SIGN_IN_CANCELED') {
                setLoading(false);
                return;
            }
            setError(getErrorMessage(err, t(`${prefix}.error_apple`)));
            setLoading(false);
        }
    }, [loginWithApple, navigate, setError, setLoading, t, prefix]);

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
            <IconApple className="w-4 h-4" />
            {t(`${prefix}.apple`)}
        </button>
    );
}

export default function AppleLoginButton({ setLoading, setError, isRegister = false }) {
    if (isNativePlatform()) {
        return <NativeAppleLoginButton setLoading={setLoading} setError={setError} isRegister={isRegister} />;
    }

    if (!isAppleAuthValid()) {
        return null;
    }

    return <WebAppleLoginButton setLoading={setLoading} setError={setError} isRegister={isRegister} />;
}
