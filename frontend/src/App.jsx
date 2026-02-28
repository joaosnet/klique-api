import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Layout/Navbar';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DemoPage from './pages/DemoPage';
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
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/demo" element={<DemoPage />} />
      <Route path="/dominios" element={<ProtectedRoute><DomainsPage /></ProtectedRoute>} />
      <Route path="/criar/:domainId" element={<ProtectedRoute><CardSwipePage /></ProtectedRoute>} />
      <Route path="/treinar" element={<ProtectedRoute><TrainingPage /></ProtectedRoute>} />
      <Route path="/oracle" element={<ProtectedRoute><OracleDashboardPage /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {

  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="min-h-screen flex flex-col" style={{ background: '#12121a' }}>
          <Navbar />
          <main className="flex-1">
            <AppRoutes />
          </main>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
