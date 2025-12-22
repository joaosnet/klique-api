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
    const [isDragging, setIsDragging] = useState(false);

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
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } }
            });

            setCameraStream(stream);
            setCameraActive(true);
            setError('');

            // Delay to ensure the video element is rendered
            setTimeout(() => {
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
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

            // Espelhar horizontalmente para corresponder à visualização da câmera (UX mais natural)
            ctx.translate(canvas.width, 0);
            ctx.scale(-1, 1);
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
        if (file) processFile(file);
    };

    const processFile = (file) => {
        if (file.size > 10 * 1024 * 1024) {
            setError('Imagem muito grande. Máximo 10MB.');
            return;
        }
        if (!file.type.startsWith('image/')) {
            setError('Por favor, envie apenas um arquivo de imagem.');
            return;
        }
        setSelectedImage(file);
        setImagePreview(URL.createObjectURL(file));
        setResult(null);
        setError('');
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);

        if (processing) return;

        const file = e.dataTransfer.files?.[0];
        if (file) {
            if (cameraActive) {
                stopCamera();
            }
            processFile(file);
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
            console.error('Erro na geração:', err);
            if (err.status === 401 || err.message.includes('Faça login')) {
                navigate('/login', { state: { message: err.message } });
            } else if (err.status === 402 || err.message.includes('Créditos insuficientes')) {
                // Redireciona para página de créditos se faltar saldo
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

    // Helper to convert Base64 to File for sharing
    const dataURLtoFile = (dataurl, filename) => {
        try {
            const arr = dataurl.split(',');
            const mime = arr[0].match(/:(.*?);/)[1];
            const bstr = atob(arr[1]);
            let n = bstr.length;
            const u8arr = new Uint8Array(n);
            while (n--) {
                u8arr[n] = bstr.charCodeAt(n);
            }
            return new File([u8arr], filename, { type: mime });
        } catch (e) {
            console.error("Error converting file", e);
            return null;
        }
    };

    const handleShareWhatsApp = async () => {
        const text = `Ficou incrível meu avatar de Natal! 🎅🎄\n\nFiz no Klique, cria o seu também aqui: ${window.location.href}`;

        // Tenta usar o Web Share API nativo (Mobile Android/iOS)
        if (navigator.share && result) {
            try {
                const file = dataURLtoFile(result, 'avatar-natal.png');
                if (file && navigator.canShare && navigator.canShare({ files: [file] })) {
                    await navigator.share({
                        files: [file],
                        title: 'Meu Avatar de Natal',
                        text: text
                    });
                    return; // Sucesso, não precisa do fallback
                }
            } catch (error) {
                console.log('Share API cancelled or failed:', error);
                // Continua para o fallback
            }
        }

        // Fallback: Desktop ou navegador sem suporte a arquivos
        // Baixa a imagem para o usuário poder anexar manualmente
        handleDownload();

        // Abre o WhatsApp com o texto
        const urlText = encodeURIComponent(text);
        window.open(`https://wa.me/?text=${urlText}`, '_blank');
    };

    const handleShareInstagram = async () => {
        const text = `Ficou incrível meu avatar de Natal! 🎅🎄\n\nFiz no Klique, cria o seu também aqui: ${window.location.href}`;

        // Tenta usar o Web Share API nativo
        if (navigator.share && result) {
            try {
                const file = dataURLtoFile(result, 'avatar-natal.png');
                if (file && navigator.canShare && navigator.canShare({ files: [file] })) {
                    await navigator.share({
                        files: [file],
                        title: 'Meu Avatar de Natal',
                        text: text
                    });
                    return;
                }
            } catch (error) {
                console.log('Share API cancelled or failed:', error);
            }
        }

        // Fallback: Baixa a imagem + Copia Texto + Abre Instagram
        handleDownload();

        navigator.clipboard.writeText(text).then(() => {
            alert('Imagem baixada e texto copiado! 📸\n\nAgora é só abrir o Instagram e postar no Story ou Feed.');
            window.open('https://instagram.com', '_blank');
        }).catch(() => {
            window.open('https://instagram.com', '_blank');
        });
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

                <div className="generator-stage">
                    {result ? (
                        // Result State (Comparator)
                        <div className="result-container" style={{ position: 'relative', minHeight: '450px' }}>
                            <ImageComparator
                                beforeImage={imagePreview}
                                afterImage={result}
                            />
                        </div>
                    ) : (
                        // Upload / Preview / Camera State
                        <div className="upload-container">
                            <div
                                className={`upload-zone ${imagePreview ? 'has-image' : ''} ${cameraActive ? 'camera-active' : ''} ${isDragging ? 'dragging' : ''}`}
                                onClick={() => !processing && !cameraActive && !imagePreview && fileInputRef.current?.click()}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onDrop={handleDrop}
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
                                        <div className="camera-overlay" style={{ gap: '15px' }}>
                                            <button
                                                className="btn-capture secondary-action"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    fileInputRef.current?.click();
                                                }}
                                                title="Fazer Upload da Galeria"
                                                style={{ width: '50px', height: '50px', padding: 0, justifyContent: 'center', borderRadius: '50%', background: 'rgba(255,255,255,0.2)', backdropFilter: 'blur(5px)' }}
                                            >
                                                <span className="capture-icon" style={{ fontSize: '1.5rem' }}>📁</span>
                                            </button>

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
                                        <div style={{ marginTop: '20px' }}>
                                            {!cameraActive && (
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); startCamera(); }}
                                                    className="btn-secondary"
                                                    style={{ background: 'var(--christmas-green)', color: 'white', border: 'none' }}
                                                >
                                                    📷 Usar Câmera
                                                </button>
                                            )}
                                        </div>
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

                            {/* Actions overlay for preview mode (Reset button) */}
                            {imagePreview && !processing && !result && (
                                <div style={{ position: 'absolute', top: '10px', right: '10px', zIndex: 10 }}>
                                    <button onClick={(e) => { e.stopPropagation(); handleReset(); }} className="btn-secondary">
                                        🔄 Trocar Foto
                                    </button>
                                </div>
                            )}

                            {/* PROCESSING OVERLAY */}
                            {processing && (
                                <div className="processing-overlay">
                                    <div className="processing-content">
                                        <span className="processing-icon">✨</span>
                                        <p className="processing-message">{progress.message || 'Preparando magia...'}</p>
                                        <div className="progress-bar">
                                            <div
                                                className="progress-fill"
                                                style={{ width: `${progress.percent}%` }}
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {result ? (
                    <div className="result-actions-section">
                        <div className="share-buttons-grid">
                            <button onClick={handleDownload} className="btn-action download">
                                <span className="icon">⬇️</span>
                                <span className="label">Baixar Imagem</span>
                            </button>

                            <button onClick={handleShareWhatsApp} className="btn-action whatsapp">
                                <span className="icon">💚</span>
                                <span className="label">WhatsApp</span>
                            </button>

                            <button onClick={handleShareInstagram} className="btn-action instagram">
                                <span className="icon">📸</span>
                                <span className="label">Instagram</span>
                            </button>
                        </div>

                        <button onClick={handleReset} className="btn-action reset">
                            <span>🔄</span> Fazer Outro
                        </button>
                    </div>
                ) : (
                    <>
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
                                        {template.preview_url ? (
                                            <img
                                                src={template.preview_url}
                                                alt={template.name}
                                                className="template-preview-image"
                                            />
                                        ) : (
                                            <span className="template-emoji">{template.emoji}</span>
                                        )}
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
                    </>
                )}
            </div> {/* end editor-card */}
        </div>
    );
}

