import { useState, useRef, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import { cn } from '../lib/utils';
import { Send, X, MessageCircle, Mic } from 'lucide-react';
import api from '../services/api';

const ChatbotWidget = () => {
    const [open, setOpen] = useState(false);
    const [messages, setMessages] = useState([
        { role: 'bot', text: "Bonjour ! Je suis l'assistant virtuel. Comment puis-je vous aider aujourd'hui ?" },
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [speechSupported, setSpeechSupported] = useState(true);
    const [isListening, setIsListening] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);
    const recognitionRef = useRef(null);
    const { isDark } = useTheme();

    useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, loading]);
    useEffect(() => { if (open) inputRef.current?.focus(); }, [open]);

    useEffect(() => {
        if (typeof window === 'undefined') { setSpeechSupported(false); return; }
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) { setSpeechSupported(false); return; }
        const recognition = new SR();
        recognition.lang = 'fr-FR'; recognition.continuous = false; recognition.interimResults = true;
        recognition.onresult = (e) => { let t = ''; for (let i = e.resultIndex; i < e.results.length; i++) t += e.results[i][0].transcript; setInput(t.trimStart()); };
        recognition.onerror = () => setIsListening(false);
        recognition.onend = () => setIsListening(false);
        recognitionRef.current = recognition;
        return () => { try { recognition.stop(); } catch { } recognitionRef.current = null; };
    }, []);

    const toggleVoice = () => {
        if (!speechSupported || loading) return;
        const r = recognitionRef.current; if (!r) return;
        if (isListening) { try { r.stop(); } catch { } setIsListening(false); return; }
        try { r.start(); setIsListening(true); } catch { setIsListening(false); }
    };

    const sendMessage = async (forcedText) => {
        const text = (forcedText ?? input).trim();
        if (!text || loading) return;
        if (isListening && recognitionRef.current) { try { recognitionRef.current.stop(); } catch { } setIsListening(false); }
        setMessages(prev => [...prev, { role: 'user', text }]); setInput(''); setLoading(true);
        try {
            const res = await api.post('/chatbot', { message: text });
            setMessages(prev => [...prev, { role: 'bot', text: res.data.answer, sources: res.data.sources }]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'bot', text: err.response?.data?.detail || 'Désolé, une erreur est survenue.', error: true }]);
        } finally { setLoading(false); }
    };

    const renderText = (text) => {
        if (!text) return '';
        const parts = text.split(/\*\*([^*]+)\*\*/g);
        return parts.map((part, i) => (i % 2 === 1 ? <strong key={i}>{part}</strong> : part));
    };

    if (!open) {
        return (
            <button onClick={() => setOpen(true)}
                className="fixed bottom-6 right-6 z-[1000] w-14 h-14 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 text-white flex items-center justify-center shadow-2xl shadow-indigo-500/40 hover:scale-105 transition-all duration-300"
                title="Assistant">
                <MessageCircle className="h-6 w-6" />
            </button>
        );
    }

    return (
        <div className={cn(
            'fixed bottom-6 right-6 z-[1000] w-[380px] h-[520px] rounded-2xl overflow-hidden flex flex-col shadow-2xl border',
            isDark ? 'bg-[#1a1a2e] border-white/10' : 'bg-white border-gray-200'
        )}>
            {/* Header */}
            <div className="bg-gradient-to-r from-indigo-500 to-purple-500 px-4 py-3 flex items-center justify-between shrink-0">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center"><MessageCircle className="h-4 w-4 text-white" /></div>
                    <div>
                        <div className="text-white font-bold text-sm">Assistant CRM</div>
                        <div className="text-white/70 text-[11px]">{isListening ? 'Micro actif...' : 'En ligne'}</div>
                    </div>
                </div>
                <button onClick={() => { if (recognitionRef.current) try { recognitionRef.current.stop(); } catch { } setIsListening(false); setOpen(false); }}
                    className="text-white/70 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/10">
                    <X className="h-4 w-4" />
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
                {messages.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={cn(
                            'max-w-[85%] px-3.5 py-2.5 text-[13px] leading-relaxed whitespace-pre-wrap',
                            msg.role === 'user'
                                ? 'bg-indigo-500 text-white rounded-[14px_14px_4px_14px]'
                                : cn('rounded-[14px_14px_14px_4px] border', isDark ? 'bg-white/5 border-white/10 text-gray-200' : 'bg-gray-50 border-gray-200 text-gray-800')
                        )}>
                            {renderText(msg.text)}
                            {msg.error && <span className="text-red-400 text-[11px] block mt-1">Erreur</span>}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className={cn('px-4 py-3 rounded-[14px_14px_14px_4px] border', isDark ? 'bg-white/5 border-white/10' : 'bg-gray-50 border-gray-200')}>
                            <div className="flex items-center gap-2">
                                <div className="flex gap-1">
                                    <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                                    <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                                    <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                                </div>
                                <span className="text-muted-foreground text-xs">Réflexion...</span>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className={cn('px-3 py-2.5 border-t flex gap-2 shrink-0', isDark ? 'bg-white/[0.02] border-white/10' : 'bg-gray-50 border-gray-200')}>
                <input ref={inputRef} value={input} onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                    placeholder={isListening ? 'Je vous écoute...' : 'Posez votre question...'}
                    disabled={loading}
                    className={cn(
                        'flex-1 h-9 px-3 rounded-xl text-sm outline-none border transition-all',
                        isDark ? 'bg-white/5 border-white/10 text-gray-200 placeholder:text-gray-500 focus:border-indigo-500'
                            : 'bg-white border-gray-200 text-gray-800 placeholder:text-gray-400 focus:border-indigo-500'
                    )}
                />
                {speechSupported && (
                    <button onClick={toggleVoice} disabled={loading}
                        className={cn('h-9 w-9 rounded-xl flex items-center justify-center text-white text-sm font-bold transition-all shrink-0',
                            isListening ? 'bg-red-500 hover:bg-red-600' : 'bg-sky-500 hover:bg-sky-600'
                        )}>
                        {isListening ? <span className="text-[10px]">STOP</span> : <Mic className="h-4 w-4" />}
                    </button>
                )}
                <button onClick={() => sendMessage()} disabled={!input.trim() || loading}
                    className="h-9 w-9 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-white flex items-center justify-center transition-all disabled:opacity-40 shrink-0">
                    <Send className="h-4 w-4" />
                </button>
            </div>
        </div>
    );
};

export default ChatbotWidget;
