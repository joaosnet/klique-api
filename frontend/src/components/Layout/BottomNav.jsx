import React from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './BottomNav.css';
import { useAuth } from '../../context/AuthContext';
import { IconDomains, IconTrain, IconDashboard, IconVisual, IconProfile } from '../Icons/NavIcons';

export default function BottomNav() {
    const { isAuthenticated } = useAuth();
    const { t } = useTranslation();

    if (!isAuthenticated) return null;

    return (
        <>
            <nav className="bottom-nav">
                <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end>
                    {({ isActive }) => (
                        <>
                            <IconDomains active={isActive} width={24} height={24} />
                            <span>{t('nav.domains')}</span>
                        </>
                    )}
                </NavLink>

                <NavLink to="/treinar" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    {({ isActive }) => (
                        <>
                            <IconTrain active={isActive} width={24} height={24} />
                            <span>{t('nav.train')}</span>
                        </>
                    )}
                </NavLink>

                <NavLink to="/oracle" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    {({ isActive }) => (
                        <>
                            <IconDashboard active={isActive} width={24} height={24} />
                            <span>{t('nav.dashboard')}</span>
                        </>
                    )}
                </NavLink>

                <NavLink to="/visual" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    {({ isActive }) => (
                        <>
                            <IconVisual active={isActive} width={24} height={24} />
                            <span>{t('nav.visual')}</span>
                        </>
                    )}
                </NavLink>

                <NavLink to="/perfil" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    {({ isActive }) => (
                        <>
                            <IconProfile active={isActive} width={24} height={24} />
                            <span>{t('nav.profile')}</span>
                        </>
                    )}
                </NavLink>
            </nav>
        </>
    );
}
