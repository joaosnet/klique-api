import { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { domainsAPI } from '../../services/api';

const THEMES = [
  { value: 'dating', labelKey: 'domains.theme_dating' },
  { value: 'office', labelKey: 'domains.theme_office' },
  { value: 'finance', labelKey: 'domains.theme_finance' },
  { value: 'negotiation', labelKey: 'domains.theme_negotiation' },
  { value: 'geopolitics', labelKey: 'domains.theme_geopolitics' },
  { value: 'social', labelKey: 'domains.theme_social' },
  { value: 'custom', labelKey: 'domains.theme_custom' },
];

const API_URL = import.meta.env.VITE_API_URL || '';

const inputStyle = {
  width: '100%',
  background: 'var(--bg-card-inner)',
  border: '1px solid var(--border-color)',
  color: 'var(--text-main)',
  borderRadius: 6,
  padding: '8px 10px',
  fontSize: 14,
  outline: 'none',
  boxSizing: 'border-box',
};

const labelStyle = {
  color: 'var(--text-muted)',
  fontSize: 10,
  letterSpacing: 1,
  textTransform: 'uppercase',
  display: 'block',
  marginBottom: 4,
  marginTop: 12,
};

/**
 * Modal para editar um domínio (nome, tema e imagem).
 *
 * Props:
 *   domain     - objeto Domain com id, name, theme, image_url
 *   onSave(updatedDomain) - chamado após guardar com sucesso
 *   onClose()  - chamado ao fechar
 */
export default function DomainEditModal({ domain, onSave, onClose }) {
  const { t } = useTranslation();
  const isCustomTheme = !THEMES.find(t => t.value === domain.theme || t.value === 'custom');
  const initialTheme = THEMES.find(t => t.value === domain.theme) ? domain.theme : 'custom';

  const [name, setName] = useState(domain.name || '');
  const [theme, setTheme] = useState(initialTheme);
  const [customTheme, setCustomTheme] = useState(isCustomTheme ? domain.theme : '');

  // Image section
  const [imgAction, setImgAction] = useState(null);
  const [stylePrompt, setStylePrompt] = useState('');
  const [imgLoading, setImgLoading] = useState(false);
  const [imgMsg, setImgMsg] = useState('');
  const fileInputRef = useRef(null);

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const currentImageUrl = domain.image_url
    ? (domain.image_url.startsWith('http') ? domain.image_url : `${API_URL}${domain.image_url}`)
    : null;

  const finalTheme = theme === 'custom'
    ? (customTheme.trim() || 'personalizado')
    : theme;

  const handleImageAction = async () => {
    setImgLoading(true);
    setImgMsg('');
    try {
      if (imgAction === 'generate') {
        await domainsAPI.regenerateImage(domain.id);
        setImgMsg(t('domainEdit.generating'));
      } else if (imgAction === 'improve' && stylePrompt) {
        await domainsAPI.improveImage(domain.id, stylePrompt);
        setImgMsg(t('domainEdit.improving'));
      } else if (imgAction === 'remove') {
        await domainsAPI.removeImage(domain.id);
        setImgMsg(t('domainEdit.image_removed'));
      }
    } catch (e) {
      setImgMsg(t('domainEdit.error_image_process') + ': ' + (e.message || t('domainEdit.error_failed')));
    } finally {
      setImgLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImgLoading(true);
    setImgMsg('');
    try {
      await domainsAPI.uploadImage(domain.id, file);
      setImgMsg(t('domainEdit.image_uploaded_success'));
    } catch {
      setImgMsg(t('domainEdit.error_image_upload'));
    } finally {
      setImgLoading(false);
    }
  };

  const handleSave = async () => {
    if (!name.trim()) return;
    setSaving(true);
    setError('');
    try {
      const updates = { name: name.trim() };
      if (finalTheme !== domain.theme) updates.theme = finalTheme;

      const updated = await domainsAPI.update(domain.id, updates);
      onSave(updated);
      onClose();
    } catch (e) {
      setError(e.response?.data?.detail || e.message || t('domainEdit.error_save'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 300, padding: '1rem',
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'var(--bg-card)', border: '1px solid var(--accent-dark)',
          borderRadius: 14, padding: '1.5rem', width: '100%', maxWidth: 440,
          maxHeight: '90vh', overflowY: 'auto',
        }}
        onClick={e => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h2 style={{ color: 'var(--text-highlight)', fontSize: 16, fontWeight: 700, letterSpacing: 2, textTransform: 'uppercase', margin: 0 }}>
            {t('domainEdit.edit_title')}
          </h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 20 }}>✕</button>
        </div>

        {/* Name */}
        <label style={labelStyle}>{t('domainEdit.name')}</label>
        <input value={name} onChange={e => setName(e.target.value)} style={inputStyle} />

        {/* Theme */}
        <label style={{ ...labelStyle, marginTop: 12 }}>{t('domainEdit.theme')}</label>
        <select
          value={theme}
          onChange={e => setTheme(e.target.value)}
          style={{ ...inputStyle, marginBottom: theme === 'custom' ? 8 : 0 }}
        >
          {THEMES.map(theme => <option key={theme.value} value={theme.value}>{t(theme.labelKey)}</option>)}
        </select>

        {theme === 'custom' && (
          <input
            value={customTheme}
            onChange={e => setCustomTheme(e.target.value)}
            placeholder={t('domainEdit.name_placeholder')}
            style={{ ...inputStyle, marginTop: 4 }}
          />
        )}

        {/* Image section */}
        <div style={{ marginTop: 20, borderTop: '1px solid var(--border-color)', paddingTop: 16 }}>
          <p style={{ color: 'var(--text-muted)', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 10 }}>{t('domainEdit.image_section')}</p>

          {currentImageUrl && (
            <div style={{ marginBottom: 10, borderRadius: 8, overflow: 'hidden', height: 90 }}>
              <img src={currentImageUrl} alt="domain" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            </div>
          )}
          {!currentImageUrl && (
            <div style={{ height: 60, borderRadius: 8, background: 'var(--bg-card-inner)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 10 }}>
              <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>{t('domainEdit.no_image')}</span>
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
            <button
              onClick={() => { setImgAction('generate'); }}
              disabled={imgLoading}
              style={{ padding: '7px 4px', borderRadius: 6, border: '1px solid #7c3aed', background: imgAction === 'generate' ? '#7c3aed22' : 'transparent', color: '#a78bfa', fontSize: 11, cursor: 'pointer', fontWeight: 600 }}
            >
              {t('domainEdit.generate_ai')}
            </button>
            <button
              onClick={() => setImgAction(imgAction === 'improve' ? null : 'improve')}
              disabled={imgLoading}
              style={{ padding: '7px 4px', borderRadius: 6, border: '1px solid #06b6d4', background: imgAction === 'improve' ? '#06b6d422' : 'transparent', color: '#67e8f9', fontSize: 11, cursor: 'pointer', fontWeight: 600 }}
            >
              {t('domainEdit.improve_ai')}
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={imgLoading}
              style={{ padding: '7px 4px', borderRadius: 6, border: '1px solid var(--border-color)', background: 'transparent', color: 'var(--text-muted)', fontSize: 11, cursor: 'pointer', fontWeight: 600 }}
            >
              {t('domainEdit.upload')}
            </button>
            <button
              onClick={() => setImgAction('remove')}
              disabled={imgLoading || !currentImageUrl}
              style={{ padding: '7px 4px', borderRadius: 6, border: '1px solid #ef444466', background: 'transparent', color: '#ef4444', fontSize: 11, cursor: 'pointer', fontWeight: 600, opacity: currentImageUrl ? 1 : 0.4 }}
            >
              {t('domainEdit.remove')}
            </button>
          </div>

          {imgAction === 'improve' && (
            <div style={{ marginTop: 8, display: 'flex', gap: 6 }}>
              <input
                value={stylePrompt}
                onChange={e => setStylePrompt(e.target.value)}
                placeholder={t('domainEdit.style_prompt_placeholder')}
                style={{ ...inputStyle, flex: 1 }}
              />
              <button
                onClick={handleImageAction}
                disabled={imgLoading || !stylePrompt}
                style={{ padding: '8px 12px', borderRadius: 6, background: '#06b6d4', border: 'none', color: '#fff', fontSize: 11, cursor: 'pointer', fontWeight: 700, opacity: (!stylePrompt || imgLoading) ? 0.5 : 1 }}
              >
                {imgLoading ? '...' : t('domainEdit.apply')}
              </button>
            </div>
          )}

          {imgAction && imgAction !== 'improve' && (
            <button
              onClick={handleImageAction}
              disabled={imgLoading}
              style={{ marginTop: 8, width: '100%', padding: '8px 0', borderRadius: 6, background: 'var(--accent)', border: 'none', color: '#fff', fontSize: 12, fontWeight: 700, cursor: 'pointer', opacity: imgLoading ? 0.6 : 1 }}
            >
              {imgLoading ? t('domainEdit.processing') : t('domainEdit.confirm_image_action')}
            </button>
          )}

          {imgMsg && (
            <p style={{ color: imgMsg.startsWith(t('domainEdit.error_prefix')) ? '#ef4444' : '#22c55e', fontSize: 12, marginTop: 6 }}>
              {imgMsg}
            </p>
          )}

          <input ref={fileInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={handleFileUpload} />
        </div>

        {error && <p style={{ color: '#ef4444', fontSize: 12, marginTop: 8 }}>{error}</p>}

        <div style={{ display: 'flex', gap: 8, marginTop: 20 }}>
          <button
            onClick={onClose}
            style={{ flex: 1, padding: '10px 0', borderRadius: 8, border: '1px solid var(--border-color)', background: 'transparent', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 13 }}
          >
            {t('domainEdit.cancel')}
          </button>
          <button
            onClick={handleSave}
            disabled={saving || !name.trim()}
            style={{ flex: 2, padding: '10px 0', borderRadius: 8, border: 'none', background: 'var(--accent)', color: '#fff', cursor: 'pointer', fontSize: 13, fontWeight: 700, letterSpacing: 1, opacity: (saving || !name.trim()) ? 0.6 : 1 }}
          >
            {saving ? t('domainEdit.saving') : t('domainEdit.save')}
          </button>
        </div>
      </div>
    </div>
  );
}
