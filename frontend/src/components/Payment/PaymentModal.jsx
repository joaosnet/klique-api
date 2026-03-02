import { useNavigate } from 'react-router-dom';
import './PaymentModal.css';
import { IconGiftQuest, IconShareRocket, IconSparkBoost, IconWatermarkOff } from '../Icons/ActionIcons';
import { useTranslation } from 'react-i18next';

export default function PaymentModal({ isOpen, onClose }) {
    const navigate = useNavigate();
    const { t } = useTranslation();

    if (!isOpen) return null;

    const handleBuyCredits = () => {
        onClose();
        navigate('/credits');
    };

    return (
        <div className="payment-modal-overlay" onClick={onClose}>
            <div className="payment-modal" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close" onClick={onClose}>
                    ×
                </button>

                <IconGiftQuest className="modal-icon" width={64} height={64} />

                <h2 className="modal-title">
                    {t('payment.title')}
                </h2>

                <p className="modal-description">
                    {t('payment.description')}
                </p>

                <div className="modal-benefits">
                    <div className="benefit">
                        <IconSparkBoost className="benefit-icon" width={20} height={20} />
                        <span>{t('payment.highRes')}</span>
                    </div>
                    <div className="benefit">
                        <IconWatermarkOff className="benefit-icon" width={20} height={20} />
                        <span>{t('payment.noWatermark')}</span>
                    </div>
                    <div className="benefit">
                        <IconShareRocket className="benefit-icon" width={20} height={20} />
                        <span>{t('payment.shareSocial')}</span>
                    </div>
                </div>

                <button className="btn-buy-credits" onClick={handleBuyCredits}>
                    {t('payment.buy')}
                </button>

                <button className="btn-maybe-later" onClick={onClose}>
                    {t('payment.later')}
                </button>
            </div>
        </div>
    );
}
