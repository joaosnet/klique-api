import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { christmasAPI } from '../../services/api';
import { useNavigate } from 'react-router-dom';
import ImageComparator from './ImageComparator';
import './AvatarGenerator.css';

export default function AvatarGenerator() {
    const [categories, setCategories] = useState({});
    const [currentCategory, setCurrentCategory] = useState('populares');
    const [selectedImage, setSelectedImage] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [selectedTemplate, setSelectedTemplate] = useState(null);
    const [removeBg, setRemoveBg] = useState(false);
    const [processing, setProcessing] = useState(false);
    const [progress, setProgress] = useState({ message: '', percent: 0 });
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const [cameraStream, setCameraStream] = useState(null);
    const [cameraActive, setCameraActive] = useState(false);

    const fileInputRef = useRef(null);
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const { credits, refreshCredits, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        const fetchTemplates = async () => {
            try {
                const data = await christmasAPI.getTemplates();
                setCategories(data);
                if (Object.keys(data).length > 0) {
                    setCurrentCategory(Object.keys(data)[0]);
                }
            } catch (err) {
                console.error('Erro ao buscar templates:', err);
                setError('Não foi possível carregar os templates.');
            }
        };
        fetchTemplates();
        startCamera();

        return () => stopCamera();
    }, []);

    const startCamera = async () => {
        console.log('Starting camera...');
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } }
            });

            console.log('Stream obtained:', stream);
            setCameraStream(stream);
            setCameraActive(true);
            setError('');

            // Delay to ensure the video element is rendered
            setTimeout(() => {
                if (videoRef.current) {
                    console.log('Attaching stream to video element');
                    videoRef.current.srcObject = stream;
                } else {
                    console.error('videoRef.current is null!');
                }
            }, 500);

        } catch (err) {
            console.error('Erro ao acessar a câmera:', err);
            let msg = 'Não foi possível acessar a câmera.';
            if (err.name === 'NotAllowedError') msg = 'Acesso à câmera negado. Por favor, permita o acesso.';
            else if (err.name === 'NotFoundError') msg = 'Nenhuma câmera encontrada.';
            setError(msg + ' Tente fazer o upload.');
            setCameraActive(false);
        }
    };

    const stopCamera = () => {
        if (cameraStream) {
            cameraStream.getTracks().forEach(track => track.stop());
            setCameraStream(null);
            setCameraActive(false);
        }
    };

    const handleCapture = () => {
        if (videoRef.current && canvasRef.current) {
            const video = videoRef.current;
            const canvas = canvasRef.current;
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');

            // Flip horizontal for natural preview if needed, 
            // but for Christmas avatar usually we want what the camera sees.
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            canvas.toBlob((blob) => {
                const file = new File([blob], "captured-photo.jpg", { type: "image/jpeg" });
                setSelectedImage(file);
                setImagePreview(URL.createObjectURL(blob));
                setResult(null);
                setError('');
                stopCamera();
            }, 'image/jpeg', 0.9);
        }
    };

    const categoryLabels = {
        'populares': 'Populares',
        'classico': 'Clássico',
        'divertido': 'Divertido',
        'papai-noel': 'Papai Noel'
    };

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
        if (!selectedImage || !selectedTemplate) {
            setError('Selecione uma imagem e um template');
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
                if (isAuthenticated) {
                    await refreshCredits();
                }
            }
        } catch (err) {
            if (err.message.includes('Faça login')) {
                navigate('/login', { state: { message: err.message } });
            } else if (err.message.includes('Créditos insuficientes')) {
                navigate('/credits');
            } else {
                setError(err.message || 'Erro ao gerar avatar');
            }
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
        startCamera();
    };

    return (
        <div className="generator-container">
            <div className="generator-header">
                <h1>Torne-se um ícone de Natal!</h1>
                <p>Crie sua foto de perfil para Instagram ou WhatsApp.</p>
            </div>

            <div className="editor-card">
                {error && (
                    <div className="error-banner">
                        <span>⚠️</span> {error}
                    </div>
                )}

                <div className="generator-grid">
                    {/* Upload Section */}
                    <div className="upload-section">
                        <div
                            className={`upload-zone ${imagePreview ? 'has-image' : ''} ${cameraActive ? 'camera-active' : ''}`}
                            onClick={() => !processing && !cameraActive && !imagePreview && fileInputRef.current?.click()}
                        >
                            {imagePreview ? (
                                <img src={imagePreview} alt="Preview" className="image-preview" />
                            ) : cameraActive ? (
                                <div className="camera-preview-container">
                                    <video
                                        ref={videoRef}
                                        autoPlay
                                        playsInline
                                        className="camera-video"
                                    />
                                    <canvas ref={canvasRef} style={{ display: 'none' }} />
                                    <div className="camera-overlay">
                                        <button
                                            className="btn-capture"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleCapture();
                                            }}
                                        >
                                            <span className="capture-icon">📸</span>
                                            Tirar Foto
                                        </button>
                                    </div>
                                </div>
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

                        <div className="upload-actions">
                            {imagePreview && !processing && (
                                <button onClick={handleReset} className="btn-secondary">
                                    🔄 Tentar novamente
                                </button>
                            )}
                            {!imagePreview && !cameraActive && !processing && (
                                <button onClick={startCamera} className="btn-secondary">
                                    📷 Usar Câmera
                                </button>
                            )}
                            {cameraActive && !processing && (
                                <button onClick={() => fileInputRef.current?.click()} className="btn-secondary">
                                    📁 Fazer Upload
                                </button>
                            )}
                        </div>
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
                        ) : result && imagePreview ? (
                            <>
                                <ImageComparator
                                    beforeImage={imagePreview}
                                    afterImage={result}
                                />
                                <div className="result-actions">
                                    <button onClick={handleDownload} className="btn-download">
                                        ⬇️ Baixar Avatar
                                    </button>
                                </div>
                            </>
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
                    <div className="category-tabs">
                        {Object.keys(categories).map((cat) => (
                            <button
                                key={cat}
                                className={`category-tab ${currentCategory === cat ? 'active' : ''}`}
                                onClick={() => setCurrentCategory(cat)}
                                disabled={processing}
                            >
                                {categoryLabels[cat] || cat}
                            </button>
                        ))}
                    </div>

                    <div className="templates-grid">
                        {(categories[currentCategory] || []).map((template) => (
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
                    ) : (
                        <>
                            ✨ Gerar Avatar {isAuthenticated && `(${credits.total} créditos)`}
                        </>
                    )}
                </button>
            </div> {/* end editor-card */}
        </div>
    );
}

