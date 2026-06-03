import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import Constants from 'expo-constants';

export const getDefaultApiBase = () => {
    // Expo Go/dev server host, e.g. "192.168.1.22:8081"
    const hostUri = Constants?.expoConfig?.hostUri || Constants?.expoGoConfig?.debuggerHost;
    if (hostUri) {
        const host = hostUri.split(':')[0];
        if (host) return `http://${host}:8000/api/v1`;
    }
    return 'http://localhost:8000/api/v1';
};

// Prefer EXPO_PUBLIC_API_BASE_URL, fallback to auto-detected dev host.
export const API_BASE = process.env.EXPO_PUBLIC_API_BASE_URL || getDefaultApiBase();

const api = axios.create({
    baseURL: API_BASE,
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' },
});

// Add auth token to every request
api.interceptors.request.use(async (config) => {
    try {
        const token = await SecureStore.getItemAsync('auth_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
    } catch (e) {
        // SecureStore not available (web)
    }
    return config;
});

// Handle 401 errors
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            try {
                await SecureStore.deleteItemAsync('auth_token');
            } catch (e) { }
        }
        return Promise.reject(error);
    }
);

export default api;
