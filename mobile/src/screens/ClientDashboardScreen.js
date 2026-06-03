import React, { useState, useEffect } from 'react';
import {
    View, Text, StyleSheet, ScrollView, RefreshControl,
    ActivityIndicator, Platform, TouchableOpacity,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import api from '../services/api';

const ClientDashboardScreen = ({ navigation }) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const { user } = useAuth();
    const { isDark, toggleTheme, theme } = useTheme();

    const fetchDashboard = async () => {
        try {
            const r = await api.get('/client/dashboard');
            setData(r.data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => { fetchDashboard(); }, []);

    const onRefresh = () => { setRefreshing(true); fetchDashboard(); };

    if (loading) {
        return (
            <View style={[styles.loadingContainer, { backgroundColor: theme.bg }]}>
                <ActivityIndicator size="large" color={theme.accent} />
            </View>
        );
    }

    const kpis = [
        { title: 'Tickets ouverts', value: data?.open_tickets || 0, icon: 'alert-circle-outline', color: '#f59e0b', gradient: ['#f59e0b', '#d97706'] },
        { title: 'Tickets résolus', value: data?.resolved_tickets || 0, icon: 'checkmark-circle-outline', color: '#10b981', gradient: ['#10b981', '#059669'] },
        { title: 'Devis reçus', value: data?.total_quotes || 0, icon: 'document-text-outline', color: '#6366f1', gradient: ['#6366f1', '#4f46e5'] },
        { title: 'Total devis', value: `${(data?.total_quotes_value || 0).toLocaleString()} DT`, icon: 'cash-outline', color: '#ec4899', gradient: ['#ec4899', '#db2777'] },
    ];

    const quickActions = [
        { title: 'Mes Tickets', subtitle: `${data?.open_tickets || 0} ouvert(s)`, icon: 'chatbubbles-outline', color: '#10b981', screen: 'ClientTickets' },
        { title: 'Assistant IA', subtitle: 'Poser une question', icon: 'sparkles-outline', color: '#818cf8', screen: 'ClientChatbot' },
        { title: 'Mes Devis', subtitle: `${data?.total_quotes || 0} devis`, icon: 'document-text-outline', color: '#6366f1', screen: 'ClientQuotes' },
        { title: 'Mon Profil', subtitle: 'Voir mon compte', icon: 'person-outline', color: '#ec4899', screen: 'Profile' },
    ];

    return (
        <View style={[styles.container, { backgroundColor: theme.bg }]}>
            <StatusBar style={theme.statusBar} />
            <LinearGradient colors={theme.profileGradientBg} style={StyleSheet.absoluteFill} />

            {/* Theme Toggle */}
            <TouchableOpacity onPress={toggleTheme} style={[styles.themeToggle, {
                backgroundColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)',
                borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)',
            }]} activeOpacity={0.7}>
                <Ionicons name={isDark ? 'sunny-outline' : 'moon-outline'} size={20} color={isDark ? '#fbbf24' : '#6366f1'} />
            </TouchableOpacity>

            <ScrollView
                contentContainerStyle={styles.scrollContent}
                showsVerticalScrollIndicator={false}
                refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={theme.accent} />}
            >
                {/* ═══ HEADER ═══ */}
                <View style={styles.header}>
                    <Text style={[styles.greeting, { color: theme.text }]}>
                        Bienvenue, {user?.name?.split(' ')[0]} 👋
                    </Text>
                    <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
                        Portail client — {data?.account_name || 'Votre entreprise'}
                    </Text>
                </View>

                {/* ═══ KPIs ═══ */}
                <View style={styles.kpiGrid}>
                    {kpis.map((kpi, i) => (
                        <View key={i} style={[styles.kpiCard, {
                            backgroundColor: theme.sectionBg,
                            borderColor: theme.sectionBorder,
                        }]}>
                            <View style={styles.kpiHeader}>
                                <Text style={[styles.kpiTitle, { color: theme.textSecondary }]}>{kpi.title}</Text>
                                <LinearGradient colors={kpi.gradient} style={styles.kpiIconBox}>
                                    <Ionicons name={kpi.icon} size={18} color="#fff" />
                                </LinearGradient>
                            </View>
                            <Text style={[styles.kpiValue, { color: theme.text }]}>
                                {typeof kpi.value === 'number' ? kpi.value : kpi.value}
                            </Text>
                        </View>
                    ))}
                </View>

                {/* ═══ QUICK ACTIONS ═══ */}
                <Text style={[styles.sectionLabel, { color: theme.textMuted }]}>ACCÈS RAPIDE</Text>
                {quickActions.map((action, i) => (
                    <TouchableOpacity
                        key={i}
                        style={[styles.actionCard, {
                            backgroundColor: theme.sectionBg,
                            borderColor: theme.sectionBorder,
                        }]}
                        onPress={() => navigation.navigate(action.screen)}
                        activeOpacity={0.7}
                    >
                        <View style={[styles.actionIcon, { backgroundColor: action.color + '15' }]}>
                            <Ionicons name={action.icon} size={22} color={action.color} />
                        </View>
                        <View style={{ flex: 1 }}>
                            <Text style={[styles.actionTitle, { color: theme.text }]}>{action.title}</Text>
                            <Text style={[styles.actionSubtitle, { color: theme.textSecondary }]}>{action.subtitle}</Text>
                        </View>
                        <Ionicons name="chevron-forward" size={20} color={theme.textMuted} />
                    </TouchableOpacity>
                ))}

                {/* ═══ HELP CARD ═══ */}
                <View style={[styles.helpCard, {
                    backgroundColor: theme.sectionBg,
                    borderColor: theme.sectionBorder,
                }]}>
                    <Ionicons name="help-circle-outline" size={24} color="#10b981" style={{ marginBottom: 12 }} />
                    <Text style={[styles.helpTitle, { color: theme.text }]}>Besoin d'aide ?</Text>
                    <Text style={[styles.helpText, { color: theme.textSecondary }]}>
                        Utilisez "Mes Tickets" pour ouvrir un nouveau ticket de support. Notre équipe vous répondra dans les plus brefs délais.
                    </Text>
                    <Text style={[styles.helpHours, { color: theme.textMuted }]}>
                        Horaires : Dimanche — Jeudi, 8h — 17h
                    </Text>
                </View>

                <Text style={[styles.footer, { color: theme.footerColor }]}>© 2026 FRS — IT Development Company</Text>
            </ScrollView>
        </View>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1 },
    loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
    themeToggle: {
        position: 'absolute', top: Platform.OS === 'ios' ? 54 : 34, right: 20, zIndex: 100,
        width: 42, height: 42, borderRadius: 14, alignItems: 'center', justifyContent: 'center', borderWidth: 1,
    },
    scrollContent: { paddingHorizontal: 20, paddingTop: Platform.OS === 'ios' ? 70 : 50, paddingBottom: 40 },

    header: { marginBottom: 28 },
    greeting: { fontSize: 28, fontWeight: '800', letterSpacing: -0.5, marginBottom: 4 },
    subtitle: { fontSize: 15 },

    kpiGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginBottom: 28 },
    kpiCard: { width: '47%', borderRadius: 20, padding: 18, borderWidth: 1 },
    kpiHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 },
    kpiTitle: { fontSize: 12, fontWeight: '600' },
    kpiIconBox: { width: 36, height: 36, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
    kpiValue: { fontSize: 26, fontWeight: '800', letterSpacing: -0.5 },

    sectionLabel: { fontSize: 11, fontWeight: '700', letterSpacing: 1.5, marginBottom: 14 },
    actionCard: { flexDirection: 'row', alignItems: 'center', padding: 18, borderRadius: 18, borderWidth: 1, marginBottom: 10 },
    actionIcon: { width: 48, height: 48, borderRadius: 16, alignItems: 'center', justifyContent: 'center', marginRight: 16 },
    actionTitle: { fontSize: 16, fontWeight: '700', marginBottom: 2 },
    actionSubtitle: { fontSize: 13 },

    helpCard: { borderRadius: 20, padding: 24, borderWidth: 1, marginTop: 16, marginBottom: 24, alignItems: 'center' },
    helpTitle: { fontSize: 17, fontWeight: '700', marginBottom: 8 },
    helpText: { fontSize: 14, textAlign: 'center', lineHeight: 20, marginBottom: 8 },
    helpHours: { fontSize: 12 },

    footer: { textAlign: 'center', fontSize: 11, marginBottom: 16 },
});

export default ClientDashboardScreen;
