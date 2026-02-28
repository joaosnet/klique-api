import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';
import { getErrorMessage } from '../utils/errorHandler';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [method, setMethod] = useState('password'); // 'password', 'otp', 'magic', 'social'
  const [otpSent, setOtpSent] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, loginWithGoogle, loginWithApple, loginWithOTP, loginWithMagicLink, lazyRegister, loginWithPasskey } = useAuth();
  const navigate = useNavigate();

  const handlePasskeyLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await loginWithPasskey(email);
      navigate('/dominios');
    } catch (err) {
      setError(getErrorMessage(err, 'Erro na autenticação por passkey.'));
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dominios');
    } catch (err) {
      setError(getErrorMessage(err, 'Email ou senha incorretos.'));
    } finally {
      setLoading(false);
    }
  };

  const handleOTPRequest = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authAPI.requestOTP(phone);
      setOtpSent(true);
    } catch (err) {
      setError(getErrorMessage(err, 'Erro ao enviar código. Verifique o número.'));
    } finally {
      setLoading(false);
    }
  };

  const handleOTPVerify = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await loginWithOTP(phone, otp);
      navigate('/dominios');
    } catch (err) {
      setError(getErrorMessage(err, 'Código inválido ou expirado.'));
    } finally {
      setLoading(false);
    }
  };

  const handleMagicLinkRequest = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authAPI.requestMagicLink(email);
      alert('Link enviado! Verifique seu e-mail.');
    } catch (err) {
      setError(getErrorMessage(err, 'Erro ao enviar link.'));
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    // This should open Google One Tap or a popup
    // For now, mock a successful token
    setError('');
    setLoading(true);
    try {
      // Mock token for demo
      // await loginWithGoogle("google-token");
      alert("Google Login placeholder");
    } catch (err) {
      setError(getErrorMessage(err, "Erro no login com Google"));
    } finally {
      setLoading(false);
    }
  };

  const handleLazyRegister = async () => {
    setLoading(true);
    try {
      await lazyRegister();
      navigate('/dominios');
    } catch (err) {
      setError(getErrorMessage(err, "Erro ao iniciar sessão convidado"));
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    background: 'var(--bg-card-inner)',
    border: '1px solid var(--border-color)',
    color: 'var(--text-main)',
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4 py-12"
      style={{ background: 'var(--bg-app)', transition: 'background-color 0.3s ease' }}
    >
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="font-title text-2xl tracking-widest text-purple-400">
            GAME THEORY
          </Link>
          <p className="text-[var(--text-muted)] text-xs uppercase tracking-widest mt-1">
            Teoria dos Jogos · Geopolítica
          </p>
        </div>

        {/* Card */}
        <div
          className="rounded-2xl p-8 transition-colors duration-300"
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          }}
        >
          <h1 className="font-title text-2xl tracking-wider text-[var(--text-main)] mb-1 uppercase">
            {method === 'otp' ? 'WhatsApp' : method === 'magic' ? 'Magic Link' : 'Entrar'}
          </h1>
          <p className="text-[var(--text-muted)] text-sm mb-6">Escolha como deseja acessar sua conta.</p>

          {error && (
            <div
              className="rounded-lg px-4 py-3 mb-5 text-sm bg-red-500/10 border border-red-500/30 text-red-400"
            >
              {error}
            </div>
          )}

          {/* Social Buttons */}
          <div className="grid grid-cols-2 gap-3 mb-6">
            <button
              type="button"
              onClick={handleGoogleLogin}
              className="flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-semibold text-[var(--text-main)] transition-all hover:bg-[var(--bg-card-inner)]"
              style={{ border: '1px solid var(--border-color)' }}
            >
              <img src="https://www.google.com/favicon.ico" className="w-4 h-4" alt="Google" />
              Google
            </button>
            <button
              type="button"
              className="flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-semibold text-[var(--text-main)] transition-all hover:bg-[var(--bg-card-inner)]"
              style={{ border: '1px solid var(--border-color)' }}
            >
              <span className="text-lg"></span>
              Apple
            </button>
          </div>

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-[var(--border-color)]"></div></div>
            <div className="relative flex justify-center text-xs uppercase"><span className="bg-[var(--bg-card)] px-2 text-[var(--text-muted)] tracking-tighter">ou continue com</span></div>
          </div>

          {method === 'password' && (
            <form onSubmit={handlePasswordLogin} className="space-y-4">
              <div>
                <label className="block text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-1.5 ml-1">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="seu@email.com"
                  required
                  className="w-full rounded-lg px-4 py-3 text-sm placeholder-[var(--text-muted)/50] outline-none focus:ring-1 ring-purple-500"
                  style={inputStyle}
                />
              </div>
              <div>
                <label className="block text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-1.5 ml-1">Senha</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full rounded-lg px-4 py-3 text-sm placeholder-[var(--text-muted)/50] outline-none focus:ring-1 ring-purple-500"
                  style={inputStyle}
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-lg font-title tracking-widest text-sm uppercase text-white transition-all hover:opacity-90 disabled:opacity-50"
                style={{ background: 'linear-gradient(135deg, #7c3aed, #a855f7)' }}
              >
                {loading ? 'Aguarde...' : 'Entrar'}
              </button>
            </form>
          )}

          {method === 'otp' && (
            <form onSubmit={otpSent ? handleOTPVerify : handleOTPRequest} className="space-y-4">
              <div>
                <label className="block text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-1.5 ml-1">Telefone (WhatsApp)</label>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="5511999999999"
                  required
                  disabled={otpSent}
                  className="w-full rounded-lg px-4 py-3 text-sm placeholder-[var(--text-muted)/50] outline-none focus:ring-1 ring-purple-500"
                  style={inputStyle}
                />
              </div>
              {otpSent && (
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-1.5 ml-1">Código</label>
                  <input
                    type="text"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    placeholder="123456"
                    required
                    maxLength={6}
                    className="w-full rounded-lg px-4 py-3 text-sm text-center text-xl font-bold tracking-widest outline-none focus:ring-1 ring-purple-500"
                    style={inputStyle}
                  />
                </div>
              )}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-lg font-title tracking-widest text-sm uppercase text-white transition-all hover:opacity-90 disabled:opacity-50"
                style={{ background: 'linear-gradient(135deg, #22c55e, #16a34a)' }}
              >
                {loading ? 'Aguarde...' : otpSent ? 'Verificar Código' : 'Receber via WhatsApp'}
              </button>
              {otpSent && <button type="button" onClick={() => setOtpSent(false)} className="w-full text-xs text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors">Alterar número</button>}
            </form>
          )}

          {method === 'magic' && (
            <form onSubmit={handleMagicLinkRequest} className="space-y-4">
              <div>
                <label className="block text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-1.5 ml-1">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="seu@email.com"
                  required
                  className="w-full rounded-lg px-4 py-3 text-sm placeholder-[var(--text-muted)/50] outline-none focus:ring-1 ring-purple-500"
                  style={inputStyle}
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-lg font-title tracking-widest text-sm uppercase text-white transition-all hover:opacity-90 disabled:opacity-50"
                style={{ background: 'linear-gradient(135deg, #3b82f6, #2563eb)' }}
              >
                {loading ? 'Enviando...' : 'Enviar Link Mágico'}
              </button>
            </form>
          )}

          {method === 'passkey' && (
            <form onSubmit={handlePasskeyLogin} className="space-y-4">
              <div>
                <label className="block text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-1.5 ml-1">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="seu@email.com"
                  required
                  className="w-full rounded-lg px-4 py-3 text-sm placeholder-[var(--text-muted)/50] outline-none focus:ring-1 ring-purple-500"
                  style={inputStyle}
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-lg font-title tracking-widest text-sm uppercase text-white transition-all hover:opacity-90 disabled:opacity-50"
                style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}
              >
                {loading ? 'Aguarde...' : 'Entrar com Passkey'}
              </button>
            </form>
          )}

          {/* Alternative Methods */}
          <div className="mt-8 flex flex-wrap justify-center gap-4 border-t border-[var(--border-color)] pt-6">
            <button onClick={() => setMethod('password')} className={`text-[10px] uppercase tracking-widest transition-colors ${method === 'password' ? 'text-purple-400' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}`}>Senha</button>
            <button onClick={() => setMethod('otp')} className={`text-[10px] uppercase tracking-widest transition-colors ${method === 'otp' ? 'text-green-400' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}`}>WhatsApp</button>
            <button onClick={() => setMethod('magic')} className={`text-[10px] uppercase tracking-widest transition-colors ${method === 'magic' ? 'text-blue-400' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}`}>E-mail</button>
            <button onClick={() => setMethod('passkey')} className={`text-[10px] uppercase tracking-widest transition-colors ${method === 'passkey' ? 'text-orange-400' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}`}>Passkey</button>
          </div>

          <button
            onClick={handleLazyRegister}
            className="w-full mt-6 py-2 rounded-lg text-[10px] uppercase tracking-widest text-[var(--text-muted)] hover:text-[var(--text-main)] transition-all hover:bg-[var(--bg-card-inner)]"
            style={{ border: '1px dashed var(--border-color)' }}
          >
            Iniciar sem cadastro (Progresso temporário)
          </button>

          <p className="text-center text-sm text-[var(--text-muted)] mt-6">
            Não tem conta?{' '}
            <Link to="/register" className="text-purple-400 hover:text-purple-300 transition-colors">
              Cadastre-se
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
