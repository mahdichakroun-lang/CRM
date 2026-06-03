import React, { useEffect, useRef, useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    TextInput,
    KeyboardAvoidingView,
    Platform,
    FlatList,
    ActivityIndicator,
    ScrollView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';

import { useTheme } from '../context/ThemeContext';
import api from '../services/api';

const SUGGESTED_PROMPTS = [
    'Quels services propose FRS ?',
    'Comment ouvrir un ticket support ?',
    'Comment demander un devis ?',
];

const ClientChatbotScreen = ({ navigation }) => {
    const { theme } = useTheme();
    const [messages, setMessages] = useState([
        {
            id: 'welcome',
            role: 'bot',
            text: "Bonjour ! Je suis l'assistant FRS. Posez votre question sur nos services, devis ou support.",
        },
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const listRef = useRef(null);

    useEffect(() => {
        const t = setTimeout(() => {
            listRef.current?.scrollToEnd({ animated: true });
        }, 80);
        return () => clearTimeout(t);
    }, [messages, loading]);

    const sendMessage = async (forcedText) => {
        const text = (forcedText ?? input).trim();
        if (!text || loading) return;

        const userMessage = { id: `u-${Date.now()}`, role: 'user', text };
        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const res = await api.post('/chatbot', { message: text });
            const botMessage = {
                id: `b-${Date.now()}`,
                role: 'bot',
                text: res?.data?.answer || 'Je suis disponible pour vous aider.',
            };
            setMessages((prev) => [...prev, botMessage]);
        } catch (err) {
            const errorText = err?.response?.data?.detail || "Je ne peux pas repondre pour l'instant. Veuillez reessayer.";
            setMessages((prev) => [
                ...prev,
                { id: `e-${Date.now()}`, role: 'bot', text: errorText, error: true },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const renderMessage = ({ item }) => {
        const isUser = item.role === 'user';
        return (
            <View style={[styles.msgRow, { justifyContent: isUser ? 'flex-end' : 'flex-start' }]}>
                <View
                    style={[
                        styles.msgBubble,
                        {
                            backgroundColor: isUser ? '#6366f1' : theme.sectionBg,
                            borderColor: isUser ? '#6366f1' : theme.sectionBorder,
                            borderBottomRightRadius: isUser ? 4 : 16,
                            borderBottomLeftRadius: isUser ? 16 : 4,
                        },
                    ]}
                >
                    <Text style={{ color: isUser ? '#fff' : theme.text, fontSize: 14, lineHeight: 20 }}>
                        {item.text}
                    </Text>
                    {item.error ? (
                        <Text style={{ color: '#ef4444', fontSize: 11, marginTop: 6, fontWeight: '700' }}>
                            ERREUR
                        </Text>
                    ) : null}
                </View>
            </View>
        );
    };

    return (
        <View style={[styles.container, { backgroundColor: theme.bg }]}>
            <StatusBar style={theme.statusBar} />
            <LinearGradient colors={theme.profileGradientBg} style={StyleSheet.absoluteFill} />

            <View style={[styles.screenHeader, { borderBottomColor: theme.sectionBorder }]}>
                <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
                    <Ionicons name="arrow-back" size={24} color={theme.text} />
                </TouchableOpacity>
                <View style={{ flex: 1 }}>
                    <Text style={[styles.screenTitle, { color: theme.text }]}>Assistant IA</Text>
                    <Text style={[styles.screenSubtitle, { color: theme.textSecondary }]}>Chatbot client FRS</Text>
                </View>
                <View style={[styles.headerIcon, { backgroundColor: 'rgba(99, 102, 241, 0.16)' }]}>
                    <Ionicons name="sparkles-outline" size={18} color="#818cf8" />
                </View>
            </View>

            <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={styles.promptRow}
            >
                {SUGGESTED_PROMPTS.map((prompt) => (
                    <TouchableOpacity
                        key={prompt}
                        onPress={() => sendMessage(prompt)}
                        disabled={loading}
                        style={[styles.promptChip, { borderColor: theme.sectionBorder, backgroundColor: theme.sectionBg }]}
                    >
                        <Text style={{ color: theme.textSecondary, fontSize: 12 }}>{prompt}</Text>
                    </TouchableOpacity>
                ))}
            </ScrollView>

            <FlatList
                ref={listRef}
                data={messages}
                renderItem={renderMessage}
                keyExtractor={(item) => item.id}
                contentContainerStyle={styles.messagesContent}
                showsVerticalScrollIndicator={false}
            />

            {loading ? (
                <View style={[styles.loadingBox, { borderTopColor: theme.sectionBorder }]}>
                    <ActivityIndicator size="small" color={theme.accent} />
                    <Text style={{ color: theme.textSecondary, marginLeft: 8, fontSize: 12 }}>
                        Assistant en train de repondre...
                    </Text>
                </View>
            ) : null}

            <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
                <View style={[styles.inputRow, { borderTopColor: theme.sectionBorder }]}>
                    <TextInput
                        style={[
                            styles.input,
                            {
                                backgroundColor: theme.inputBg,
                                borderColor: theme.inputBorder,
                                color: theme.inputText,
                            },
                        ]}
                        placeholder="Posez votre question..."
                        placeholderTextColor={theme.placeholder}
                        value={input}
                        onChangeText={setInput}
                        editable={!loading}
                        multiline
                    />
                    <TouchableOpacity
                        onPress={() => sendMessage()}
                        disabled={loading || !input.trim()}
                        activeOpacity={0.8}
                    >
                        <LinearGradient
                            colors={loading || !input.trim() ? ['#94a3b8', '#94a3b8'] : ['#6366f1', '#4f46e5']}
                            style={styles.sendBtn}
                        >
                            <Ionicons name="send" size={18} color="#fff" />
                        </LinearGradient>
                    </TouchableOpacity>
                </View>
            </KeyboardAvoidingView>
        </View>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1 },
    screenHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 20,
        paddingTop: Platform.OS === 'ios' ? 60 : 40,
        paddingBottom: 16,
        borderBottomWidth: 1,
    },
    backBtn: {
        width: 40,
        height: 40,
        borderRadius: 12,
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 12,
    },
    screenTitle: { fontSize: 22, fontWeight: '800', letterSpacing: -0.5 },
    screenSubtitle: { fontSize: 13 },
    headerIcon: {
        width: 34,
        height: 34,
        borderRadius: 10,
        alignItems: 'center',
        justifyContent: 'center',
    },
    promptRow: {
        paddingHorizontal: 16,
        paddingVertical: 12,
        gap: 8,
    },
    promptChip: {
        paddingHorizontal: 12,
        paddingVertical: 8,
        borderRadius: 999,
        borderWidth: 1,
    },
    messagesContent: {
        paddingHorizontal: 16,
        paddingBottom: 16,
    },
    msgRow: {
        width: '100%',
        marginBottom: 10,
    },
    msgBubble: {
        maxWidth: '88%',
        paddingHorizontal: 14,
        paddingVertical: 10,
        borderWidth: 1,
        borderRadius: 16,
    },
    loadingBox: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 16,
        paddingTop: 8,
    },
    inputRow: {
        flexDirection: 'row',
        alignItems: 'flex-end',
        gap: 10,
        paddingHorizontal: 14,
        paddingTop: 12,
        paddingBottom: Platform.OS === 'ios' ? 26 : 14,
        borderTopWidth: 1,
    },
    input: {
        flex: 1,
        minHeight: 44,
        maxHeight: 100,
        borderWidth: 1,
        borderRadius: 14,
        paddingHorizontal: 14,
        paddingVertical: 10,
        fontSize: 14,
    },
    sendBtn: {
        width: 44,
        height: 44,
        borderRadius: 14,
        alignItems: 'center',
        justifyContent: 'center',
    },
});

export default ClientChatbotScreen;
