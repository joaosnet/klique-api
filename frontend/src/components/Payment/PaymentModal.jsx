import { useNavigate } from 'react-router-dom';
import './PaymentModal.css';

export default function PaymentModal({ isOpen, onClose }) {
    const navigate = useNavigate();

    if (!isOpen) return null;

    const handleBuyCredits = () => {
        onClose();
        navigate('/credits');
    };

    return (
        <div className="payment-modal-overlay" onClick={onClose}>
            <div className="payment-modal" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close" onClick={onClose}>
                    ✕
                </button>

                <div className="modal-icon">🎁</div>

                <h2 className="modal-title">
                    Desbloqueie sua imagem!
                </h2>

                <p className="modal-description">
                    Sua imagem está pronta, mas com marca d'água.
                    Compre créditos para baixar em alta qualidade, sem marcas!
                </p>

                <div className="modal-benefits">
                    <div className="benefit">
                        <span className="benefit-icon">✨</span>
                        <span>Imagem em alta resolução</span>
                    </div>
                    <div className="benefit">
                        <span className="benefit-icon">🚫</span>
                        <span>Sem marca d'água</span>
                    </div>
                    <div className="benefit">
                        <span className="benefit-icon">📱</span>
                        <span>Compartilhe nas redes</span>
                    </div>
                </div>

                <button className="btn-buy-credits" onClick={handleBuyCredits}>
                    Comprar Créditos
                </button>

                <button className="btn-maybe-later" onClick={onClose}>
                    Talvez depois
                </button>
            </div>
        </div>
    );
}
