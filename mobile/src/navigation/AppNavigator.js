import React from 'react';
import { View, ActivityIndicator, StyleSheet, Text, TouchableOpacity } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

import { useAuth } from '../context/AuthContext';
import LoginScreen from '../screens/LoginScreen';
import ProfileScreen from '../screens/ProfileScreen';
import ClientDashboardScreen from '../screens/ClientDashboardScreen';
import ClientTicketsScreen from '../screens/ClientTicketsScreen';
import ClientQuotesScreen from '../screens/ClientQuotesScreen';
import ClientChatbotScreen from '../screens/ClientChatbotScreen';
import ChatbotFAB from '../components/ChatbotFAB';

const Stack = createNativeStackNavigator();

// ═══ Screen shown to non-client users ═══
const NotClientScreen = () => {
    const { logout, user } = useAuth();
    return (
        <View style={styles.notClientContainer}>
            <LinearGradient colors={['#050510', '#0a0a1a', '#050510']} style={StyleSheet.absoluteFill} />
            <View style={styles.notClientContent}>
                <View style={styles.notClientIcon}>
                    <Ionicons name="desktop-outline" size={48} color="#6366f1" />
                </View>
                <Text style={styles.notClientTitle}>Accès réservé aux clients</Text>
                <Text style={styles.notClientDesc}>
                    Cette application mobile est dédiée exclusivement aux clients.{'\n\n'}
                    En tant que <Text style={{ color: '#6366f1', fontWeight: '700' }}>{user?.role?.toUpperCase()}</Text>, veuillez utiliser la <Text style={{ color: '#818cf8', fontWeight: '700' }}>version web</Text> pour accéder au CRM.
                </Text>
                <TouchableOpacity onPress={logout} style={styles.notClientLogout} activeOpacity={0.8}>
                    <Ionicons name="log-out-outline" size={20} color="#ef4444" />
                    <Text style={styles.notClientLogoutText}>Se déconnecter</Text>
                </TouchableOpacity>
            </View>
        </View>
    );
};

// ═══ HOC: wrap a screen and add the floating chatbot FAB ═══
const withFAB = (ScreenComponent) => {
    const WrappedScreen = (props) => (
        <View style={{ flex: 1 }}>
            <ScreenComponent {...props} />
            <ChatbotFAB onPress={() => props.navigation.navigate('ClientChatbot')} />
        </View>
    );
    WrappedScreen.displayName = `withFAB(${ScreenComponent.displayName || ScreenComponent.name || 'Screen'})`;
    return WrappedScreen;
};

const AppNavigator = () => {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <View style={styles.loading}>
                <ActivityIndicator size="large" color="#6366f1" />
                <Text style={styles.loadingText}>Chargement...</Text>
            </View>
        );
    }

    const isClient = user?.role === 'client';

    return (
        <NavigationContainer>
            <Stack.Navigator screenOptions={{ headerShown: false, animation: 'fade' }}>
                {!user ? (
                    <Stack.Screen name="Login" component={LoginScreen} />
                ) : isClient ? (
                    <>
                        <Stack.Screen name="ClientDashboard" component={withFAB(ClientDashboardScreen)} />
                        <Stack.Screen name="ClientTickets" component={withFAB(ClientTicketsScreen)} />
                        <Stack.Screen name="ClientQuotes" component={withFAB(ClientQuotesScreen)} />
                        <Stack.Screen name="ClientChatbot" component={ClientChatbotScreen} />
                        <Stack.Screen name="Profile" component={withFAB(ProfileScreen)} />
                    </>
                ) : (
                    <Stack.Screen name="NotClient" component={NotClientScreen} />
                )}
            </Stack.Navigator>
        </NavigationContainer>
    );
};

const styles = StyleSheet.create({
    loading: {
        flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#050510',
    },
    loadingText: {
        marginTop: 16, color: '#94a3b8', fontSize: 14, fontWeight: '500',
    },
    notClientContainer: {
        flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#050510',
    },
    notClientContent: {
        alignItems: 'center', paddingHorizontal: 40,
    },
    notClientIcon: {
        width: 100, height: 100, borderRadius: 30,
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        alignItems: 'center', justifyContent: 'center',
        marginBottom: 28, borderWidth: 1,
        borderColor: 'rgba(99, 102, 241, 0.15)',
    },
    notClientTitle: {
        fontSize: 24, fontWeight: '800', color: '#f1f5f9',
        marginBottom: 16, textAlign: 'center',
    },
    notClientDesc: {
        fontSize: 15, color: '#94a3b8', textAlign: 'center',
        lineHeight: 24, marginBottom: 32,
    },
    notClientLogout: {
        flexDirection: 'row', alignItems: 'center', gap: 10,
        paddingHorizontal: 28, paddingVertical: 14, borderRadius: 16,
        backgroundColor: 'rgba(239, 68, 68, 0.08)',
        borderWidth: 1, borderColor: 'rgba(239, 68, 68, 0.15)',
    },
    notClientLogoutText: {
        fontSize: 16, fontWeight: '700', color: '#ef4444',
    },
});

export default AppNavigator;
