import { useState, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import { christmasAPI } from '../../services/api';
import { useNavigate } from 'react-router-dom';
import './AvatarGenerator.css';

const TEMPLATES = [
    { id: 'papai-noel', name: 'Papai Noel', emoji: '🎅' },
    { id: 'duende', name: 'Duende', emoji: '🧝' },
    { id: 'cena-natal', name: 'Cena de Natal', emoji: '🎄' },
    { id: 'gorro-neve', name: 'Gorro de Neve', emoji: '⛄' },
    { id: 'anjo', name: 'Anjo', emoji: '👼' },
    { id: 'rena', name: 'Rena', emoji: '🦌' },
    { id: 'boneco-neve', name: 'Boneco de Neve', emoji: '☃️' },
    { id: 'grinch', name: 'Grinch', emoji: '💚' },
    { id: 'pinguim', name: 'Pinguim', emoji: '🐧' },
    { id: 'urso-polar', name: 'Urso Polar', emoji: '🐻‍❄️' },
];

export default function AvatarGenerator() {
    const [selectedImage, setSelectedImage] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [selectedTemplate, setSelectedTemplate] = useState(null);
    const [removeBg, setRemoveBg] = useState(false);
    const [processing, setProcessing] = useState(false);
    const [progress, setProgress] = useState({ message: '', percent: 0 });
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');

    const fileInputRef = useRef(null);
    const { credits, refreshCredits, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    const handleImageSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (file.size > 10 * 1024 * 1024) {
                setError('Imagem muito grande. Máximo 10MB.');
                return;
            }
            setSelectedImage(file);
            setImagePreview(URL.createObjectURL(file));
            setResult(null);
            setError('');
        }
    };

    const handleGenerate = async () => {
        if (!isAuthenticated) {
            navigate('/login');
            return;
        }

        if (!selectedImage || !selectedTemplate) {
            setError('Selecione uma imagem e um template');
            return;
        }

        if (credits.total <= 0) {
            navigate('/credits');
            return;
        }

        setError('');
        setProcessing(true);
        setProgress({ message: 'Iniciando...', percent: 0 });

        try {
            const resultData = await christmasAPI.generateAvatar(
                selectedImage,
                selectedTemplate,
                removeBg,
                (progressData) => {
                    setProgress({
                        message: progressData.message,
                        percent: progressData.percent,
                    });
                }
            );

            if (resultData?.processed_image) {
                setResult(resultData.processed_image);
                await refreshCredits();
            }
        } catch (err) {
            setError(err.message || 'Erro ao gerar avatar');
        } finally {
            setProcessing(false);
        }
    };

    const handleDownload = () => {
        if (!result) return;
        const link = document.createElement('a');
        link.download = 'avatar-natal-klique.png';
        link.href = result;
        link.click();
    };

    const handleReset = () => {
        setSelectedImage(null);
        setImagePreview(null);
        setResult(null);
        setError('');
        setProgress({ message: '', percent: 0 });
    };

    return (
        <div className="generator-container">
            <div className="generator-header">
                <h1>🎄 Crie seu Avatar Natalino</h1>
                <p>Transforme sua foto em um personagem de Natal!</p>
            </div>

            {error && (
                <div className="error-banner">
                    <span>⚠️</span> {error}
                </div>
            )}

            <div className="generator-grid">
                {/* Upload Section */}
                <div className="upload-section">
                    <div
                        className={`upload-zone ${imagePreview ? 'has-image' : ''}`}
                        onClick={() => !processing && fileInputRef.current?.click()}
                    >
                        {imagePreview ? (
                            <img src={imagePreview} alt="Preview" className="image-preview" />
                        ) : (
                            <div className="upload-placeholder">
                                <span className="upload-icon">📷</span>
                                <p>Clique para enviar sua foto</p>
                                <span className="upload-hint">ou arraste e solte aqui</span>
                            </div>
                        )}
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleImageSelect}
                            hidden
                            disabled={processing}
                        />
                    </div>

                    {imagePreview && !processing && (
                        <button onClick={handleReset} className="btn-reset">
                            Trocar foto
                        </button>
                    )}
                </div>

                {/* Result Section */}
                <div className="result-section">
                    {processing ? (
                        <div className="processing-state">
                            <div className="processing-animation">
                                <span className="processing-icon">✨</span>
                            </div>
                            <p className="processing-message">{progress.message}</p>
                            <div className="progress-bar">
                                <div
                                    className="progress-fill"
                                    style={{ width: `${progress.percent}%` }}
                                />
                            </div>
                        </div>
                    ) : result ? (
                        <div className="result-display">
                            <img src={result} alt="Avatar gerado" className="result-image" />
                            <div className="result-actions">
                                <button onClick={handleDownload} className="btn-download">
                                    ⬇️ Baixar Avatar
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="result-placeholder">
                            <span>🎅</span>
                            <p>Seu avatar aparecerá aqui</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Templates Section */}
            <div className="templates-section">
                <h3>Escolha um estilo:</h3>
                <div className="templates-grid">
                    {TEMPLATES.map((template) => (
                        <button
                            key={template.id}
                            className={`template-card ${selectedTemplate === template.id ? 'selected' : ''}`}
                            onClick={() => setSelectedTemplate(template.id)}
                            disabled={processing}
                        >
                            <span className="template-emoji">{template.emoji}</span>
                            <span className="template-name">{template.name}</span>
                        </button>
                    ))}
                </div>
            </div>

            {/* Options */}
            <div className="options-section">
                <label className="checkbox-option">
                    <input
                        type="checkbox"
                        checked={removeBg}
                        onChange={(e) => setRemoveBg(e.target.checked)}
                        disabled={processing}
                    />
                    <span className="checkbox-label">✂️ Remover fundo da imagem</span>
                </label>
            </div>

            {/* Generate Button */}
            <button
                className="btn-generate"
                onClick={handleGenerate}
                disabled={!selectedImage || !selectedTemplate || processing}
            >
                {processing ? (
                    <>
                        <span className="spinner"></span>
                        Processando...
                    </>
                ) : credits.total > 0 ? (
                    <>
                        ✨ Gerar Avatar ({credits.total} créditos)
                    </>
                ) : (
                    <>
                        🎫 Comprar Créditos
                    </>
                )}
            </button>
        </div>
    );
}
