import React, { useState } from 'react';
import {
    View, Text, StyleSheet, TouchableOpacity, ScrollView,
    Alert, TextInput, ActivityIndicator, Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const roleConfig = {
    admin: { label: 'Administrateur', icon: 'shield-checkmark', color: '#6366f1', gradient: ['#6366f1', '#4f46e5'] },
    manager: { label: 'Manager', icon: 'trending-up', color: '#ec4899', gradient: ['#ec4899', '#db2777'] },
    commercial: { label: 'Commercial', icon: 'briefcase', color: '#f59e0b', gradient: ['#f59e0b', '#d97706'] },
    support: { label: 'Support', icon: 'headset', color: '#10b981', gradient: ['#10b981', '#059669'] },
    client: { label: 'Client', icon: 'business', color: '#0ea5e9', gradient: ['#0ea5e9', '#0284c7'] },
};

const ProfileScreen = () => {
    const { user, logout, updateProfile } = useAuth();
    const { isDark, toggleTheme, theme } = useTheme();
    const [editing, setEditing] = useState(false);
    const [name, setName] = useState(user?.name || '');
    const [phone, setPhone] = useState(user?.phone || '');
    const [saving, setSaving] = useState(false);

    const role = roleConfig[user?.role] || roleConfig.commercial;

    const handleSave = async () => {
        setSaving(true);
        try {
            await updateProfile({ name, phone });
            setEditing(false);
            Alert.alert('✅ Succès', 'Profil mis à jour avec succès !');
        } catch (err) {
            Alert.alert('Erreur', 'Impossible de mettre à jour le profil.');
        } finally {
            setSaving(false);
        }
    };

    const handleLogout = () => {
        Alert.alert(
            'Déconnexion',
            'Êtes-vous sûr de vouloir vous déconnecter ?',
            [
                { text: 'Annuler', style: 'cancel' },
                { text: 'Déconnexion', style: 'destructive', onPress: logout },
            ]
        );
    };

    const infoItems = [
        { icon: 'mail-outline', label: 'Email', value: user?.email, editable: false },
        { icon: 'person-outline', label: 'Nom complet', value: name, editable: true, setter: setName, field: 'name' },
        { icon: 'call-outline', label: 'Téléphone', value: phone, editable: true, setter: setPhone, field: 'phone' },
        { icon: 'shield-outline', label: 'Rôle', value: role.label, editable: false },
        { icon: 'calendar-outline', label: 'Membre depuis', value: user?.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' }) : 'N/A', editable: false },
    ];

    return (
        <View style={[styles.container, { backgroundColor: theme.bg }]}>
            <StatusBar style={theme.statusBar} />
            <LinearGradient
                colors={theme.profileGradientBg}
                style={StyleSheet.absoluteFill}
            />

            {/* Header gradient glow */}
            <LinearGradient
                colors={[role.gradient[0] + '25', 'transparent']}
                style={styles.headerGlow}
            />

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

            <ScrollView
                contentContainerStyle={styles.scrollContent}
                showsVerticalScrollIndicator={false}
            >
                {/* ═══ PROFILE HEADER ═══ */}
                <View style={styles.profileHeader}>
                    <LinearGradient
                        colors={role.gradient}
                        style={styles.avatar}
                        start={{ x: 0, y: 0 }}
                        end={{ x: 1, y: 1 }}
                    >
                        <Text style={styles.avatarLetter}>
                            {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                        </Text>
                    </LinearGradient>

                    <Text style={[styles.userName, { color: theme.text }]}>{user?.name || 'Utilisateur'}</Text>
                    <Text style={[styles.userEmail, { color: theme.textSecondary }]}>{user?.email}</Text>

                    <View style={[styles.roleBadge, { backgroundColor: role.color + '18' }]}>
                        <Ionicons name={role.icon} size={14} color={role.color} />
                        <Text style={[styles.roleBadgeText, { color: role.color }]}>{role.label}</Text>
                    </View>
                </View>

                {/* ═══ ACCOUNT INFO ═══ */}
                <View style={[styles.section, {
                    backgroundColor: theme.sectionBg,
                    borderColor: theme.sectionBorder,
                }]}>
                    <View style={styles.sectionHeader}>
                        <Text style={[styles.sectionTitle, { color: theme.text }]}>Informations du compte</Text>
                        {!editing ? (
                            <TouchableOpacity onPress={() => setEditing(true)} style={[styles.editButton, { backgroundColor: theme.infoIconBg }]}>
                                <Ionicons name="create-outline" size={16} color={theme.accent} />
                                <Text style={[styles.editButtonText, { color: theme.accent }]}>Modifier</Text>
                            </TouchableOpacity>
                        ) : (
                            <View style={{ flexDirection: 'row', gap: 12 }}>
                                <TouchableOpacity onPress={() => { setEditing(false); setName(user?.name || ''); setPhone(user?.phone || ''); }} style={styles.cancelButton}>
                                    <Text style={[styles.cancelButtonText, { color: theme.textSecondary }]}>Annuler</Text>
                                </TouchableOpacity>
                                <TouchableOpacity onPress={handleSave} disabled={saving} style={styles.saveButton}>
                                    {saving ? (
                                        <ActivityIndicator size="small" color="#fff" />
                                    ) : (
                                        <Text style={styles.saveButtonText}>Sauvegarder</Text>
                                    )}
                                </TouchableOpacity>
                            </View>
                        )}
                    </View>

                    {infoItems.map((item, i) => (
                        <View key={i} style={[styles.infoRow, { borderBottomColor: theme.sectionBorder }]}>
                            <View style={[styles.infoIconBox, { backgroundColor: theme.infoIconBg }]}>
                                <Ionicons name={item.icon} size={18} color={theme.accent} />
                            </View>
                            <View style={styles.infoContent}>
                                <Text style={[styles.infoLabel, { color: theme.textMuted }]}>{item.label}</Text>
                                {editing && item.editable ? (
                                    <TextInput
                                        style={[styles.infoInput, { color: theme.text, borderBottomColor: theme.accent }]}
                                        value={item.value}
                                        onChangeText={item.setter}
                                        placeholder={`Entrez votre ${item.label.toLowerCase()}`}
                                        placeholderTextColor={theme.placeholder}
                                    />
                                ) : (
                                    <Text style={[styles.infoValue, { color: theme.text }]}>{item.value || '—'}</Text>
                                )}
                            </View>
                        </View>
                    ))}
                </View>

                {/* ═══ QUICK STATS ═══ */}
                {user?.role !== 'client' && (
                    <View style={[styles.section, {
                        backgroundColor: theme.sectionBg,
                        borderColor: theme.sectionBorder,
                    }]}>
                        <Text style={[styles.sectionTitle, { color: theme.text }]}>Aperçu rapide</Text>
                        <View style={styles.statsGrid}>
                            {[
                                { icon: 'document-text-outline', label: 'Rôle', value: role.label, color: role.color },
                                { icon: 'business-outline', label: 'Compte', value: user?.account_name || 'CRM', color: '#6366f1' },
                                { icon: 'shield-checkmark-outline', label: 'Statut', value: 'Actif', color: '#10b981' },
                                { icon: 'apps-outline', label: 'App', value: 'Mobile', color: '#ec4899' },
                            ].map((stat, i) => (
                                <View key={i} style={[styles.statCard, {
                                    backgroundColor: isDark ? 'rgba(30, 41, 59, 0.4)' : 'rgba(241, 245, 249, 0.8)',
                                    borderColor: theme.sectionBorder,
                                }]}>
                                    <View style={[styles.statIcon, { backgroundColor: stat.color + '15' }]}>
                                        <Ionicons name={stat.icon} size={20} color={stat.color} />
                                    </View>
                                    <Text style={[styles.statValue, { color: theme.text }]}>{stat.value}</Text>
                                    <Text style={[styles.statLabel, { color: theme.textMuted }]}>{stat.label}</Text>
                                </View>
                            ))}
                        </View>
                    </View>
                )}

                {/* ═══ APP INFO ═══ */}
                <View style={[styles.section, {
                    backgroundColor: theme.sectionBg,
                    borderColor: theme.sectionBorder,
                }]}>
                    <Text style={[styles.sectionTitle, { color: theme.text }]}>Application</Text>
                    {[
                        { icon: 'phone-portrait-outline', label: 'Version', value: '1.0.0' },
                        { icon: 'globe-outline', label: 'Plateforme', value: Platform.OS === 'ios' ? 'iOS' : 'Android' },
                        { icon: 'server-outline', label: 'Backend', value: 'Connecté', color: '#10b981' },
                    ].map((item, i) => (
                        <View key={i} style={[styles.infoRow, { borderBottomColor: theme.sectionBorder }]}>
                            <View style={[styles.infoIconBox, { backgroundColor: theme.infoIconBg }]}>
                                <Ionicons name={item.icon} size={18} color={theme.textMuted} />
                            </View>
                            <View style={styles.infoContent}>
                                <Text style={[styles.infoLabel, { color: theme.textMuted }]}>{item.label}</Text>
                                <Text style={[styles.infoValue, item.color && { color: item.color }, !item.color && { color: theme.text }]}>{item.value}</Text>
                            </View>
                        </View>
                    ))}
                </View>

                {/* ═══ LOGOUT BUTTON ═══ */}
                <TouchableOpacity onPress={handleLogout} style={[styles.logoutButton, {
                    backgroundColor: theme.logoutBg,
                    borderColor: theme.logoutBorder,
                }]} activeOpacity={0.8}>
                    <Ionicons name="log-out-outline" size={20} color="#ef4444" />
                    <Text style={styles.logoutText}>Se Déconnecter</Text>
                </TouchableOpacity>

                <Text style={[styles.footer, { color: theme.footerColor }]}>© 2026 FRS — IT Development Company</Text>
            </ScrollView>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    headerGlow: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: 300,
    },
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
    scrollContent: {
        paddingHorizontal: 20,
        paddingTop: Platform.OS === 'ios' ? 70 : 50,
        paddingBottom: 40,
    },

    // Profile Header
    profileHeader: {
        alignItems: 'center',
        marginBottom: 32,
    },
    avatar: {
        width: 90,
        height: 90,
        borderRadius: 28,
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 16,
        shadowColor: '#6366f1',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.35,
        shadowRadius: 20,
        elevation: 16,
    },
    avatarLetter: {
        fontSize: 38,
        fontWeight: '900',
        color: '#fff',
    },
    userName: {
        fontSize: 26,
        fontWeight: '800',
        marginBottom: 4,
        letterSpacing: -0.5,
    },
    userEmail: {
        fontSize: 14,
        marginBottom: 12,
    },
    roleBadge: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 14,
        paddingVertical: 6,
        borderRadius: 20,
        gap: 6,
    },
    roleBadgeText: {
        fontSize: 13,
        fontWeight: '600',
    },

    // Sections
    section: {
        borderRadius: 20,
        padding: 20,
        marginBottom: 16,
        borderWidth: 1,
    },
    sectionHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 20,
    },
    sectionTitle: {
        fontSize: 17,
        fontWeight: '700',
        letterSpacing: -0.3,
    },
    editButton: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 4,
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 10,
    },
    editButtonText: {
        fontSize: 13,
        fontWeight: '600',
    },
    cancelButton: {
        paddingHorizontal: 14,
        paddingVertical: 6,
        borderRadius: 10,
        backgroundColor: 'rgba(128, 128, 128, 0.1)',
    },
    cancelButtonText: {
        fontSize: 13,
        fontWeight: '600',
    },
    saveButton: {
        paddingHorizontal: 16,
        paddingVertical: 6,
        borderRadius: 10,
        backgroundColor: '#6366f1',
    },
    saveButtonText: {
        fontSize: 13,
        color: '#fff',
        fontWeight: '700',
    },

    // Info rows
    infoRow: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 14,
        borderBottomWidth: 1,
    },
    infoIconBox: {
        width: 40,
        height: 40,
        borderRadius: 12,
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 14,
    },
    infoContent: {
        flex: 1,
    },
    infoLabel: {
        fontSize: 12,
        fontWeight: '500',
        marginBottom: 2,
        textTransform: 'uppercase',
        letterSpacing: 0.5,
    },
    infoValue: {
        fontSize: 15,
        fontWeight: '600',
    },
    infoInput: {
        fontSize: 15,
        fontWeight: '600',
        borderBottomWidth: 1,
        paddingBottom: 4,
        paddingTop: 2,
    },

    // Stats grid
    statsGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 12,
        marginTop: 4,
    },
    statCard: {
        width: '47%',
        borderRadius: 16,
        padding: 16,
        alignItems: 'center',
        borderWidth: 1,
    },
    statIcon: {
        width: 44,
        height: 44,
        borderRadius: 14,
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 10,
    },
    statValue: {
        fontSize: 16,
        fontWeight: '700',
        marginBottom: 2,
    },
    statLabel: {
        fontSize: 11,
        fontWeight: '500',
    },

    // Logout
    logoutButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 10,
        borderRadius: 16,
        paddingVertical: 16,
        marginBottom: 24,
        borderWidth: 1,
    },
    logoutText: {
        fontSize: 16,
        fontWeight: '700',
        color: '#ef4444',
    },

    footer: {
        textAlign: 'center',
        fontSize: 11,
        marginBottom: 16,
    },
});

export default ProfileScreen;
