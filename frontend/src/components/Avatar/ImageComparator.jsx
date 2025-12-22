import { useState, useRef, useEffect, useCallback } from 'react';
import './ImageComparator.css';

export default function ImageComparator({ beforeImage, afterImage }) {
    const [sliderPosition, setSliderPosition] = useState(50);
    const [isDragging, setIsDragging] = useState(false);
    const containerRef = useRef(null);

    const updateSliderPosition = useCallback((clientX) => {
        if (!containerRef.current) return;

        const rect = containerRef.current.getBoundingClientRect();
        let position = ((clientX - rect.left) / rect.width) * 100;
        position = Math.max(0, Math.min(100, position));
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
                {/* Before Image (full width, bottom layer) */}
                <div className="comparator-before">
                    <img
                        src={beforeImage}
                        alt="Antes"
                        className="comparator-image"
                    />
                </div>

                {/* After Image (clipped overlay) */}
                <div
                    className="comparator-overlay"
                    style={{ width: `${sliderPosition}%` }}
                >
                    <img
                        src={afterImage}
                        alt="Depois"
                        className="comparator-image after"
                    />
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
                    <span className="label-before">Antes</span>
                    <span className="label-after">Depois</span>
                </div>
            </div>
        </div>
    );
}
