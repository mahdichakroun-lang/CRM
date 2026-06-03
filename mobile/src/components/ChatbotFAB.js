import React from 'react';
import { TouchableOpacity, StyleSheet, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

/**
 * Floating Action Button for the AI Assistant.
 * Appears as a glowing sparkles icon at the bottom-right of the screen.
 * Just pass onPress from the parent screen.
 */
const ChatbotFAB = ({ onPress }) => {
    return (
        <TouchableOpacity
            style={styles.fabContainer}
            onPress={onPress}
            activeOpacity={0.85}
        >
            <LinearGradient
                colors={['#6366f1', '#8b5cf6', '#a855f7']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.fabGradient}
            >
                <Ionicons name="sparkles" size={26} color="#fff" />
            </LinearGradient>

            {/* Subtle ring */}
            <View style={styles.pulseRing} />
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    fabContainer: {
        position: 'absolute',
        bottom: 28,
        right: 20,
        zIndex: 999,
        shadowColor: '#6366f1',
        shadowOffset: { width: 0, height: 6 },
        shadowOpacity: 0.45,
        shadowRadius: 12,
        elevation: 12,
    },
    fabGradient: {
        width: 58,
        height: 58,
        borderRadius: 29,
        alignItems: 'center',
        justifyContent: 'center',
    },
    pulseRing: {
        position: 'absolute',
        top: -3,
        left: -3,
        width: 64,
        height: 64,
        borderRadius: 32,
        borderWidth: 2,
        borderColor: 'rgba(99, 102, 241, 0.3)',
    },
});

export default ChatbotFAB;
