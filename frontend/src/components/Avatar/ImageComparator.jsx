import { useState, useRef, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import './ImageComparator.css';

export default function ImageComparator({ beforeImage, afterImage }) {
    const { t } = useTranslation();
    const [sliderPosition, setSliderPosition] = useState(50);
    const [isDragging, setIsDragging] = useState(false);
    const containerRef = useRef(null);

    const updateSliderPosition = useCallback((clientX) => {
        if (!containerRef.current) return;

        const rect = containerRef.current.getBoundingClientRect();
        let position = ((clientX - rect.left) / rect.width) * 100;
        // Clamp to 0.1 - 99.9 to avoid division by zero or glitches in CSS calc
        position = Math.max(0.1, Math.min(99.9, position));
        setSliderPosition(position);
    }, []);

    useEffect(() => {
        const handleMouseMove = (e) => {
            if (isDragging) {
                updateSliderPosition(e.clientX);
            }
        };

        const handleMouseUp = () => {
            setIsDragging(false);
        };

        const handleTouchMove = (e) => {
            if (isDragging && e.touches[0]) {
                updateSliderPosition(e.touches[0].clientX);
            }
        };

        const handleTouchEnd = () => {
            setIsDragging(false);
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
        document.addEventListener('touchmove', handleTouchMove);
        document.addEventListener('touchend', handleTouchEnd);

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
            document.removeEventListener('touchmove', handleTouchMove);
            document.removeEventListener('touchend', handleTouchEnd);
        };
    }, [isDragging, updateSliderPosition]);

    const handleMouseDown = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleTouchStart = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleContainerClick = (e) => {
        if (!containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        const position = ((e.clientX - rect.left) / rect.width) * 100;
        setSliderPosition(Math.max(0, Math.min(100, position)));
    };

    return (
        <div
            className="image-comparator"
            ref={containerRef}
            onClick={handleContainerClick}
        >
            <div className="comparator-wrapper">
                {/* Right Side (Background) - Should be AFTER (Result) */}
                <div className="comparator-background">
                    <img
                        src={afterImage}
                        alt={t('avatar.generated')}
                        className="comparator-image"
                    />
                </div>

                {/* Left Side (Overlay) - Should be BEFORE (Original) */}
                <div
                    className="comparator-overlay"
                    style={{
                        width: `${sliderPosition}%`,
                        '--slider-pos': sliderPosition
                    }}
                >
                    <div className="comparator-crop-container">
                        <img
                            src={beforeImage}
                            alt={t('avatar.original')}
                            className="comparator-image fixed-scale"
                        />
                    </div>
                </div>

                {/* Slider Handle */}
                <div
                    className="comparator-slider"
                    style={{ left: `${sliderPosition}%` }}
                    onMouseDown={handleMouseDown}
                    onTouchStart={handleTouchStart}
                >
                    <div className="slider-handle">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M8 5l-5 7 5 7M16 5l5 7-5 7" />
                        </svg>
                    </div>
                </div>

                {/* Labels */}
                <div className="comparator-labels">
                    <span className="label-before">{t('avatar.original')}</span>
                    <span className="label-after">{t('avatar.generated')}</span>
                </div>
            </div>
        </div>
    );
}
