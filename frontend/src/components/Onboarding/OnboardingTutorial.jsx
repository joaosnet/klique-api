import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import './OnboardingTutorial.css';

const TUTORIAL_STEPS = [
    {
        id: 1,
        target: '[data-tutorial="camera"]',
        title: 'onboarding.step1_title',
        description: 'onboarding.step1_desc',
        position: 'bottom',
    },
    {
        id: 2,
        target: '[data-tutorial="templates"]',
        title: 'onboarding.step2_title',
        description: 'onboarding.step2_desc',
        position: 'top',
    },
    {
        id: 3,
        target: '[data-tutorial="generate"]',
        title: 'onboarding.step3_title',
        description: 'onboarding.step3_desc',
        position: 'top',
    },
    {
        id: 4,
        target: '[data-tutorial="comparator"]',
        title: 'onboarding.step4_title',
        description: 'onboarding.step4_desc',
        position: 'bottom',
    },
    {
        id: 5,
        target: '[data-tutorial="download"]',
        title: 'onboarding.step5_title',
        description: 'onboarding.step5_desc',
        position: 'top',
    },
];

export default function OnboardingTutorial({ onComplete, currentStep = 1 }) {
    const { t } = useTranslation();
    const [step, setStep] = useState(currentStep);
    const [targetRect, setTargetRect] = useState(null);
    const [isVisible, setIsVisible] = useState(true);

    const currentStepData = TUTORIAL_STEPS[step - 1];

    const updateTargetRect = useCallback(() => {
        if (!currentStepData) return;

        const target = document.querySelector(currentStepData.target);
        if (target) {
            const rect = target.getBoundingClientRect();
            setTargetRect({
                top: rect.top + window.scrollY,
                left: rect.left + window.scrollX,
                width: rect.width,
                height: rect.height,
            });
        }
    }, [currentStepData]);

    useEffect(() => {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        updateTargetRect();
        window.addEventListener('resize', updateTargetRect);
        window.addEventListener('scroll', updateTargetRect);

        return () => {
            window.removeEventListener('resize', updateTargetRect);
            window.removeEventListener('scroll', updateTargetRect);
        };
    }, [step, updateTargetRect]);

    // Watch for step completion triggers
    useEffect(() => {
        const observer = new MutationObserver(() => {
            updateTargetRect();
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
        });

        return () => observer.disconnect();
    }, [updateTargetRect]);

    const handleNext = () => {
        if (step < TUTORIAL_STEPS.length) {
            setStep(step + 1);
        } else {
            handleComplete();
        }
    };

    const handleSkip = () => {
        handleComplete();
    };

    const handleComplete = () => {
        setIsVisible(false);
        localStorage.setItem('omniflash_onboarding_complete', 'true');
        onComplete?.();
    };

    // Auto-advance based on user actions
    const advanceToStep = useCallback((newStep) => {
        if (newStep > step && newStep <= TUTORIAL_STEPS.length) {
            setStep(newStep);
        }
    }, [step]);

    // Expose advance function for parent component
    useEffect(() => {
        window.advanceTutorialStep = advanceToStep;
        return () => {
            delete window.advanceTutorialStep;
        };
    }, [advanceToStep]);

    if (!isVisible || !currentStepData || !targetRect) {
        return null;
    }

    const tooltipStyle = {
        top: currentStepData.position === 'bottom'
            ? targetRect.top + targetRect.height + 16
            : targetRect.top - 16,
        left: targetRect.left + targetRect.width / 2,
        transform: currentStepData.position === 'bottom'
            ? 'translateX(-50%)'
            : 'translate(-50%, -100%)',
    };

    return (
        <div className="onboarding-overlay">
            {/* Spotlight cutout */}
            <div
                className="onboarding-spotlight"
                style={{
                    top: targetRect.top - 8,
                    left: targetRect.left - 8,
                    width: targetRect.width + 16,
                    height: targetRect.height + 16,
                }}
            />

            {/* Tooltip */}
            <div className="onboarding-tooltip" style={tooltipStyle}>
                <div className="tooltip-content">
                    <div className="tooltip-step">
                        {t('onboarding.step', { step, total: TUTORIAL_STEPS.length })}
                    </div>
                    <h3 className="tooltip-title">{t(currentStepData.title)}</h3>
                    <p className="tooltip-description">{t(currentStepData.description)}</p>

                    <div className="tooltip-actions">
                        <button className="btn-skip" onClick={handleSkip}>
                            {t('onboarding.skip')}
                        </button>
                        <button className="btn-next" onClick={handleNext}>
                            {step === TUTORIAL_STEPS.length ? t('onboarding.get_started') : t('onboarding.next')}
                        </button>
                    </div>
                </div>

                <div className={`tooltip-arrow tooltip-arrow-${currentStepData.position}`} />
            </div>
        </div>
    );
}

// Hook to check if onboarding is needed
// eslint-disable-next-line react-refresh/only-export-components
export function useOnboarding() {
    const [showOnboarding, setShowOnboarding] = useState(false);

    useEffect(() => {
        const completed = localStorage.getItem('omniflash_onboarding_complete');
        if (!completed) {
            // eslint-disable-next-line react-hooks/set-state-in-effect
            setShowOnboarding(true);
        }
    }, []);

    const completeOnboarding = () => {
        setShowOnboarding(false);
        localStorage.setItem('omniflash_onboarding_complete', 'true');
    };

    const resetOnboarding = () => {
        localStorage.removeItem('omniflash_onboarding_complete');
        setShowOnboarding(true);
    };

    return { showOnboarding, completeOnboarding, resetOnboarding };
}
