import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { paymentsAPI } from '../../services/api';
import './BuyCredits.css';
import { getErrorMessage } from '../../utils/errorHandler';

export default function BuyCredits() {
    const [unitPrice, setUnitPrice] = useState(1.00);
    const [quantity, setQuantity] = useState(5);
    const [loading, setLoading] = useState(false);
    const [payment, setPayment] = useState(null);
    const [error, setError] = useState('');
    const [checkingPayment, setCheckingPayment] = useState(false);
    const [limits, setLimits] = useState({
        minPrice: 0.50,
        minQuantity: 1
    });

    const { credits, refreshCredits } = useAuth();

    const MIN_PRICE = limits.minPrice;
    const MIN_QUANTITY = limits.minQuantity;

    const totalAmount = unitPrice * quantity;

    useEffect(() => {
        const fetchConfig = async () => {
            try {
                const config = await paymentsAPI.getPaymentConfig();
                setLimits({
                    minPrice: config.min_price_per_credit,
                    minQuantity: config.min_quantity
                });
                // Atualizar valores iniciais se necessário
                if (unitPrice < config.min_price_per_credit) setUnitPrice(config.min_price_per_credit);
                if (quantity < config.min_quantity) setQuantity(config.min_quantity);
            } catch (err) {
                console.error('Erro ao carregar configurações de pagamento:', err);
            }
        };
        fetchConfig();
    }, []);

    const handleUnitPriceChange = (e) => {
        const value = parseFloat(e.target.value);
        if (value >= MIN_PRICE) {
            setUnitPrice(value);
        }
    };

    const handleQuantityChange = (e) => {
        const value = parseInt(e.target.value);
        if (value >= MIN_QUANTITY) {
            setQuantity(value);
        }
    };

    const handleCreatePix = async () => {
        setError('');
        setLoading(true);

        try {
            const result = await paymentsAPI.createPixPayment(totalAmount, quantity);
            setPayment(result);
        } catch (err) {
            setError(
                getErrorMessage(err, 'Erro ao criar pagamento. Tente novamente.')
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
                    <p>Defina o valor e a quantidade de créditos</p>
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

                            <div className="input-group">
                                <label>Quanto você quer pagar por crédito?</label>
                                <div className="amount-input-wrapper">
                                    <span className="currency">R$</span>
                                    <input
                                        type="number"
                                        value={unitPrice}
                                        onChange={(e) => setUnitPrice(e.target.value)}
                                        onBlur={handleUnitPriceChange}
                                        min={MIN_PRICE}
                                        step="0.01"
                                        disabled={loading}
                                    />
                                    <span className="unit-label">/crédito</span>
                                </div>
                                <small>Mínimo R$ {MIN_PRICE.toFixed(2)}</small>
                            </div>

                            <div className="input-group" style={{ marginTop: '20px' }}>
                                <label>Quantos créditos você quer?</label>
                                <div className="amount-input-wrapper">
                                    <span className="currency">#</span>
                                    <input
                                        type="number"
                                        value={quantity}
                                        onChange={(e) => setQuantity(e.target.value)}
                                        onBlur={handleQuantityChange}
                                        min={MIN_QUANTITY}
                                        step="1"
                                        disabled={loading}
                                    />
                                </div>
                            </div>

                            <div className="total-preview" style={{ marginTop: '30px', textAlign: 'center', background: 'rgba(255,255,255,0.05)', padding: '15px', borderRadius: '12px' }}>
                                <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Total a pagar</div>
                                <div style={{ fontSize: '2rem', fontWeight: '800', color: 'var(--christmas-green)' }}>
                                    R$ {totalAmount.toFixed(2)}
                                </div>
                            </div>
                        </div>

                        <div className="credits-preview">
                            <span className="preview-icon">✨</span>
                            <span className="preview-text">
                                Você receberá <strong>{quantity} créditos</strong>
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
