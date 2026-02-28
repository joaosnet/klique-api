import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import MagicLinkCallback from './pages/MagicLinkCallback';
import DomainsPage from './pages/DomainsPage';
import CardSwipePage from './pages/CardSwipePage';
import TrainingPage from './pages/TrainingPage';
import DashboardPage from './pages/DashboardPage';
import ProfilePage from './pages/ProfilePage';
import BottomNav from './components/Layout/BottomNav';
import GamifiedLoader from './components/Layout/GamifiedLoader';
import './index.css';


function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    <GamifiedLoader label="Carregando..." />
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<DomainsPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/magic-login" element={<MagicLinkCallback />} />
      <Route path="/criar/:domainId" element={<CardSwipePage />} />
      <Route path="/treinar" element={<ProtectedRoute><TrainingPage /></ProtectedRoute>} />
      <Route path="/oracle" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/perfil" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

import { useDynamicStatusBar } from './hooks/useDynamicStatusBar';
import { useThemeInit } from './hooks/useThemeInit';

function DynamicStatusBarHandler() {
  useDynamicStatusBar();
  useThemeInit();
  return null;
}

export default function App() {
  return (
    <BrowserRouter>
      <DynamicStatusBarHandler />
      <AuthProvider>
        <div className="min-h-screen flex flex-col" style={{ background: 'var(--bg-app)', transition: 'background-color 0.3s ease' }}>
          <main className="flex-1 pb-24 relative">
            <AppRoutes />
          </main>
          <BottomNav />
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
