import React, { useState, useEffect } from 'react';
import {
    View, Text, StyleSheet, FlatList, RefreshControl,
    ActivityIndicator, Platform, TouchableOpacity,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../context/ThemeContext';
import api from '../services/api';

const STATUS_COLORS = { draft: '#64748b', sent: '#3b82f6', accepted: '#10b981', rejected: '#ef4444' };
const STATUS_LABELS = { draft: 'Brouillon', sent: 'Envoyé', accepted: '✅ Accepté', rejected: '❌ Refusé' };

const ClientQuotesScreen = ({ navigation }) => {
    const [quotes, setQuotes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const { isDark, theme } = useTheme();

    const fetchQuotes = async () => {
        try {
            const r = await api.get('/client/quotes');
            setQuotes(r.data || []);
        } catch (e) { console.error(e); }
        finally { setLoading(false); setRefreshing(false); }
    };

    useEffect(() => { fetchQuotes(); }, []);
    const onRefresh = () => { setRefreshing(true); fetchQuotes(); };

    const totalAmount = quotes.reduce((s, q) => s + (q.amount || 0), 0);
    const acceptedAmount = quotes.filter(q => q.status === 'accepted').reduce((s, q) => s + (q.amount || 0), 0);

    const renderQuote = ({ item }) => (
        <View style={[styles.quoteCard, { backgroundColor: theme.sectionBg, borderColor: theme.sectionBorder }]}>
            <View style={styles.quoteHeader}>
                <View style={{ flex: 1 }}>
                    <Text style={[styles.quoteRef, { color: theme.accent }]}>{item.reference || 'N/A'}</Text>
                    <Text style={[styles.quoteDeal, { color: theme.textSecondary }]} numberOfLines={1}>
                        {item.deal_name || 'Projet'}
                    </Text>
                </View>
                <View style={[styles.statusBadge, { backgroundColor: (STATUS_COLORS[item.status] || '#64748b') + '18' }]}>
                    <Text style={[styles.statusText, { color: STATUS_COLORS[item.status] || '#64748b' }]}>
                        {STATUS_LABELS[item.status] || item.status?.toUpperCase()}
                    </Text>
                </View>
            </View>
            <View style={styles.quoteFooter}>
                <Text style={[styles.quoteAmount, { color: theme.text }]}>
                    {(item.amount || 0).toLocaleString()} DT
                </Text>
                <Text style={[styles.quoteDate, { color: theme.textMuted }]}>
                    {item.created_at ? new Date(item.created_at).toLocaleDateString('fr-FR') : ''}
                </Text>
            </View>
        </View>
    );

    if (loading) {
        return <View style={[styles.loadingContainer, { backgroundColor: theme.bg }]}><ActivityIndicator size="large" color={theme.accent} /></View>;
    }

    return (
        <View style={[styles.container, { backgroundColor: theme.bg }]}>
            <StatusBar style={theme.statusBar} />
            <LinearGradient colors={theme.profileGradientBg} style={StyleSheet.absoluteFill} />

            {/* Header */}
            <View style={[styles.screenHeader, { borderBottomColor: theme.sectionBorder }]}>
                <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
                    <Ionicons name="arrow-back" size={24} color={theme.text} />
                </TouchableOpacity>
                <View style={{ flex: 1 }}>
                    <Text style={[styles.screenTitle, { color: theme.text }]}>Mes Devis</Text>
                    <Text style={[styles.screenSubtitle, { color: theme.textSecondary }]}>{quotes.length} devis</Text>
                </View>
            </View>

            {/* Stats Cards */}
            <View style={styles.statsRow}>
                <View style={[styles.statCard, { backgroundColor: theme.sectionBg, borderColor: theme.sectionBorder }]}>
                    <Text style={[styles.statLabel, { color: theme.textSecondary }]}>Total devis</Text>
                    <Text style={[styles.statValue, { color: theme.text }]}>{totalAmount.toLocaleString()}</Text>
                    <Text style={[styles.statSuffix, { color: theme.textMuted }]}>DT</Text>
                </View>
                <View style={[styles.statCard, { backgroundColor: theme.sectionBg, borderColor: theme.sectionBorder }]}>
                    <Text style={[styles.statLabel, { color: theme.textSecondary }]}>Devis acceptés</Text>
                    <Text style={[styles.statValue, { color: '#10b981' }]}>{acceptedAmount.toLocaleString()}</Text>
                    <Text style={[styles.statSuffix, { color: theme.textMuted }]}>DT</Text>
                </View>
            </View>

            {/* Quotes List */}
            <FlatList
                data={quotes}
                renderItem={renderQuote}
                keyExtractor={(item) => String(item.id)}
                contentContainerStyle={styles.listContent}
                showsVerticalScrollIndicator={false}
                refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={theme.accent} />}
                ListEmptyComponent={
                    <View style={styles.emptyState}>
                        <Ionicons name="document-text-outline" size={48} color={theme.textMuted} />
                        <Text style={[styles.emptyText, { color: theme.textSecondary }]}>Aucun devis</Text>
                    </View>
                }
            />
        </View>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1 },
    loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
    screenHeader: {
        flexDirection: 'row', alignItems: 'center', paddingHorizontal: 20,
        paddingTop: Platform.OS === 'ios' ? 60 : 40, paddingBottom: 16, borderBottomWidth: 1,
    },
    backBtn: { width: 40, height: 40, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginRight: 12 },
    screenTitle: { fontSize: 22, fontWeight: '800', letterSpacing: -0.5 },
    screenSubtitle: { fontSize: 13 },

    statsRow: { flexDirection: 'row', gap: 12, paddingHorizontal: 20, paddingTop: 20, paddingBottom: 8 },
    statCard: { flex: 1, borderRadius: 18, padding: 18, borderWidth: 1 },
    statLabel: { fontSize: 12, fontWeight: '600', marginBottom: 8 },
    statValue: { fontSize: 24, fontWeight: '800', letterSpacing: -0.5 },
    statSuffix: { fontSize: 12, fontWeight: '500', marginTop: 2 },

    listContent: { padding: 20 },
    quoteCard: { borderRadius: 18, padding: 18, marginBottom: 12, borderWidth: 1 },
    quoteHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 },
    quoteRef: { fontSize: 15, fontWeight: '800', marginBottom: 2 },
    quoteDeal: { fontSize: 13 },
    statusBadge: { paddingHorizontal: 10, paddingVertical: 5, borderRadius: 10 },
    statusText: { fontSize: 11, fontWeight: '700' },
    quoteFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
    quoteAmount: { fontSize: 20, fontWeight: '800' },
    quoteDate: { fontSize: 12 },

    emptyState: { alignItems: 'center', paddingTop: 60 },
    emptyText: { marginTop: 12, fontSize: 16, fontWeight: '500' },
});

export default ClientQuotesScreen;
