import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Layout/Navbar';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DomainsPage from './pages/DomainsPage';
import CardSwipePage from './pages/CardSwipePage';
import TrainingPage from './pages/TrainingPage';
import OracleDashboardPage from './pages/OracleDashboardPage';
import './index.css';



function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner">⚡</div>
        <p className="mt-4 text-gray-400 text-sm uppercase tracking-widest">Carregando...</p>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<DomainsPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/criar/:domainId" element={<CardSwipePage />} />
      <Route path="/treinar" element={<ProtectedRoute><TrainingPage /></ProtectedRoute>} />
      <Route path="/oracle" element={<ProtectedRoute><OracleDashboardPage /></ProtectedRoute>} />
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
          <Navbar />
          <main className="flex-1">
            <AppRoutes />
          </main>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
