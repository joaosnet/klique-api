import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../../services/api';
import './RegisterForm.css';
import { getErrorMessage } from '../../utils/errorHandler';
import { IconGiftQuest } from '../Icons/ActionIcons';

import { useTranslation } from 'react-i18next';

export default function RegisterForm() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();
    const { t } = useTranslation();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError(t('registerForm.error_password_match', 'As senhas não coincidem'));
            return;
        }

        if (password.length < 6) {
            setError(t('registerForm.error_password_length', 'A senha deve ter no mínimo 6 caracteres'));
            return;
        }

        setLoading(true);

        try {
            await authAPI.register(name, email, password);
            navigate('/login', {
                state: { message: t('registerForm.success', 'Conta criada! Faça login para continuar.') }
            });
        } catch (err) {
            setError(
                getErrorMessage(err, t('registerForm.error_create', 'Erro ao criar conta. Tente novamente.'))
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="register-container">
            <div className="register-card">
                <div className="register-header">
                    <IconGiftQuest className="register-icon" width={58} height={58} />
                    <h1>{t('registerForm.title')}</h1>
                    <p>{t('registerForm.subtitle')}</p>
                </div>

                {error && (
                    <div className="error-message">
                        <span>⚠️</span> {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="register-form">
                    <div className="form-group">
                        <label htmlFor="name">{t('registerForm.full_name')}</label>
                        <input
                            type="text"
                            id="name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder={t('registerForm.full_name_placeholder')}
                            required
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">{t('registerForm.email')}</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder={t('registerForm.email_placeholder')}
                            required
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">{t('registerForm.password')}</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder={t('registerForm.password_placeholder')}
                            required
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="confirmPassword">{t('registerForm.confirm_password')}</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            placeholder={t('registerForm.confirm_password_placeholder')}
                            required
                            disabled={loading}
                        />
                    </div>

                    <button
                        type="submit"
                        className="btn-submit"
                        disabled={loading}
                    >
                        {loading ? (
                            <>
                                <span className="spinner"></span>
                                {t('registerForm.loading')}
                            </>
                        ) : (
                            <>
                                <IconGiftQuest width={20} height={20} />
                                {t('registerForm.submit')}
                            </>
                        )}
                    </button>
                </form>

                <div className="register-footer">
                    <p>
                        {t('registerForm.has_account')}{' '}
                        <Link to="/login">{t('registerForm.login_link')}</Link>
                    </p>
                </div>
            </div>

            {/* Snowflakes */}
            <div className="snowflakes" aria-hidden="true">
                {[...Array(10)].map((_, i) => (
                    <div key={i} className="snowflake">
                        {['❄', '❅', '❆'][i % 3]}
                    </div>
                ))}
            </div>
        </div>
    );
}
