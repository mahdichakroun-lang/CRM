import React, { useState, useEffect, useCallback } from 'react';
import {
    View, Text, StyleSheet, ScrollView, RefreshControl, TouchableOpacity,
    ActivityIndicator, Platform, Modal, TextInput, Alert, FlatList,
    KeyboardAvoidingView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../context/ThemeContext';
import api from '../services/api';

const PRIORITY_COLORS = { low: '#10b981', medium: '#3b82f6', high: '#f59e0b', urgent: '#ef4444' };
const STATUS_COLORS = { open: '#3b82f6', in_progress: '#06b6d4', waiting_customer: '#f59e0b', resolved: '#10b981', closed: '#64748b' };
const STATUS_LABELS = { open: 'Ouvert', in_progress: 'En cours', waiting_customer: 'En attente', resolved: 'Résolu', closed: 'Fermé' };
const CATEGORY_OPTIONS = [
    { value: 'bug', label: '🐛 Bug' },
    { value: 'support', label: '🛟 Support' },
    { value: 'question', label: '❓ Question' },
    { value: 'feature_request', label: '✨ Fonctionnalité' },
    { value: 'incident', label: '⚠️ Incident' },
    { value: 'other', label: '📌 Autre' },
];
const PRIORITY_OPTIONS = [
    { value: 'low', label: 'Faible' },
    { value: 'medium', label: 'Moyen' },
    { value: 'high', label: 'Élevé' },
    { value: 'urgent', label: 'Urgent' },
];

const ClientTicketsScreen = ({ navigation }) => {
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [createModal, setCreateModal] = useState(false);
    const [detailModal, setDetailModal] = useState(false);
    const [selectedTicket, setSelectedTicket] = useState(null);
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [sendingMessage, setSendingMessage] = useState(false);
    const [creating, setCreating] = useState(false);
    const { isDark, theme } = useTheme();

    // Create form state
    const [formSubject, setFormSubject] = useState('');
    const [formCategory, setFormCategory] = useState('support');
    const [formPriority, setFormPriority] = useState('medium');
    const [formDescription, setFormDescription] = useState('');
    const [showCatPicker, setShowCatPicker] = useState(false);
    const [showPrioPicker, setShowPrioPicker] = useState(false);

    const fetchTickets = async () => {
        try {
            const r = await api.get('/client/tickets');
            setTickets(r.data || []);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => { fetchTickets(); }, []);
    const onRefresh = () => { setRefreshing(true); fetchTickets(); };

    const openTicketDetail = async (ticket) => {
        setSelectedTicket(ticket);
        setDetailModal(true);
        try {
            const r = await api.get(`/client/tickets/${ticket.id}/messages`);
            setMessages(r.data || []);
        } catch { setMessages([]); }
    };

    const handleSendMessage = async () => {
        if (!newMessage.trim()) return;
        setSendingMessage(true);
        try {
            await api.post(`/client/tickets/${selectedTicket.id}/messages`, { message: newMessage });
            setNewMessage('');
            const r = await api.get(`/client/tickets/${selectedTicket.id}/messages`);
            setMessages(r.data || []);
        } catch {
            Alert.alert('Erreur', 'Impossible d\'envoyer le message.');
        } finally {
            setSendingMessage(false);
        }
    };

    const handleCreateTicket = async () => {
        if (!formSubject.trim()) {
            Alert.alert('Erreur', 'Le sujet est requis.');
            return;
        }
        setCreating(true);
        try {
            await api.post('/client/tickets', {
                subject: formSubject,
                category: formCategory,
                priority: formPriority,
                description: formDescription,
            });
            Alert.alert('✅ Succès', 'Ticket créé avec succès !');
            setCreateModal(false);
            setFormSubject(''); setFormDescription('');
            setFormCategory('support'); setFormPriority('medium');
            fetchTickets();
        } catch {
            Alert.alert('Erreur', 'Impossible de créer le ticket.');
        } finally {
            setCreating(false);
        }
    };

    const renderTicket = ({ item }) => (
        <TouchableOpacity
            style={[styles.ticketCard, { backgroundColor: theme.sectionBg, borderColor: theme.sectionBorder }]}
            onPress={() => openTicketDetail(item)}
            activeOpacity={0.7}
        >
            <View style={styles.ticketHeader}>
                <Text style={[styles.ticketId, { color: theme.textMuted }]}>#{item.id}</Text>
                <View style={[styles.statusBadge, { backgroundColor: (STATUS_COLORS[item.status] || '#64748b') + '20' }]}>
                    <View style={[styles.statusDot, { backgroundColor: STATUS_COLORS[item.status] || '#64748b' }]} />
                    <Text style={[styles.statusText, { color: STATUS_COLORS[item.status] || '#64748b' }]}>
                        {STATUS_LABELS[item.status] || item.status}
                    </Text>
                </View>
            </View>
            <Text style={[styles.ticketSubject, { color: theme.text }]} numberOfLines={2}>{item.subject}</Text>
            <View style={styles.ticketFooter}>
                <View style={[styles.prioTag, { backgroundColor: (PRIORITY_COLORS[item.priority] || '#64748b') + '15' }]}>
                    <Text style={[styles.prioText, { color: PRIORITY_COLORS[item.priority] || '#64748b' }]}>
                        {item.priority?.toUpperCase()}
                    </Text>
                </View>
                <Text style={[styles.ticketCategory, { color: theme.textMuted }]}>
                    {item.category?.replace('_', ' ')}
                </Text>
                <Text style={[styles.ticketDate, { color: theme.textMuted }]}>
                    {item.created_at ? new Date(item.created_at).toLocaleDateString('fr-FR') : ''}
                </Text>
            </View>
        </TouchableOpacity>
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
                    <Text style={[styles.screenTitle, { color: theme.text }]}>Mes Tickets</Text>
                    <Text style={[styles.screenSubtitle, { color: theme.textSecondary }]}>{tickets.length} ticket(s)</Text>
                </View>
                <TouchableOpacity
                    onPress={() => { setFormSubject(''); setFormDescription(''); setCreateModal(true); }}
                    activeOpacity={0.8}
                >
                    <LinearGradient colors={['#10b981', '#059669']} style={styles.createBtn}>
                        <Ionicons name="add" size={22} color="#fff" />
                    </LinearGradient>
                </TouchableOpacity>
            </View>

            {/* Ticket List */}
            <FlatList
                data={tickets}
                renderItem={renderTicket}
                keyExtractor={(item) => String(item.id)}
                contentContainerStyle={styles.listContent}
                showsVerticalScrollIndicator={false}
                refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={theme.accent} />}
                ListEmptyComponent={
                    <View style={styles.emptyState}>
                        <Ionicons name="chatbubbles-outline" size={48} color={theme.textMuted} />
                        <Text style={[styles.emptyText, { color: theme.textSecondary }]}>Aucun ticket</Text>
                    </View>
                }
            />

            {/* ═══ CREATE MODAL ═══ */}
            <Modal visible={createModal} animationType="slide" transparent>
                <View style={styles.modalOverlay}>
                    <View style={[styles.modalContent, { backgroundColor: isDark ? '#0f172a' : '#fff' }]}>
                        <View style={styles.modalHeader}>
                            <Text style={[styles.modalTitle, { color: theme.text }]}>🎫 Nouveau Ticket</Text>
                            <TouchableOpacity onPress={() => setCreateModal(false)}>
                                <Ionicons name="close" size={24} color={theme.textMuted} />
                            </TouchableOpacity>
                        </View>

                        <ScrollView showsVerticalScrollIndicator={false}>
                            <Text style={[styles.fieldLabel, { color: theme.textSecondary }]}>Sujet *</Text>
                            <TextInput
                                style={[styles.modalInput, { backgroundColor: theme.inputBg, borderColor: theme.inputBorder, color: theme.inputText }]}
                                placeholder="Décrivez brièvement votre problème..."
                                placeholderTextColor={theme.placeholder}
                                value={formSubject}
                                onChangeText={setFormSubject}
                            />

                            <View style={{ flexDirection: 'row', gap: 12 }}>
                                <View style={{ flex: 1 }}>
                                    <Text style={[styles.fieldLabel, { color: theme.textSecondary }]}>Catégorie</Text>
                                    <TouchableOpacity
                                        style={[styles.modalInput, styles.pickerBtn, { backgroundColor: theme.inputBg, borderColor: theme.inputBorder }]}
                                        onPress={() => setShowCatPicker(!showCatPicker)}
                                    >
                                        <Text style={{ color: theme.inputText, fontSize: 14 }}>
                                            {CATEGORY_OPTIONS.find(c => c.value === formCategory)?.label}
                                        </Text>
                                        <Ionicons name="chevron-down" size={16} color={theme.textMuted} />
                                    </TouchableOpacity>
                                    {showCatPicker && (
                                        <View style={[styles.pickerList, { backgroundColor: isDark ? '#1e293b' : '#f8fafc', borderColor: theme.sectionBorder }]}>
                                            {CATEGORY_OPTIONS.map(opt => (
                                                <TouchableOpacity key={opt.value} style={styles.pickerItem}
                                                    onPress={() => { setFormCategory(opt.value); setShowCatPicker(false); }}>
                                                    <Text style={{ color: theme.text, fontSize: 14 }}>{opt.label}</Text>
                                                </TouchableOpacity>
                                            ))}
                                        </View>
                                    )}
                                </View>
                                <View style={{ flex: 1 }}>
                                    <Text style={[styles.fieldLabel, { color: theme.textSecondary }]}>Priorité</Text>
                                    <TouchableOpacity
                                        style={[styles.modalInput, styles.pickerBtn, { backgroundColor: theme.inputBg, borderColor: theme.inputBorder }]}
                                        onPress={() => setShowPrioPicker(!showPrioPicker)}
                                    >
                                        <Text style={{ color: PRIORITY_COLORS[formPriority], fontSize: 14, fontWeight: '600' }}>
                                            {PRIORITY_OPTIONS.find(p => p.value === formPriority)?.label}
                                        </Text>
                                        <Ionicons name="chevron-down" size={16} color={theme.textMuted} />
                                    </TouchableOpacity>
                                    {showPrioPicker && (
                                        <View style={[styles.pickerList, { backgroundColor: isDark ? '#1e293b' : '#f8fafc', borderColor: theme.sectionBorder }]}>
                                            {PRIORITY_OPTIONS.map(opt => (
                                                <TouchableOpacity key={opt.value} style={styles.pickerItem}
                                                    onPress={() => { setFormPriority(opt.value); setShowPrioPicker(false); }}>
                                                    <Text style={{ color: PRIORITY_COLORS[opt.value], fontSize: 14, fontWeight: '600' }}>{opt.label}</Text>
                                                </TouchableOpacity>
                                            ))}
                                        </View>
                                    )}
                                </View>
                            </View>

                            <Text style={[styles.fieldLabel, { color: theme.textSecondary }]}>Description</Text>
                            <TextInput
                                style={[styles.modalInput, styles.textArea, { backgroundColor: theme.inputBg, borderColor: theme.inputBorder, color: theme.inputText }]}
                                placeholder="Expliquez le problème en détail..."
                                placeholderTextColor={theme.placeholder}
                                value={formDescription}
                                onChangeText={setFormDescription}
                                multiline
                                numberOfLines={4}
                                textAlignVertical="top"
                            />

                            <TouchableOpacity onPress={handleCreateTicket} disabled={creating} activeOpacity={0.85}>
                                <LinearGradient colors={['#10b981', '#059669']} style={styles.submitBtn}>
                                    {creating ? <ActivityIndicator color="#fff" /> : (
                                        <><Ionicons name="send-outline" size={18} color="#fff" style={{ marginRight: 8 }} /><Text style={styles.submitBtnText}>Envoyer</Text></>
                                    )}
                                </LinearGradient>
                            </TouchableOpacity>
                        </ScrollView>
                    </View>
                </View>
            </Modal>

            {/* ═══ DETAIL MODAL (Conversation) ═══ */}
            <Modal visible={detailModal} animationType="slide" transparent>
                <View style={styles.modalOverlay}>
                    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1, justifyContent: 'flex-end' }}>
                        <View style={[styles.detailContent, { backgroundColor: isDark ? '#0f172a' : '#fff' }]}>
                            {/* Detail Header */}
                            <View style={styles.modalHeader}>
                                <View style={{ flex: 1 }}>
                                    <Text style={[styles.modalTitle, { color: theme.text }]}>Ticket #{selectedTicket?.id}</Text>
                                    <Text style={[{ fontSize: 14, color: theme.textSecondary, marginTop: 2 }]} numberOfLines={1}>{selectedTicket?.subject}</Text>
                                </View>
                                <TouchableOpacity onPress={() => setDetailModal(false)}>
                                    <Ionicons name="close" size={24} color={theme.textMuted} />
                                </TouchableOpacity>
                            </View>

                            {/* Status & Priority badges */}
                            <View style={{ flexDirection: 'row', gap: 8, marginBottom: 16 }}>
                                <View style={[styles.statusBadge, { backgroundColor: (STATUS_COLORS[selectedTicket?.status] || '#64748b') + '20' }]}>
                                    <View style={[styles.statusDot, { backgroundColor: STATUS_COLORS[selectedTicket?.status] || '#64748b' }]} />
                                    <Text style={{ color: STATUS_COLORS[selectedTicket?.status] || '#64748b', fontSize: 12, fontWeight: '600' }}>
                                        {STATUS_LABELS[selectedTicket?.status] || selectedTicket?.status}
                                    </Text>
                                </View>
                                <View style={[styles.prioTag, { backgroundColor: (PRIORITY_COLORS[selectedTicket?.priority] || '#64748b') + '15' }]}>
                                    <Text style={{ color: PRIORITY_COLORS[selectedTicket?.priority] || '#64748b', fontSize: 12, fontWeight: '600' }}>
                                        {selectedTicket?.priority?.toUpperCase()}
                                    </Text>
                                </View>
                            </View>

                            {/* Description */}
                            {selectedTicket?.description ? (
                                <View style={[styles.descBox, { backgroundColor: isDark ? 'rgba(255,255,255,0.03)' : '#f8fafc', borderColor: theme.sectionBorder }]}>
                                    <Text style={[{ fontSize: 14, color: theme.text, lineHeight: 20 }]}>{selectedTicket.description}</Text>
                                </View>
                            ) : null}

                            {/* Messages */}
                            <Text style={[styles.convLabel, { color: theme.textMuted }]}>
                                💬 CONVERSATION ({messages.length})
                            </Text>
                            <FlatList
                                data={messages}
                                keyExtractor={(m, i) => String(m.id || i)}
                                style={{ flex: 1 }}
                                showsVerticalScrollIndicator={false}
                                ListEmptyComponent={
                                    <Text style={[{ textAlign: 'center', marginTop: 20, color: theme.textMuted }]}>Aucun message</Text>
                                }
                                renderItem={({ item: m }) => (
                                    <View style={[styles.msgBubble, { backgroundColor: isDark ? 'rgba(255,255,255,0.03)' : '#f1f5f9', borderColor: theme.sectionBorder }]}>
                                        <View style={styles.msgHeader}>
                                            <View style={[styles.msgAvatar, { backgroundColor: '#10b981' }]}>
                                                <Text style={{ color: '#fff', fontSize: 11, fontWeight: '700' }}>{(m.author_name || 'S')[0]}</Text>
                                            </View>
                                            <Text style={[styles.msgAuthor, { color: theme.text }]}>{m.author_name || 'Support'}</Text>
                                            <Text style={[styles.msgDate, { color: theme.textMuted }]}>
                                                {m.created_at ? new Date(m.created_at).toLocaleString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }) : ''}
                                            </Text>
                                        </View>
                                        <Text style={[{ fontSize: 14, color: theme.text, marginLeft: 34, lineHeight: 20 }]}>{m.message}</Text>
                                    </View>
                                )}
                            />

                            {/* Message Input */}
                            <View style={[styles.msgInputRow, { borderTopColor: theme.sectionBorder }]}>
                                <TextInput
                                    style={[styles.msgInput, { backgroundColor: theme.inputBg, borderColor: theme.inputBorder, color: theme.inputText }]}
                                    placeholder="Écrire un message..."
                                    placeholderTextColor={theme.placeholder}
                                    value={newMessage}
                                    onChangeText={setNewMessage}
                                    multiline
                                />
                                <TouchableOpacity onPress={handleSendMessage} disabled={sendingMessage} activeOpacity={0.8}>
                                    <LinearGradient colors={['#10b981', '#059669']} style={styles.sendBtn}>
                                        {sendingMessage ? <ActivityIndicator size="small" color="#fff" /> :
                                            <Ionicons name="send" size={18} color="#fff" />}
                                    </LinearGradient>
                                </TouchableOpacity>
                            </View>
                        </View>
                    </KeyboardAvoidingView>
                </View>
            </Modal>
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
    createBtn: { width: 44, height: 44, borderRadius: 14, alignItems: 'center', justifyContent: 'center' },

    listContent: { padding: 20 },
    ticketCard: { borderRadius: 18, padding: 18, marginBottom: 12, borderWidth: 1 },
    ticketHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
    ticketId: { fontSize: 12, fontWeight: '600' },
    statusBadge: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 10, gap: 5 },
    statusDot: { width: 6, height: 6, borderRadius: 3 },
    statusText: { fontSize: 11, fontWeight: '600' },
    ticketSubject: { fontSize: 15, fontWeight: '700', marginBottom: 12, lineHeight: 21 },
    ticketFooter: { flexDirection: 'row', alignItems: 'center', gap: 10 },
    prioTag: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
    prioText: { fontSize: 10, fontWeight: '700', letterSpacing: 0.5 },
    ticketCategory: { fontSize: 12, flex: 1 },
    ticketDate: { fontSize: 11 },

    emptyState: { alignItems: 'center', paddingTop: 60 },
    emptyText: { marginTop: 12, fontSize: 16, fontWeight: '500' },

    // Modals
    modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
    modalContent: { borderTopLeftRadius: 28, borderTopRightRadius: 28, padding: 24, maxHeight: '90%' },
    detailContent: { borderTopLeftRadius: 28, borderTopRightRadius: 28, padding: 24, height: '85%' },
    modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 },
    modalTitle: { fontSize: 20, fontWeight: '800' },
    fieldLabel: { fontSize: 12, fontWeight: '600', marginBottom: 6, marginTop: 12, textTransform: 'uppercase', letterSpacing: 0.5 },
    modalInput: { borderWidth: 1, borderRadius: 14, paddingHorizontal: 16, paddingVertical: 12, fontSize: 15 },
    textArea: { height: 100, textAlignVertical: 'top' },
    pickerBtn: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
    pickerList: { borderWidth: 1, borderRadius: 12, marginTop: 4, overflow: 'hidden' },
    pickerItem: { paddingHorizontal: 16, paddingVertical: 12 },
    submitBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', height: 52, borderRadius: 16, marginTop: 20 },
    submitBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },

    // Detail / conversation
    descBox: { borderRadius: 14, padding: 14, marginBottom: 16, borderWidth: 1 },
    convLabel: { fontSize: 11, fontWeight: '700', letterSpacing: 1.5, marginBottom: 12 },
    msgBubble: { borderRadius: 14, padding: 14, marginBottom: 10, borderWidth: 1 },
    msgHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 6, gap: 8 },
    msgAvatar: { width: 26, height: 26, borderRadius: 8, alignItems: 'center', justifyContent: 'center' },
    msgAuthor: { fontSize: 13, fontWeight: '700', flex: 1 },
    msgDate: { fontSize: 10 },
    msgInputRow: { flexDirection: 'row', alignItems: 'flex-end', gap: 10, paddingTop: 14, borderTopWidth: 1 },
    msgInput: { flex: 1, borderWidth: 1, borderRadius: 14, paddingHorizontal: 16, paddingVertical: 10, fontSize: 14, maxHeight: 80 },
    sendBtn: { width: 44, height: 44, borderRadius: 14, alignItems: 'center', justifyContent: 'center' },
});

export default ClientTicketsScreen;
