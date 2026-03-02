import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';
import { getErrorMessage } from '../utils/errorHandler';
import { IconPasswordLock, IconWhatsApp, IconEmailMagic, IconPasskeyBadge, IconGoogle, IconApple } from '../components/Icons/AuthIcons';

export default function LoginPage() {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [method, setMethod] = useState('password'); // 'password', 'otp', 'magic', 'social'
  const [otpSent, setOtpSent] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, loginWithOTP, lazyRegister, loginWithPasskey } = useAuth();
  const navigate = useNavigate();

  const handlePasskeyLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await loginWithPasskey(email);
      navigate('/dominios');
    } catch (err) {
      setError(getErrorMessage(err, t('login.error_credentials')));
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
      setError(getErrorMessage(err, t('login.error_credentials')));
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
      setError(getErrorMessage(err, t('login.error_otp_send')));
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
      setError(getErrorMessage(err, t('login.error_otp_verify')));
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
      setError(getErrorMessage(err, t('login.error_magic_link')));
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
      alert(t('login.google_placeholder'));
    } catch (err) {
      setError(getErrorMessage(err, t('login.error_google')));
    } finally {
      setLoading(false);
    }
  };

  const handleAppleLogin = async () => {
    setError('');
    setLoading(true);
    try {
      alert(t('login.apple_placeholder'));
    } catch (err) {
      setError(getErrorMessage(err, t('login.error_apple')));
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
      setError(getErrorMessage(err, t('login.error_guest')));
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
            {t('login.omniflash')}
          </Link>
          <p className="text-[var(--text-muted)] text-xs uppercase tracking-widest mt-1">
            {t('login.subtitle')}
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
            {method === 'otp' ? t('login.whatsapp') : method === 'magic' ? t('login.magic_link') : t('login.sign_in')}
          </h1>
          <p className="text-[var(--text-muted)] text-sm mb-6">{t('login.choose_method')}</p>

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
              <IconGoogle className="w-4 h-4" />
              {t('login.google')}
            </button>
            <button
              type="button"
              onClick={handleAppleLogin}
              className="flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-semibold text-[var(--text-main)] transition-all hover:bg-[var(--bg-card-inner)]"
              style={{ border: '1px solid var(--border-color)' }}
            >
              <IconApple className="w-4 h-4" />
              {t('login.apple')}
            </button>
          </div>

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-[var(--border-color)]"></div></div>
            <div className="relative flex justify-center text-xs uppercase"><span className="bg-[var(--bg-card)] px-2 text-[var(--text-muted)] tracking-tighter">{t('login.or_continue_with')}</span></div>
          </div>

          {method === 'password' && (
            <form onSubmit={handlePasswordLogin} className="space-y-4">
              <div>
                <label className="block text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-1.5 ml-1">{t('login.email')}</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={t('login.email_placeholder')}
                  required
                  className="w-full rounded-lg px-4 py-3 text-sm placeholder-[var(--text-muted)/50] outline-none focus:ring-1 ring-purple-500"
                  style={inputStyle}
                />
              </div>
              <div>
                <label className="block text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-1.5 ml-1">{t('login.password')}</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={t('login.password_placeholder')}
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
                {loading ? t('login.signing_in') : t('login.sign_in')}
              </button>
            </form>
          )}

          {method === 'otp' && (
            <form onSubmit={otpSent ? handleOTPVerify : handleOTPRequest} className="space-y-4">
              <div>
                <label className="block text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-1.5 ml-1">{t('login.phone_whatsapp')}</label>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder={t('login.phone_placeholder')}
                  required
                  disabled={otpSent}
                  className="w-full rounded-lg px-4 py-3 text-sm placeholder-[var(--text-muted)/50] outline-none focus:ring-1 ring-purple-500"
                  style={inputStyle}
                />
              </div>
              {otpSent && (
                <div>
                  <label className="block text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-1.5 ml-1">{t('login.code')}</label>
                  <input
                    type="text"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    placeholder={t('login.code_placeholder')}
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
                {loading ? t('login.signing_in') : otpSent ? t('login.verify_code') : t('login.receive_via_whatsapp')}
              </button>
              {otpSent && <button type="button" onClick={() => setOtpSent(false)} className="w-full text-xs text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors">{t('login.change_number')}</button>}
            </form>
          )}

          {method === 'magic' && (
            <form onSubmit={handleMagicLinkRequest} className="space-y-4">
              <div>
                <label className="block text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-1.5 ml-1">{t('login.email')}</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={t('login.email_placeholder')}
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
                {loading ? t('login.sending') : t('login.send_magic_link')}
              </button>
            </form>
          )}

          {method === 'passkey' && (
            <form onSubmit={handlePasskeyLogin} className="space-y-4">
              <div>
                <label className="block text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-1.5 ml-1">{t('login.email')}</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={t('login.email_placeholder')}
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
                {loading ? t('login.signing_in') : t('login.sign_in_passkey')}
              </button>
            </form>
          )}

          {/* Alternative Methods */}
          <div className="mt-8 flex flex-wrap justify-center gap-4 border-t border-[var(--border-color)] pt-6">
            <button onClick={() => setMethod('password')} className={`flex items-center gap-1.5 text-[10px] uppercase tracking-widest transition-colors ${method === 'password' ? 'text-purple-400' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}`}>
              <IconPasswordLock className="w-3.5 h-3.5" />
              {t('login.method_password')}
            </button>
            <button onClick={() => setMethod('otp')} className={`flex items-center gap-1.5 text-[10px] uppercase tracking-widest transition-colors ${method === 'otp' ? 'text-green-400' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}`}>
              <IconWhatsApp className="w-3.5 h-3.5" />
              {t('login.method_whatsapp')}
            </button>
            <button onClick={() => setMethod('magic')} className={`flex items-center gap-1.5 text-[10px] uppercase tracking-widest transition-colors ${method === 'magic' ? 'text-blue-400' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}`}>
              <IconEmailMagic className="w-3.5 h-3.5" />
              {t('login.method_email')}
            </button>
            <button onClick={() => setMethod('passkey')} className={`flex items-center gap-1.5 text-[10px] uppercase tracking-widest transition-colors ${method === 'passkey' ? 'text-orange-400' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}`}>
              <IconPasskeyBadge className="w-3.5 h-3.5" />
              {t('login.method_passkey')}
            </button>
          </div>

          <button
            onClick={handleLazyRegister}
            className="w-full mt-6 py-2 rounded-lg text-[10px] uppercase tracking-widest text-[var(--text-muted)] hover:text-[var(--text-main)] transition-all hover:bg-[var(--bg-card-inner)]"
            style={{ border: '1px dashed var(--border-color)' }}
          >
            {t('login.start_without_account')}
          </button>

          <p className="text-center text-sm text-[var(--text-muted)] mt-6">
            {t('login.no_account')}{' '}
            <Link to="/register" className="text-purple-400 hover:text-purple-300 transition-colors">
              {t('login.sign_up')}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
