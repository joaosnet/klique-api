import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor para adicionar token de autenticação
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Interceptor para tratar erros de autenticação
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// ========================================
// Auth API
// ========================================

export const authAPI = {
    login: async (email, password) => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await api.post('/token', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
        return response.data;
    },

    register: async (name, email, password) => {
        const response = await api.post('/auth/register', { name, email, password });
        return response.data;
    },

    loginWithGoogle: async (googleToken) => {
        const response = await api.post('/auth/google', { token: googleToken });
        return response.data;
    },

    loginWithApple: async (appleToken, name) => {
        const response = await api.post('/auth/apple', { token: appleToken, name });
        return response.data;
    },

    requestOTP: async (phoneNumber, method = 'whatsapp') => {
        const response = await api.post('/auth/otp/request', { phone_number: phoneNumber, method });
        return response.data;
    },

    verifyOTP: async (phoneNumber, code) => {
        const response = await api.post('/auth/otp/verify', { phone_number: phoneNumber, code });
        return response.data;
    },

    requestMagicLink: async (email) => {
        const response = await api.post('/auth/magic-link/request', { email });
        return response.data;
    },

    verifyMagicLink: async (token) => {
        const response = await api.post('/auth/magic-link/verify', { token });
        return response.data;
    },

    getPasskeyRegistrationOptions: async () => {
        const response = await api.post('/auth/passkey/register/options');
        return response.data;
    },

    verifyPasskeyRegistration: async (registrationId, credential) => {
        const response = await api.post('/auth/passkey/register/verify', { registration_id: registrationId, credential });
        return response.data;
    },

    getPasskeyAuthenticationOptions: async (email) => {
        const response = await api.post('/auth/passkey/authenticate/options', null, { params: { email } });
        return response.data;
    },

    verifyPasskeyAuthentication: async (authenticationId, credential) => {
        const response = await api.post('/auth/passkey/authenticate/verify', { authentication_id: authenticationId, credential });
        return response.data;
    },

    lazyRegister: async () => {
        const response = await api.post('/auth/lazy');
        return response.data;
    },

    validateToken: async () => {
        const response = await api.post('/auth/valid_token');
        return response.data;
    },

    logout: async () => {
        const response = await api.post('/auth/logout');
        localStorage.removeItem('access_token');
        return response.data;
    },

    getCurrentUser: async () => {
        const response = await api.get('/users/me/');
        return response.data;
    },
};

// ========================================
// Credits API
// ========================================

export const creditsAPI = {
    getBalance: async () => {
        const response = await api.get('/api/credits/balance');
        return response.data;
    },

    getHistory: async (limit = 50) => {
        const response = await api.get(`/api/credits/history?limit=${limit}`);
        return response.data;
    },
};

// ========================================
// Payments API
// ========================================

export const paymentsAPI = {
    getPaymentConfig: async () => {
        const response = await api.get('/api/payments/config');
        return response.data;
    },

    createPixPayment: async (amount, creditsCount) => {
        const response = await api.post('/api/payments/pix/create', { amount, credits_count: creditsCount });
        return response.data;
    },

    getPaymentStatus: async (paymentId) => {
        const response = await api.get(`/api/payments/status/${paymentId}`);
        return response.data;
    },
};

// ========================================
// OmniFlash — Domains API
// ========================================

export const domainsAPI = {
    list: async () => {
        const response = await api.get('/api/domains/');
        return response.data;
    },

    create: async (name, theme) => {
        const response = await api.post('/api/domains/', { name, theme });
        return response.data;
    },

    getOne: async (domainId) => {
        const response = await api.get(`/api/domains/${domainId}`);
        return response.data;
    },

    update: async (domainId, data) => {
        const response = await api.put(`/api/domains/${domainId}`, data);
        return response.data;
    },

    remove: async (domainId) => {
        const response = await api.delete(`/api/domains/${domainId}`);
        return response.data;
    },

    regenerateImage: async (domainId) => {
        const response = await api.post(`/api/domains/${domainId}/regenerate-image`);
        return response.data;
    },

    improveImage: async (domainId, stylePrompt) => {
        const response = await api.post(`/api/domains/${domainId}/improve-image`, { style_prompt: stylePrompt });
        return response.data;
    },

    uploadImage: async (domainId, file) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post(`/api/domains/${domainId}/upload-image`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    removeImage: async (domainId) => {
        const response = await api.delete(`/api/domains/${domainId}/image`);
        return response.data;
    },
};

// ========================================
// OmniFlash — Cards API
// ========================================

/**
 * Utilitário interno para processar um stream SSE.
 * Chama onProgress(data) para eventos 'progress' e resolve com o
 * payload do evento 'complete'. Rejeita em 'error'.
 */
async function _readSSEStream(response, onProgress) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let eventType = '';
    let eventData = '';
    let buffer = '';
    let result = null;

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
            if (line.startsWith('event: ')) {
                eventType = line.slice(7).trim();
            } else if (line.startsWith('data: ')) {
                eventData += line.slice(6);
            } else if (line === '' && eventType) {
                try {
                    if (eventData) {
                        const data = JSON.parse(eventData);
                        if (eventType === 'progress' && onProgress) {
                            onProgress(data);
                        } else if (eventType === 'complete') {
                            result = data;
                        } else if (eventType === 'error') {
                            throw new Error(data.message);
                        }
                    }
                } catch (e) {
                    console.error('SSE Parse Error:', e, eventData);
                    if (e.message !== 'Unexpected end of JSON input') {
                        throw e;
                    }
                }
                eventType = '';
                eventData = '';
            }
        }
    }

    return result;
}

