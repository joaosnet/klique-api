import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import './BottomNav.css';
import { useAuth } from '../../context/AuthContext';
import ThemeSettingsModal from './ThemeSettingsModal';
import { IconDomains, IconTrain, IconDashboard, IconVisual, IconProfile } from '../Icons/NavIcons';

export default function BottomNav() {
    const { isAuthenticated } = useAuth();
    const [showThemeModal, setShowThemeModal] = useState(false);

    if (!isAuthenticated) return null;

    return (
        <>
            <nav className="bottom-nav">
                <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end>
                    {({ isActive }) => (
                        <>
                            <IconDomains active={isActive} width={24} height={24} />
                            <span>Domínios</span>
                        </>
                    )}
                </NavLink>

                <NavLink to="/treinar" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    {({ isActive }) => (
                        <>
                            <IconTrain active={isActive} width={24} height={24} />
                            <span>Treinar</span>
                        </>
                    )}
                </NavLink>

                <NavLink to="/oracle" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    {({ isActive }) => (
                        <>
                            <IconDashboard active={isActive} width={24} height={24} />
                            <span>Dashboard</span>
                        </>
                    )}
                </NavLink>

                <button onClick={() => setShowThemeModal(true)} className={`nav-item ${showThemeModal ? 'active' : ''}`}>
                    <IconVisual active={showThemeModal} width={24} height={24} />
                    <span>Visual</span>
                </button>

                <NavLink to="/perfil" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    {({ isActive }) => (
                        <>
                            <IconProfile active={isActive} width={24} height={24} />
                            <span>Perfil</span>
                        </>
                    )}
                </NavLink>
            </nav>
            {showThemeModal && <ThemeSettingsModal onClose={() => setShowThemeModal(false)} />}
        </>
    );
}
