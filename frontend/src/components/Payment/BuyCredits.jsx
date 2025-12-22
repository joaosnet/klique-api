import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { paymentsAPI } from '../../services/api';
import './BuyCredits.css';

export default function BuyCredits() {
    const [amount, setAmount] = useState(5);
    const [loading, setLoading] = useState(false);
    const [payment, setPayment] = useState(null);
    const [error, setError] = useState('');
    const [checkingPayment, setCheckingPayment] = useState(false);

    const { credits, refreshCredits } = useAuth();

    const creditsToReceive = Math.floor(amount);
    const MIN_AMOUNT = 1;
    const MAX_AMOUNT = 100;

    const handleAmountChange = (e) => {
        const value = parseFloat(e.target.value);
        if (value >= MIN_AMOUNT && value <= MAX_AMOUNT) {
            setAmount(value);
        }
    };

    const handleCreatePix = async () => {
        setError('');
        setLoading(true);

        try {
            const result = await paymentsAPI.createPixPayment(amount);
            setPayment(result);
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                'Erro ao criar pagamento. Tente novamente.'
            );
        } finally {
            setLoading(false);
        }
    };

    const handleCopyPix = async () => {
        if (payment?.copy_paste) {
            await navigator.clipboard.writeText(payment.copy_paste);
            alert('Código PIX copiado!');
        }
    };

    // Verificar status do pagamento periodicamente
    useEffect(() => {
        if (!payment?.payment_id) return;

        const checkStatus = async () => {
            setCheckingPayment(true);
            try {
                const status = await paymentsAPI.getPaymentStatus(payment.payment_id);
                if (status.status === 'approved') {
                    await refreshCredits();
                    setPayment(null);
                    alert('Pagamento confirmado! Seus créditos foram adicionados.');
                }
            } catch (err) {
                console.error('Erro ao verificar pagamento:', err);
            } finally {
                setCheckingPayment(false);
            }
        };

        const interval = setInterval(checkStatus, 5000); // Verificar a cada 5s
        return () => clearInterval(interval);
    }, [payment?.payment_id, refreshCredits]);

    const handleNewPayment = () => {
        setPayment(null);
        setError('');
    };

    return (
        <div className="buy-credits-container">
            <div className="buy-credits-card">
                <div className="card-header">
                    <span className="card-icon">🎫</span>
                    <h2>Comprar Créditos</h2>
                    <p>Cada crédito gera 1 avatar natalino</p>
                </div>

                <div className="current-balance">
                    <span className="balance-label">Saldo atual:</span>
                    <span className="balance-value">{credits.total} créditos</span>
                </div>

                {error && (
                    <div className="error-message">
                        <span>⚠️</span> {error}
                    </div>
                )}

                {!payment ? (
                    <>
                        <div className="amount-selector">
                            <label>Quanto você quer pagar?</label>

                            <div className="amount-input-wrapper">
                                <span className="currency">R$</span>
                                <input
                                    type="number"
                                    value={amount}
                                    onChange={handleAmountChange}
                                    min={MIN_AMOUNT}
                                    max={MAX_AMOUNT}
                                    step="1"
                                    disabled={loading}
                                />
                            </div>

                            <input
                                type="range"
                                value={amount}
                                onChange={handleAmountChange}
                                min={MIN_AMOUNT}
                                max={MAX_AMOUNT}
                                step="1"
                                className="amount-slider"
                                disabled={loading}
                            />

                            <div className="amount-labels">
                                <span>R$ {MIN_AMOUNT}</span>
                                <span>R$ {MAX_AMOUNT}</span>
                            </div>
                        </div>

                        <div className="credits-preview">
                            <span className="preview-icon">✨</span>
                            <span className="preview-text">
                                Você receberá <strong>{creditsToReceive} créditos</strong>
                            </span>
                        </div>

                        <button
                            onClick={handleCreatePix}
                            className="btn-generate-pix"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <span className="spinner"></span>
                                    Gerando PIX...
                                </>
                            ) : (
                                <>
                                    <span>📱</span>
                                    Gerar QR Code PIX
                                </>
                            )}
                        </button>
                    </>
                ) : (
                    <div className="pix-payment">
                        <div className="pix-header">
                            <span className="pix-icon">✅</span>
                            <h3>PIX Gerado!</h3>
                            <p>Escaneie o QR Code ou copie o código</p>
                        </div>

                        <div className="qr-code-container">
                            {payment.qr_code_base64 ? (
                                <img
                                    src={`data:image/png;base64,${payment.qr_code_base64}`}
                                    alt="QR Code PIX"
                                    className="qr-code"
                                />
                            ) : (
                                <div className="qr-placeholder">
                                    <span>📱</span>
                                    <p>QR Code não disponível</p>
                                </div>
                            )}
                        </div>

                        <div className="pix-info">
                            <div className="info-row">
                                <span>Valor:</span>
                                <strong>R$ {payment.amount?.toFixed(2)}</strong>
                            </div>
                            <div className="info-row">
                                <span>Créditos:</span>
                                <strong>{payment.credits_amount}</strong>
                            </div>
                        </div>

                        <button onClick={handleCopyPix} className="btn-copy-pix">
                            <span>📋</span>
                            Copiar código PIX
                        </button>

                        {checkingPayment && (
                            <div className="checking-payment">
                                <span className="spinner"></span>
                                Aguardando pagamento...
                            </div>
                        )}

                        <button onClick={handleNewPayment} className="btn-new-payment">
                            Gerar novo pagamento
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