export const cardsAPI = {
    generateStream: async (domainId, context = null, onProgress) => {
        const token = localStorage.getItem('access_token');
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers.Authorization = `Bearer ${token}`;

        const response = await fetch(`${API_BASE_URL}/api/cards/generate-stream`, {
            method: 'POST',
            headers,
            body: JSON.stringify({ domain_id: domainId, context }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Erro ao gerar card');
        }

        return _readSSEStream(response, onProgress);
    },

    swipe: async (cardData, domainId, action, generateImage = true) => {
        const response = await api.post('/api/cards/swipe', {
            card_data: cardData,
            domain_id: domainId,
            action,
            generate_image: generateImage,
        });
        return response.data;
    },

    list: async (domainId) => {
        const response = await api.get(`/api/cards/${domainId}`);
        return response.data;
    },

    update: async (cardId, data) => {
        const response = await api.put(`/api/cards/${cardId}`, data);
        return response.data;
    },

    remove: async (cardId) => {
        const response = await api.delete(`/api/cards/${cardId}`);
        return response.data;
    },

    regenerateImage: async (cardId) => {
        const response = await api.post(`/api/cards/${cardId}/regenerate-image`);
        return response.data;
    },

    improveImage: async (cardId, stylePrompt) => {
        const response = await api.post(`/api/cards/${cardId}/improve-image`, { style_prompt: stylePrompt });
        return response.data;
    },

    uploadImage: async (cardId, file) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post(`/api/cards/${cardId}/upload-image`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    removeImage: async (cardId) => {
        const response = await api.delete(`/api/cards/${cardId}/image`);
        return response.data;
    },
};

// ========================================
// OmniFlash — Profile API
// ========================================

export const profileAPI = {
    getMe: async () => {
        const response = await api.get('/api/profile/me');
        return response.data;
    },

    updateMe: async (data) => {
        const response = await api.put('/api/profile/me', data);
        return response.data;
    },

    generateAvatar: async (prompt) => {
        const formData = new FormData();
        formData.append('prompt', prompt);
        const response = await api.post('/api/profile/me/avatar/generate', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    uploadAvatar: async (file, improve = false, stylePrompt = '') => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('improve', improve);
        if (stylePrompt) formData.append('style_prompt', stylePrompt);
        const response = await api.post('/api/profile/me/avatar/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    removeAvatar: async () => {
        const response = await api.delete('/api/profile/me/avatar');
        return response.data;
    },
};

// ========================================
// OmniFlash — SRS API
// ========================================

export const srsAPI = {
    getDue: async () => {
        const response = await api.get('/api/srs/due');
        return response.data;
    },

    submitReview: async (cardId, performanceRating) => {
        const response = await api.post('/api/srs/review', {
            card_id: cardId,
            performance_rating: performanceRating,
        });
        return response.data;
    },

    getStats: async () => {
        const response = await api.get('/api/srs/stats');
        return response.data;
    },
};

// ========================================
// OmniFlash — Oracle Analytics API
// ========================================

export const oracleAPI = {
    getDashboard: async () => {
        const response = await api.get('/api/oracle/dashboard');
        return response.data;
    },

    getRadar: async () => {
        const response = await api.get('/api/oracle/radar');
        return response.data;
    },

    getActivity: async () => {
        const response = await api.get('/api/oracle/activity');
        return response.data;
    },
};

export default api;
