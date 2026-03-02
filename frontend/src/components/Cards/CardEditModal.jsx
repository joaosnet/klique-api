import { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { cardsAPI } from '../../services/api';

const TEMPLATES = [
  { value: 'if_then', labelKey: 'cardEdit.type_if_then', color: '#3b82f6' },
  { value: 'payoff_matrix', labelKey: 'cardEdit.type_payoff', color: '#f59e0b' },
  { value: 'black_swan', labelKey: 'cardEdit.type_black_swan', color: '#ef4444' },
];

const API_URL = import.meta.env.VITE_API_URL || '';

const inputStyle = {
  width: '100%',
  background: 'var(--bg-card-inner)',
  border: '1px solid var(--border-color)',
  color: 'var(--text-main)',
  borderRadius: 6,
  padding: '8px 10px',
  fontSize: 13,
  outline: 'none',
  boxSizing: 'border-box',
  resize: 'vertical',
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

function heatColor(score) {
  if (score >= 67) return '#ef4444';
  if (score >= 34) return '#f59e0b';
  return '#22c55e';
}

/**
 * Modal para editar os campos e a imagem de um card.
 *
 * Modo "pre-save": cardId é null; onSave recebe (editedCard, pendingImageAction)
 * Modo "edit": cardId é string; o modal persiste alterações via API e chama onSave(updatedCard)
 */
export default function CardEditModal({ card, cardId, onSave, onClose }) {
  const { t } = useTranslation();
  const [templateType, setTemplateType] = useState(card.template_type || 'if_then');
  const [scenarioContext, setScenarioContext] = useState(card.scenario_context || '');
  const [question, setQuestion] = useState(card.question || '');
  const [predictedOutcome, setPredictedOutcome] = useState(card.predicted_outcome || '');
  const [gameTheoryExplanation, setGameTheoryExplanation] = useState(card.game_theory_explanation || '');
  const [heatScore, setHeatScore] = useState(card.probability_heat_score ?? 50);
  const [visualPrompt, setVisualPrompt] = useState(card.visual_prompt_idea || '');

  // Image section
  const [imgAction, setImgAction] = useState(null); // 'generate'|'improve'|'upload'|'remove'
  const [stylePrompt, setStylePrompt] = useState('');
  const [pendingFile, setPendingFile] = useState(null);
  const [imgLoading, setImgLoading] = useState(false);
  const [imgMsg, setImgMsg] = useState('');
  const fileInputRef = useRef(null);

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const currentImageUrl = card.media_urls && card.media_urls[0]
    ? `${API_URL}${card.media_urls[0]}`
    : null;

  const executeImageAction = async (action, prompt) => {
    if (!cardId) return;
    setImgLoading(true);
    setImgMsg('');
    try {
      if (action === 'generate') {
        await cardsAPI.regenerateImage(cardId);
        setImgMsg(t('cardEdit.gen_started'));
      } else if (action === 'improve' && prompt) {
        await cardsAPI.improveImage(cardId, prompt);
        setImgMsg(t('cardEdit.generating'));
      } else if (action === 'remove') {
        await cardsAPI.removeImage(cardId);
        setImgMsg(t('cardEdit.image_removed'));
      }
    } catch (e) {
      setImgMsg(t('cardEdit.error_image_process') + ': ' + (e.message || ''));
    } finally {
      setImgLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (!cardId) {
      // Pre-save: just store the file for later
      setPendingFile(file);
      setImgAction('upload');
      setImgMsg(`${t('cardEdit.file_selected')} ${file.name}`);
      return;
    }
    setImgLoading(true);
    setImgMsg('');
    try {
      await cardsAPI.uploadImage(cardId, file);
      setImgMsg(t('cardEdit.image_removed'));
    } catch (err) {
      setImgMsg(t('cardEdit.error_image_upload'));
    } finally {
      setImgLoading(false);
    }
  };

  const buildEditedCard = () => ({
    ...card,
    template_type: templateType,
    scenario_context: scenarioContext,
    question,
    predicted_outcome: predictedOutcome,
    game_theory_explanation: gameTheoryExplanation,
    probability_heat_score: heatScore,
    visual_prompt_idea: visualPrompt,
  });

  const handleSave = async () => {
    setSaving(true);
    setError('');
    try {
      const updates = {
        template_type: templateType,
        scenario_context: scenarioContext,
        question,
        predicted_outcome: predictedOutcome,
        game_theory_explanation: gameTheoryExplanation,
        probability_heat_score: heatScore,
        visual_prompt_idea: visualPrompt,
      };

      if (cardId) {
        // Edit mode: persist to API
        const updated = await cardsAPI.update(cardId, updates);
        onSave(updated, null);
      } else {
        // Pre-save mode: return local card + pending image action
        const pendingAction = imgAction
          ? { type: imgAction, stylePrompt, file: pendingFile }
          : null;
        onSave(buildEditedCard(), pendingAction);
      }
      onClose();
    } catch (e) {
      setError(e.message || t('cardEdit.error_save'));
    } finally {
      setSaving(false);
    }
  };

  const tmpl = TEMPLATES.find(tp => tp.value === templateType) || TEMPLATES[0];

  return (
    <div
      style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)',
        display: 'flex', alignItems: 'flex-start', justifyContent: 'center',
        zIndex: 300, padding: '1rem', overflowY: 'auto',
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'var(--bg-card)', border: '1px solid var(--accent-dark)',
          borderRadius: 14, padding: '1.5rem', width: '100%', maxWidth: 500,
          marginTop: 16, marginBottom: 64,
        }}
        onClick={e => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h2 style={{ color: 'var(--text-highlight)', fontSize: 16, fontWeight: 700, letterSpacing: 2, textTransform: 'uppercase', margin: 0 }}>
            {cardId ? t('cardEdit.edit_card') : t('cardEdit.create_card')}
          </h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 20 }}>✕</button>
        </div>

        {/* Template type */}
        <label style={labelStyle}>{t('cardEdit.template_type')}</label>
        <div style={{ display: 'flex', gap: 8, marginBottom: 4 }}>
          {TEMPLATES.map(tmpl => (
            <button
              key={tmpl.value}
              onClick={() => setTemplateType(tmpl.value)}
              style={{
                flex: 1, padding: '6px 4px', borderRadius: 6, fontSize: 10, fontWeight: 700,
                letterSpacing: 1, textTransform: 'uppercase', cursor: 'pointer',
                border: `1px solid ${tmpl.color}`,
                background: templateType === tmpl.value ? tmpl.color + '33' : 'transparent',
                color: tmpl.color,
              }}
            >
              {t(tmpl.labelKey)}
            </button>
          ))}
        </div>

        {/* Text fields */}
        <label style={labelStyle}>{t('cardEdit.context_scenario')}</label>
        <textarea rows={3} value={scenarioContext} onChange={e => setScenarioContext(e.target.value)} style={inputStyle} />

        <label style={labelStyle}>{t('cardEdit.tactical_question')}</label>
        <textarea rows={2} value={question} onChange={e => setQuestion(e.target.value)} style={inputStyle} />

        <label style={labelStyle}>{t('cardEdit.expected_outcome')}</label>
        <textarea rows={2} value={predictedOutcome} onChange={e => setPredictedOutcome(e.target.value)} style={inputStyle} />

        <label style={labelStyle}>{t('cardEdit.analysis')}</label>
        <textarea rows={3} value={gameTheoryExplanation} onChange={e => setGameTheoryExplanation(e.target.value)} style={inputStyle} />

        <label style={labelStyle}>{t('cardEdit.heat_score')} <span style={{ color: heatColor(heatScore), fontWeight: 700 }}>{heatScore}</span></label>
        <input
          type="range" min={0} max={100} value={heatScore}
          onChange={e => setHeatScore(Number(e.target.value))}
          style={{ width: '100%', accentColor: heatColor(heatScore), marginBottom: 4 }}
        />

        <label style={labelStyle}>{t('cardEdit.image_hint')}</label>
        <input value={visualPrompt} onChange={e => setVisualPrompt(e.target.value)} style={{ ...inputStyle, resize: 'none' }} />

        {/* Image section */}
        <div style={{ marginTop: 20, borderTop: '1px solid var(--border-color)', paddingTop: 16 }}>
          <p style={{ color: 'var(--text-muted)', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 10 }}>{t('cardEdit.card_image')}</p>

          {currentImageUrl && (
            <div style={{ marginBottom: 10, borderRadius: 8, overflow: 'hidden', maxHeight: 100 }}>
              <img src={currentImageUrl} alt="card" style={{ width: '100%', height: 100, objectFit: 'cover' }} />
            </div>
          )}
          {!currentImageUrl && (
            <div style={{ height: 60, borderRadius: 8, background: 'var(--bg-card-inner)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 10 }}>
              <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>{t('cardEdit.no_image')}</span>
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
            <button
              onClick={() => { setImgAction('generate'); if (cardId) executeImageAction('generate'); }}
              disabled={imgLoading}
            >
              {t('cardEdit.generate_ai')}
            </button>
            <button
              onClick={() => setImgAction(imgAction === 'improve' ? null : 'improve')}
              disabled={imgLoading}
            >
              {t('cardEdit.improve_ai')}
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={imgLoading}
            >
              {t('cardEdit.upload')}
            </button>
            <button
              onClick={() => { setImgAction('remove'); if (cardId) executeImageAction('remove'); }}
              disabled={imgLoading || !currentImageUrl}
            >
              {t('cardEdit.remove')}
            </button>
          </div>

          {/* Style prompt for improve */}
          {imgAction === 'improve' && (
            <div style={{ marginTop: 8, display: 'flex', gap: 6 }}>
              <input
                value={stylePrompt}
                onChange={e => setStylePrompt(e.target.value)}
                placeholder={t('cardEdit.style_placeholder')}
                style={{ ...inputStyle, flex: 1, marginBottom: 0 }}
              />
              {cardId && (
                <button
                  onClick={() => executeImageAction('improve', stylePrompt)}
                  disabled={imgLoading || !stylePrompt}
                >
                  {imgLoading ? '...' : t('cardEdit.apply')}
                </button>
              )}
            </div>
          )}

          {imgMsg && (
            <p style={{ color: imgMsg.startsWith('Erro') ? '#ef4444' : '#22c55e', fontSize: 12, marginTop: 6 }}>
              {imgMsg}
            </p>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            style={{ display: 'none' }}
            onChange={handleFileUpload}
          />
        </div>

        {/* Actions */}
        {error && <p style={{ color: '#ef4444', fontSize: 12, marginTop: 8 }}>{error}</p>}
        <div style={{ display: 'flex', gap: 8, marginTop: 20 }}>
          <button
            onClick={onClose}
          >
            {t('cardEdit.cancel')}
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? t('cardEdit.saving') : t('cardEdit.save_card')}
          </button>
        </div>
      </div>
    </div>
  );
}
