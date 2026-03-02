import { useNavigate } from 'react-router-dom';
import './PaymentModal.css';
import { IconGiftQuest, IconShareRocket, IconSparkBoost, IconWatermarkOff } from '../Icons/ActionIcons';

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

                <IconGiftQuest className="modal-icon" width={64} height={64} />

                <h2 className="modal-title">
                    Desbloqueie sua imagem!
                </h2>

                <p className="modal-description">
                    Sua imagem está pronta, mas com marca d'água.
                    Compre créditos para baixar em alta qualidade, sem marcas!
                </p>

                <div className="modal-benefits">
                    <div className="benefit">
                        <IconSparkBoost className="benefit-icon" width={20} height={20} />
                        <span>Imagem em alta resolução</span>
                    </div>
                    <div className="benefit">
                        <IconWatermarkOff className="benefit-icon" width={20} height={20} />
                        <span>Sem marca d'água</span>
                    </div>
                    <div className="benefit">
                        <IconShareRocket className="benefit-icon" width={20} height={20} />
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
