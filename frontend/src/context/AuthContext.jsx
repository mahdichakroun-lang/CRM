import { createContext, useContext, useState, useEffect, useCallback } from 'react';
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
        const token = localStorage.getItem('token');
        if (!token) { setLoading(false); return null; }
        try {
            const r = await api.get('/auth/me');
            setUser(r.data);
            return r.data;
        } catch {
            localStorage.removeItem('token');
            setUser(null);
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchMe(); }, [fetchMe]);

    const login = async (email, password) => {
        const r = await api.post('/auth/login', { email, password });
        localStorage.setItem('token', r.data.access_token);
        setLoading(true);          // ← AppLayout will show spinner while we fetch user
        const userData = await fetchMe();
        return userData;
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
        window.location.href = '/login';
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
