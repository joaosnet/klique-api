import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../../services/api';
import './RegisterForm.css';
import { getErrorMessage } from '../../utils/errorHandler';
import { IconGiftQuest } from '../Icons/ActionIcons';

export default function RegisterForm() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError('As senhas não coincidem');
            return;
        }

        if (password.length < 6) {
            setError('A senha deve ter no mínimo 6 caracteres');
            return;
        }

        setLoading(true);

        try {
            await authAPI.register(name, email, password);
            navigate('/login', {
                state: { message: 'Conta criada! Faça login para continuar.' }
            });
        } catch (err) {
            setError(
                getErrorMessage(err, 'Erro ao criar conta. Tente novamente.')
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
                    <h1>Criar Conta</h1>
                    <p>Ganhe 1 crédito grátis ao se cadastrar!</p>
                </div>

                {error && (
                    <div className="error-message">
                        <span>⚠️</span> {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="register-form">
                    <div className="form-group">
                        <label htmlFor="name">Nome</label>
                        <input
                            type="text"
                            id="name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="Seu nome"
                            required
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="seu@email.com"
                            required
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Senha</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            required
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="confirmPassword">Confirmar Senha</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            placeholder="••••••••"
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
                                Criando conta...
                            </>
                        ) : (
                            <>
                                <IconGiftQuest width={20} height={20} />
                                Criar Conta Grátis
                            </>
                        )}
                    </button>
                </form>

                <div className="register-footer">
                    <p>
                        Já tem uma conta?{' '}
                        <Link to="/login">Fazer login</Link>
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
