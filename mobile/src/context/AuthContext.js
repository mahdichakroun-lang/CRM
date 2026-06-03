import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import * as SecureStore from 'expo-secure-store';
import api from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within AuthProvider');
    return ctx;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchMe = useCallback(async () => {
        try {
            const token = await SecureStore.getItemAsync('auth_token');
            if (!token) {
                setLoading(false);
                return null;
            }
            const r = await api.get('/auth/me');
            setUser(r.data);
            return r.data;
        } catch (e) {
            await SecureStore.deleteItemAsync('auth_token').catch(() => { });
            setUser(null);
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    // Always show login screen on app start — clear old token
    useEffect(() => {
        const clearOnStart = async () => {
            await SecureStore.deleteItemAsync('auth_token').catch(() => { });
            setUser(null);
            setLoading(false);
        };
        clearOnStart();
    }, []);

    const login = async (email, password) => {
        const r = await api.post('/auth/login', { email, password });
        await SecureStore.setItemAsync('auth_token', r.data.access_token);
        const userData = await fetchMe();
        return userData;
    };

    const logout = async () => {
        await SecureStore.deleteItemAsync('auth_token').catch(() => { });
        setUser(null);
    };

    const updateProfile = async (data) => {
        const r = await api.patch('/auth/me', data);
        setUser(r.data);
        return r.data;
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, updateProfile, refetch: fetchMe }}>
            {children}
        </AuthContext.Provider>
    );
};
