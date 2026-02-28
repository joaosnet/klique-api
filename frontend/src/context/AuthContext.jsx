import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI, creditsAPI } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [credits, setCredits] = useState({ free: 0, paid: 0, total: 0 });
    const [loading, setLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    // Verificar se há token salvo ao carregar
    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem('access_token');
            if (token) {
                try {
                    const userData = await authAPI.getCurrentUser();
                    setUser(userData);
                    setIsAuthenticated(true);
                    await refreshCredits();
                } catch (error) {
                    console.error('Token inválido:', error);
                    localStorage.removeItem('access_token');
                }
            }
            setLoading(false);
        };
        checkAuth();
    }, []);

    const refreshCredits = async () => {
        try {
            const balance = await creditsAPI.getBalance();
            setCredits({
                free: balance.free_credits,
                paid: balance.paid_credits,
                total: balance.total_credits,
                generated: balance.total_generated,
            });
        } catch (error) {
            console.error('Erro ao buscar créditos:', error);
        }
    };

    const login = async (email, password) => {
        const response = await authAPI.login(email, password);
        localStorage.setItem('access_token', response.access_token);

        const userData = await authAPI.getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
        await refreshCredits();

        return response;
    };

    const loginWithGoogle = async (googleToken) => {
        const response = await authAPI.loginWithGoogle(googleToken);
        localStorage.setItem('access_token', response.access_token);

        const userData = await authAPI.getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
        await refreshCredits();

        return response;
    };

    const loginWithApple = async (appleToken, name) => {
        const response = await authAPI.loginWithApple(appleToken, name);
        localStorage.setItem('access_token', response.access_token);

        const userData = await authAPI.getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
        await refreshCredits();

        return response;
    };

    const loginWithOTP = async (phoneNumber, code) => {
        const response = await authAPI.verifyOTP(phoneNumber, code);
        localStorage.setItem('access_token', response.access_token);

        const userData = await authAPI.getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
        await refreshCredits();

        return response;
    };

    const loginWithMagicLink = async (token) => {
        const response = await authAPI.verifyMagicLink(token);
        localStorage.setItem('access_token', response.access_token);

        const userData = await authAPI.getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
        await refreshCredits();

        return response;
    };

    const lazyRegister = async () => {
        const response = await authAPI.lazyRegister();
        localStorage.setItem('access_token', response.access_token);

        const userData = await authAPI.getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
        await refreshCredits();

        return response;
    };

    const logout = async () => {
        try {
            await authAPI.logout();
        } catch (error) {
            console.error('Erro no logout:', error);
        }
        localStorage.removeItem('access_token');
        setUser(null);
        setIsAuthenticated(false);
        setCredits({ free: 0, paid: 0, total: 0 });
    };

    const registerPasskey = async () => {
        try {
            const { options, registration_id } = await authAPI.getPasskeyRegistrationOptions();
            const { startRegistration } = await import('@simplewebauthn/browser');
            const attResp = await startRegistration({ optionsJSON: options });
            await authAPI.verifyPasskeyRegistration(registration_id, attResp);
            const userData = await authAPI.getCurrentUser();
            setUser(userData);
            return true;
        } catch (error) {
            console.error('Falha ao registrar passkey:', error);
            throw error;
        }
    };

    const loginWithPasskey = async (email) => {
        try {
            const { options, authentication_id } = await authAPI.getPasskeyAuthenticationOptions(email);
            const { startAuthentication } = await import('@simplewebauthn/browser');
            const asseResp = await startAuthentication({ optionsJSON: options });

            const response = await authAPI.verifyPasskeyAuthentication(authentication_id, asseResp);
            localStorage.setItem('access_token', response.access_token);

            const userData = await authAPI.getCurrentUser();
            setUser(userData);
            setIsAuthenticated(true);
            await refreshCredits();

            return response;
        } catch (error) {
            console.error('Falha na autenticação com passkey:', error);
            throw error;
        }
    };

    const value = {
        user,
        credits,
        loading,
        isAuthenticated,
        login,
        loginWithGoogle,
        loginWithApple,
        loginWithOTP,
        loginWithMagicLink,
        lazyRegister,
        registerPasskey,
        loginWithPasskey,
        logout,
        refreshCredits,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth deve ser usado dentro de AuthProvider');
    }
    return context;
}

export default AuthContext;
