import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import BottomNav from './components/Layout/BottomNav';
import GamifiedLoader from './components/Layout/GamifiedLoader';
import './index.css';

const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const MagicLinkCallback = lazy(() => import('./pages/MagicLinkCallback'));
const DomainsPage = lazy(() => import('./pages/DomainsPage'));
const CardSwipePage = lazy(() => import('./pages/CardSwipePage'));
const TrainingPage = lazy(() => import('./pages/TrainingPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const VisualPage = lazy(() => import('./pages/VisualPage'));


function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <GamifiedLoader label="Carregando..." />;
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function AppRoutes() {
  return (
    <Suspense fallback={<div className="h-screen w-full flex items-center justify-center bg-[var(--bg-app)]"><GamifiedLoader label="A carregar..." /></div>}>
      <Routes>
        <Route path="/" element={<DomainsPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/magic-login" element={<MagicLinkCallback />} />
        <Route path="/criar/:domainId" element={<CardSwipePage />} />
        <Route path="/treinar" element={<ProtectedRoute><TrainingPage /></ProtectedRoute>} />
        <Route path="/oracle" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/visual" element={<ProtectedRoute><VisualPage /></ProtectedRoute>} />
        <Route path="/perfil" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}

import { useDynamicStatusBar } from './hooks/useDynamicStatusBar';
import { useThemeInit } from './hooks/useThemeInit';

function DynamicStatusBarHandler() {
  useDynamicStatusBar();
  useThemeInit();
  return null;
}

function AppShell() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'var(--bg-app)', transition: 'background-color 0.3s ease' }}>
      <main className={`flex-1 relative ${isAuthenticated ? 'pb-24' : ''}`}>
        <AppRoutes />
      </main>
      <BottomNav />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <DynamicStatusBarHandler />
        <AppShell />
      </AuthProvider>
    </BrowserRouter>
  );
}
