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

    loginWithGoogle: async (googleToken) => {
        const response = await api.post('/auth/google', { token: googleToken });
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
    createPixPayment: async (amount) => {
        const response = await api.post('/api/payments/pix/create', { amount });
        return response.data;
    },

    getPaymentStatus: async (paymentId) => {
        const response = await api.get(`/api/payments/status/${paymentId}`);
        return response.data;
    },
};

// ========================================
// Christmas Avatar API
// ========================================

export const christmasAPI = {
    generateAvatar: async (imageFile, template, removeBg = false, onProgress) => {
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('template', template);
        formData.append('remove_bg', removeBg);

        // Usar SSE para progresso
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/api/christmas/swap-stream`, {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${token}`,
            },
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao gerar avatar');
        }

        // Processar SSE stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let result = null;

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            let eventType = '';
            let eventData = '';

            for (const line of lines) {
                if (line.startsWith('event: ')) {
                    eventType = line.slice(7).trim();
                } else if (line.startsWith('data: ')) {
                    eventData = line.slice(6).trim();
                } else if (line === '' && eventType && eventData) {
                    try {
                        const data = JSON.parse(eventData);

                        if (eventType === 'progress' && onProgress) {
                            onProgress(data);
                        } else if (eventType === 'complete') {
                            result = data;
                        } else if (eventType === 'error') {
                            throw new Error(data.message);
                        }
                    } catch (e) {
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
    },
};

export default api;
