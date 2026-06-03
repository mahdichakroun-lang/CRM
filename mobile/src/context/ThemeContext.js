import React, { createContext, useContext, useState, useEffect } from 'react';
import { Appearance } from 'react-native';
import * as SecureStore from 'expo-secure-store';

const ThemeContext = createContext(null);

export const useTheme = () => useContext(ThemeContext);

// ═══ LIGHT THEME — matches web light mode ═══
const lightTheme = {
    isDark: false,
    bg: '#f0f4ff',
    bgGradient: ['#1e3a8a', '#3b82f6', '#6366f1'],
    card: 'rgba(255, 255, 255, 0.92)',
    cardBorder: 'rgba(99, 102, 241, 0.15)',
    text: '#1e293b',
    textSecondary: '#475569',
    textMuted: '#64748b',
    textOnBg: '#ffffff',
    accent: '#6366f1',
    accentLight: '#818cf8',
    inputBg: 'rgba(241, 245, 249, 0.9)',
    inputBorder: 'rgba(99, 102, 241, 0.2)',
    inputBorderFocus: '#6366f1',
    inputText: '#1e293b',
    placeholder: '#94a3b8',
    orb1: 'rgba(99, 102, 241, 0.12)',
    orb2: 'rgba(236, 72, 153, 0.08)',
    orb3: 'rgba(59, 130, 246, 0.08)',
    demoSectionBg: 'rgba(255, 255, 255, 0.85)',
    demoSectionBorder: 'rgba(99, 102, 241, 0.12)',
    demoTitle: '#6366f1',
    demoLabel: '#1e293b',
    demoEmail: '#64748b',
    sectionBg: 'rgba(255, 255, 255, 0.85)',
    sectionBorder: 'rgba(99, 102, 241, 0.1)',
    infoIconBg: 'rgba(99, 102, 241, 0.1)',
    logoutBg: 'rgba(239, 68, 68, 0.06)',
    logoutBorder: 'rgba(239, 68, 68, 0.15)',
    footerColor: '#94a3b8',
    statusBar: 'dark',
    formGradient: ['rgba(255, 255, 255, 0.95)', 'rgba(248, 250, 255, 0.98)'],
    buttonGradient: ['#4f46e5', '#6366f1', '#818cf8'],
    profileGradientBg: ['#f0f4ff', '#e8eeff', '#f0f4ff'],
    poweredByBg: 'rgba(99, 102, 241, 0.08)',
    poweredByBorder: 'rgba(99, 102, 241, 0.15)',
    poweredByText: '#6366f1',
};

// ═══ DARK THEME — matches web dark mode exactly ═══
const darkTheme = {
    isDark: true,
    bg: '#050510',
    bgGradient: ['#050510', '#0a0a1a', '#050510'],
    card: 'rgba(15, 23, 42, 0.85)',
    cardBorder: 'rgba(99, 102, 241, 0.1)',
    text: '#f1f5f9',
    textSecondary: '#94a3b8',
    textMuted: '#64748b',
    textOnBg: '#f1f5f9',
    accent: '#818cf8',
    accentLight: '#6366f1',
    inputBg: 'rgba(15, 23, 42, 0.6)',
    inputBorder: 'rgba(99, 102, 241, 0.08)',
    inputBorderFocus: '#6366f1',
    inputText: '#e2e8f0',
    placeholder: '#475569',
    orb1: 'rgba(99, 102, 241, 0.15)',
    orb2: 'rgba(236, 72, 153, 0.1)',
    orb3: 'rgba(59, 130, 246, 0.1)',
    demoSectionBg: 'rgba(15, 23, 42, 0.7)',
    demoSectionBorder: 'rgba(99, 102, 241, 0.1)',
    demoTitle: '#818cf8',
    demoLabel: '#e2e8f0',
    demoEmail: '#64748b',
    sectionBg: 'rgba(12, 18, 35, 0.7)',
    sectionBorder: 'rgba(255, 255, 255, 0.04)',
    infoIconBg: 'rgba(99, 102, 241, 0.08)',
    logoutBg: 'rgba(239, 68, 68, 0.08)',
    logoutBorder: 'rgba(239, 68, 68, 0.12)',
    footerColor: '#334155',
    statusBar: 'light',
    formGradient: ['rgba(15, 23, 42, 0.85)', 'rgba(15, 23, 42, 0.98)'],
    buttonGradient: ['#4f46e5', '#6366f1', '#818cf8'],
    profileGradientBg: ['#050510', '#0a0a1a', '#050510'],
    poweredByBg: 'rgba(99, 102, 241, 0.08)',
    poweredByBorder: 'rgba(99, 102, 241, 0.12)',
    poweredByText: '#818cf8',
};

export const ThemeProvider = ({ children }) => {
    const [isDark, setIsDark] = useState(true); // default dark like web

    useEffect(() => {
        // Load saved preference
        (async () => {
            try {
                const saved = await SecureStore.getItemAsync('theme_mode');
                if (saved !== null) {
                    setIsDark(saved === 'dark');
                }
            } catch (e) { }
        })();
    }, []);

    const toggleTheme = async () => {
        const newMode = !isDark;
        setIsDark(newMode);
        try {
            await SecureStore.setItemAsync('theme_mode', newMode ? 'dark' : 'light');
        } catch (e) { }
    };

    const theme = isDark ? darkTheme : lightTheme;

    return (
        <ThemeContext.Provider value={{ isDark, toggleTheme, theme }}>
            {children}
        </ThemeContext.Provider>
    );
};
