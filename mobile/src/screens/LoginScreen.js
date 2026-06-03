import React, { useState } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, StyleSheet,
    KeyboardAvoidingView, Platform, ScrollView, Alert,
    ActivityIndicator, Dimensions, Image,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const { width, height } = Dimensions.get('window');

const LoginScreen = () => {
    const [email, setEmail] = useState('admin@crm.com');
    const [password, setPassword] = useState('admin123');
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [focusedField, setFocusedField] = useState(null);
    const { login } = useAuth();
    const { isDark, toggleTheme, theme } = useTheme();

    const handleLogin = async () => {
        if (!email.trim() || !password.trim()) {
            Alert.alert('Erreur', 'Veuillez remplir tous les champs.');
            return;
        }
        setLoading(true);
        try {
            await login(email.trim(), password);
        } catch (err) {
            const msg = err?.response?.data?.detail || 'Email ou mot de passe incorrect.';
            Alert.alert('Erreur de connexion', typeof msg === 'string' ? msg : 'Identifiants invalides.');
        } finally {
            setLoading(false);
        }
    };

    const demoAccounts = [
        { label: 'Admin', email: 'admin@crm.com', pwd: 'admin123', icon: 'shield-checkmark', color: '#6366f1' },
        { label: 'Manager', email: 'fatima@crm.com', pwd: 'fatima123', icon: 'trending-up', color: '#ec4899' },
        { label: 'Commercial', email: 'ahmed@crm.com', pwd: 'ahmed123', icon: 'briefcase', color: '#f59e0b' },
        { label: 'Support', email: 'omar@crm.com', pwd: 'omar1234', icon: 'headset', color: '#10b981' },
        { label: 'Client', email: 'karim@sonatrach.dz', pwd: 'client123', icon: 'business', color: '#0ea5e9' },
    ];

    return (
        <View style={[styles.container, { backgroundColor: theme.bg }]}>
            <StatusBar style={theme.statusBar} />
            <LinearGradient
                colors={theme.bgGradient}
                style={StyleSheet.absoluteFill}
            />

            {/* Decorative orbs */}
            <View style={[styles.orb, styles.orb1, { backgroundColor: theme.orb1 }]} />
            <View style={[styles.orb, styles.orb2, { backgroundColor: theme.orb2 }]} />
            <View style={[styles.orb, styles.orb3, { backgroundColor: theme.orb3 }]} />

            {/* ═══ THEME TOGGLE ═══ */}
            <TouchableOpacity
                onPress={toggleTheme}
                style={[styles.themeToggle, {
                    backgroundColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)',
                    borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)',
                }]}
                activeOpacity={0.7}
            >
                <Ionicons
                    name={isDark ? 'sunny-outline' : 'moon-outline'}
                    size={20}
                    color={isDark ? '#fbbf24' : '#6366f1'}
                />
            </TouchableOpacity>

            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                style={{ flex: 1 }}
            >
                <ScrollView
                    contentContainerStyle={styles.scrollContent}
                    keyboardShouldPersistTaps="handled"
                    showsVerticalScrollIndicator={false}
                >
                    {/* ═══ FRS LOGO ═══ */}
                    <View style={styles.logoSection}>
                        <View style={[styles.logoContainer, {
                            borderColor: isDark ? 'rgba(99, 102, 241, 0.2)' : 'rgba(99, 102, 241, 0.25)',
                        }]}>
                            <Image
                                source={require('../../assets/icon.png')}
                                style={styles.logoImage}
                                resizeMode="contain"
                            />
                        </View>
                        <Text style={[styles.appName, { color: theme.textOnBg }]}>
                            CRM <Text style={[styles.appNameAccent, { color: theme.accent }]}>Mobile</Text>
                        </Text>
                        <Text style={[styles.appDesc, { color: theme.textSecondary }]}>
                            Plateforme de gestion commerciale et support client
                        </Text>
                        <View style={[styles.poweredBy, {
                            backgroundColor: theme.poweredByBg,
                            borderColor: theme.poweredByBorder,
                        }]}>
                            <Text style={[styles.poweredByText, { color: theme.poweredByText }]}>
                                Powered by FRS — IT Development Company
                            </Text>
                        </View>
                    </View>

                    {/* ═══ LOGIN FORM ═══ */}
                    <View style={[styles.formCard, { borderColor: theme.cardBorder }]}>
                        <LinearGradient
                            colors={theme.formGradient}
                            style={styles.formCardBg}
                            start={{ x: 0, y: 0 }}
                            end={{ x: 0, y: 1 }}
                        />

                        <Text style={[styles.formTitle, { color: theme.text }]}>Connexion</Text>
                        <Text style={[styles.formSubtitle, { color: theme.textMuted }]}>Entrez vos identifiants CRM</Text>

                        {/* Email Input */}
                        <View style={[
                            styles.inputWrapper,
                            { backgroundColor: theme.inputBg, borderColor: theme.inputBorder },
                            focusedField === 'email' && { borderColor: theme.inputBorderFocus, backgroundColor: isDark ? 'rgba(15, 23, 42, 0.8)' : 'rgba(255,255,255,1)' },
                        ]}>
                            <Ionicons name="mail-outline" size={20} color={focusedField === 'email' ? theme.inputBorderFocus : theme.textMuted} style={styles.inputIcon} />
                            <TextInput
                                style={[styles.textInput, { color: theme.inputText }]}
                                placeholder="Adresse e-mail"
                                placeholderTextColor={theme.placeholder}
                                value={email}
                                onChangeText={setEmail}
                                keyboardType="email-address"
                                autoCapitalize="none"
                                autoCorrect={false}
                                onFocus={() => setFocusedField('email')}
                                onBlur={() => setFocusedField(null)}
                            />
                        </View>

                        {/* Password Input */}
                        <View style={[
                            styles.inputWrapper,
                            { backgroundColor: theme.inputBg, borderColor: theme.inputBorder },
                            focusedField === 'password' && { borderColor: theme.inputBorderFocus, backgroundColor: isDark ? 'rgba(15, 23, 42, 0.8)' : 'rgba(255,255,255,1)' },
                        ]}>
                            <Ionicons name="lock-closed-outline" size={20} color={focusedField === 'password' ? theme.inputBorderFocus : theme.textMuted} style={styles.inputIcon} />
                            <TextInput
                                style={[styles.textInput, { flex: 1, color: theme.inputText }]}
                                placeholder="Mot de passe"
                                placeholderTextColor={theme.placeholder}
                                value={password}
                                onChangeText={setPassword}
                                secureTextEntry={!showPassword}
                                onFocus={() => setFocusedField('password')}
                                onBlur={() => setFocusedField(null)}
                            />
                            <TouchableOpacity onPress={() => setShowPassword(!showPassword)} style={styles.eyeButton}>
                                <Ionicons name={showPassword ? 'eye-off-outline' : 'eye-outline'} size={20} color={theme.textMuted} />
                            </TouchableOpacity>
                        </View>

                        {/* Login Button */}
                        <TouchableOpacity onPress={handleLogin} disabled={loading} activeOpacity={0.85}>
                            <LinearGradient
                                colors={loading ? ['#3730a3', '#4338ca'] : theme.buttonGradient}
                                style={styles.loginButton}
                                start={{ x: 0, y: 0 }}
                                end={{ x: 1, y: 0 }}
                            >
                                {loading ? (
                                    <ActivityIndicator color="#fff" size="small" />
                                ) : (
                                    <>
                                        <Ionicons name="log-in-outline" size={22} color="#fff" style={{ marginRight: 8 }} />
                                        <Text style={styles.loginButtonText}>Se Connecter</Text>
                                    </>
                                )}
                            </LinearGradient>
                        </TouchableOpacity>
                    </View>

                    {/* ═══ DEMO ACCOUNTS ═══ */}
                    <View style={[styles.demoSection, {
                        backgroundColor: theme.demoSectionBg,
                        borderColor: theme.demoSectionBorder,
                    }]}>
                        <Text style={[styles.demoTitle, { color: theme.demoTitle }]}>COMPTES DE DÉMONSTRATION</Text>
                        {demoAccounts.map((acc, i) => (
                            <TouchableOpacity
                                key={i}
                                style={styles.demoRow}
                                onPress={() => { setEmail(acc.email); setPassword(acc.pwd); }}
                                activeOpacity={0.7}
                            >
                                <View style={[styles.demoIcon, { backgroundColor: acc.color + '18' }]}>
                                    <Ionicons name={acc.icon} size={16} color={acc.color} />
                                </View>
                                <Text style={[styles.demoLabel, { color: theme.demoLabel }]}>{acc.label}</Text>
                                <Text style={[styles.demoEmail, { color: theme.demoEmail }]}>{acc.email}</Text>
                                <Text style={[styles.demoPwd, { color: acc.color }]}>{acc.pwd}</Text>
                            </TouchableOpacity>
                        ))}
                    </View>

                    {/* Footer */}
                    <Text style={[styles.footer, { color: theme.footerColor }]}>© 2026 FRS — IT Development Company</Text>
                </ScrollView>
            </KeyboardAvoidingView>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    scrollContent: {
        flexGrow: 1,
        paddingHorizontal: 24,
        paddingTop: Platform.OS === 'ios' ? 70 : 50,
        paddingBottom: 40,
    },

    // Theme toggle
    themeToggle: {
        position: 'absolute',
        top: Platform.OS === 'ios' ? 54 : 34,
        right: 20,
        zIndex: 100,
        width: 42,
        height: 42,
        borderRadius: 14,
        alignItems: 'center',
        justifyContent: 'center',
        borderWidth: 1,
    },

    // Decorative orbs
    orb: {
        position: 'absolute',
        borderRadius: 999,
        opacity: 0.8,
    },
    orb1: {
        width: 400,
        height: 400,
        top: -100,
        left: -100,
    },
    orb2: {
        width: 300,
        height: 300,
        bottom: 50,
        right: -80,
    },
    orb3: {
        width: 250,
        height: 250,
        top: '40%',
        left: '20%',
    },

    // Logo Section
    logoSection: {
        alignItems: 'center',
        marginBottom: 32,
    },
    logoContainer: {
        width: 110,
        height: 110,
        borderRadius: 28,
        overflow: 'hidden',
        marginBottom: 20,
        shadowColor: '#6366f1',
        shadowOffset: { width: 0, height: 12 },
        shadowOpacity: 0.4,
        shadowRadius: 24,
        elevation: 20,
        borderWidth: 2,
    },
    logoImage: {
        width: '100%',
        height: '100%',
    },
    appName: {
        fontSize: 34,
        fontWeight: '900',
        letterSpacing: -1,
        marginBottom: 8,
    },
    appNameAccent: {},
    appDesc: {
        fontSize: 15,
        textAlign: 'center',
        lineHeight: 22,
        marginBottom: 12,
    },
    poweredBy: {
        paddingHorizontal: 16,
        paddingVertical: 6,
        borderRadius: 20,
        borderWidth: 1,
    },
    poweredByText: {
        fontSize: 11,
        fontWeight: '600',
        letterSpacing: 0.3,
    },

    // Form Card
    formCard: {
        borderRadius: 24,
        padding: 28,
        marginBottom: 24,
        borderWidth: 1,
        overflow: 'hidden',
        position: 'relative',
    },
    formCardBg: {
        ...StyleSheet.absoluteFillObject,
        borderRadius: 24,
    },
    formTitle: {
        fontSize: 24,
        fontWeight: '800',
        marginBottom: 4,
    },
    formSubtitle: {
        fontSize: 14,
        marginBottom: 28,
    },

    // Inputs
    inputWrapper: {
        flexDirection: 'row',
        alignItems: 'center',
        borderRadius: 14,
        borderWidth: 1.5,
        marginBottom: 16,
        paddingHorizontal: 16,
        height: 54,
    },
    inputIcon: {
        marginRight: 12,
    },
    textInput: {
        flex: 1,
        fontSize: 15,
        fontWeight: '500',
    },
    eyeButton: {
        padding: 4,
    },

    // Login Button
    loginButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        height: 56,
        borderRadius: 16,
        marginTop: 8,
        shadowColor: '#6366f1',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.35,
        shadowRadius: 16,
        elevation: 12,
    },
    loginButtonText: {
        color: '#fff',
        fontSize: 17,
        fontWeight: '700',
        letterSpacing: 0.3,
    },

    // Demo Section
    demoSection: {
        borderRadius: 20,
        padding: 20,
        borderWidth: 1,
        marginBottom: 24,
    },
    demoTitle: {
        fontSize: 11,
        fontWeight: '700',
        letterSpacing: 1.5,
        marginBottom: 16,
    },
    demoRow: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 10,
        paddingHorizontal: 8,
        borderRadius: 10,
        marginBottom: 2,
    },
    demoIcon: {
        width: 32,
        height: 32,
        borderRadius: 10,
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 12,
    },
    demoLabel: {
        fontSize: 13,
        fontWeight: '600',
        width: 80,
    },
    demoEmail: {
        fontSize: 11,
        flex: 1,
        fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    },
    demoPwd: {
        fontSize: 12,
        fontWeight: '700',
        fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    },

    footer: {
        textAlign: 'center',
        fontSize: 11,
    },
});

export default LoginScreen;
