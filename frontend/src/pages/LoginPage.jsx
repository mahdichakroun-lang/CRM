import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label, toast } from '../components/ui/shared';
import { Sun, Moon, BarChart3, Headphones, Shield, Rocket, Zap, Globe, Lock, Mail, ArrowRight, Sparkles, Eye, EyeOff } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../components/LanguageSwitcher';

/* ─── keyframe styles injected once ─── */
const injectStyles = () => {
    if (document.getElementById('login-animations')) return;
    const style = document.createElement('style');
    style.id = 'login-animations';
    style.textContent = `
        @keyframes float-slow {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            33% { transform: translateY(-20px) rotate(2deg); }
            66% { transform: translateY(10px) rotate(-1deg); }
        }
        @keyframes float-medium {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-30px) rotate(-3deg); }
        }
        @keyframes shimmer {
            0% { background-position: -200% center; }
            100% { background-position: 200% center; }
        }
        @keyframes gradient-shift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        @keyframes progress-fill {
            from { width: 0%; }
            to { width: 100%; }
        }
        @keyframes fade-up {
            from { opacity: 0; transform: translateY(16px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes particle-float {
            0%, 100% { transform: translateY(0) translateX(0); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(-100vh) translateX(20px); opacity: 0; }
        }
        .login-fade-up { animation: fade-up 0.6s ease-out forwards; }
        .login-shimmer {
            background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.08) 50%, transparent 100%);
            background-size: 200% 100%;
            animation: shimmer 3s infinite;
        }
    `;
    document.head.appendChild(style);
};

const LoginPage = () => {
    const [loading, setLoading] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [activeFeature, setActiveFeature] = useState(0);
    const [emailFocused, setEmailFocused] = useState(false);
    const [passwordFocused, setPasswordFocused] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);
    const { login, user } = useAuth();
    const { isDark, toggleTheme } = useTheme();
    const navigate = useNavigate();
    const { t } = useTranslation();
    const progressRef = useRef(null);

    useEffect(() => { injectStyles(); }, []);

    useEffect(() => {
        const interval = setInterval(() => setActiveFeature(prev => (prev + 1) % 4), 4000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        if (!user) return;
        if (user.role === 'client') navigate('/portal', { replace: true });
        else navigate('/', { replace: true });
    }, [user, navigate]);

    const onSubmit = async (e) => {
        e.preventDefault();
        if (!email || !password) { toast.error('Veuillez remplir tous les champs'); return; }
        setLoading(true);
        try {
            await login(email, password);
            toast.success('Connexion réussie !');
            // Navigation is handled by the useEffect above when user state changes
        } catch (err) {
            const detail = err?.response?.data?.detail || 'Identifiants invalides.';
            toast.error(typeof detail === 'string' ? detail : 'Email ou mot de passe incorrect.');
        } finally { setLoading(false); }
    };

    const features = [
        { icon: BarChart3, title: t('Pipeline Commercial'), desc: t('Suivez leads, deals et devis en temps réel avec des tableaux de bord interactifs'), color: '#818cf8', gradient: 'linear-gradient(135deg, #6366f1, #818cf8)' },
        { icon: Headphones, title: t('Helpdesk Intégré'), desc: t('Gérez vos tickets, SLA et satisfaction client de bout en bout'), color: '#f472b6', gradient: 'linear-gradient(135deg, #ec4899, #f472b6)' },
        { icon: Shield, title: t('Sécurité RBAC'), desc: t("5 rôles avec permissions granulaires et journal d'audit complet"), color: '#fbbf24', gradient: 'linear-gradient(135deg, #f59e0b, #fbbf24)' },
        { icon: Rocket, title: t('Portail Client'), desc: t('Espace dédié pour vos clients avec suivi tickets et devis'), color: '#34d399', gradient: 'linear-gradient(135deg, #10b981, #34d399)' },
    ];

    const ActiveIcon = features[activeFeature].icon;

    /* ─── particles for left panel ─── */
    const particles = Array.from({ length: 20 }, (_, i) => ({
        id: i,
        left: `${Math.random() * 100}%`,
        size: Math.random() * 3 + 1,
        duration: Math.random() * 10 + 8,
        delay: Math.random() * 8,
        opacity: Math.random() * 0.4 + 0.1,
    }));

    return (
        <div className="min-h-screen flex relative overflow-hidden" style={{
            background: isDark
                ? '#06060f'
                : '#0f172a',
        }}>

            {/* ═══ LEFT — Branding ═══ */}
            <div className="flex-1 hidden lg:flex flex-col justify-center items-center relative z-10 overflow-hidden"
                style={{
                    background: isDark
                        ? 'linear-gradient(160deg, #0c0c1d 0%, #131336 40%, #1a1050 70%, #0f0a2e 100%)'
                        : 'linear-gradient(160deg, #1e3a8a 0%, #2563eb 30%, #6366f1 60%, #7c3aed 85%, #6d28d9 100%)',
                    backgroundSize: '400% 400%',
                    animation: 'gradient-shift 15s ease infinite',
                }}
            >
                {/* Floating particles */}
                {particles.map(p => (
                    <div key={p.id} className="absolute rounded-full bg-white pointer-events-none"
                        style={{
                            left: p.left,
                            bottom: '-10px',
                            width: p.size,
                            height: p.size,
                            opacity: p.opacity,
                            animation: `particle-float ${p.duration}s linear ${p.delay}s infinite`,
                        }}
                    />
                ))}

                {/* Mesh overlay */}
                <div className="absolute inset-0 opacity-[0.03]"
                    style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, white 1px, transparent 0)', backgroundSize: '40px 40px' }}
                />

                {/* Glowing orbs */}
                <div className="absolute rounded-full" style={{
                    width: 500, height: 500, top: '-15%', left: '-10%',
                    background: 'radial-gradient(circle, rgba(99,102,241,0.25), transparent 70%)',
                    animation: 'float-slow 8s ease-in-out infinite',
                }} />
                <div className="absolute rounded-full" style={{
                    width: 400, height: 400, bottom: '-10%', right: '-5%',
                    background: 'radial-gradient(circle, rgba(168,85,247,0.2), transparent 70%)',
                    animation: 'float-medium 10s ease-in-out infinite',
                }} />
                <div className="absolute rounded-full" style={{
                    width: 250, height: 250, top: '50%', left: '60%',
                    background: 'radial-gradient(circle, rgba(236,72,153,0.12), transparent 70%)',
                    animation: 'float-slow 12s ease-in-out 2s infinite',
                }} />

                <div className="max-w-[520px] text-center relative z-10 px-8">
                    {/* Logo */}
                    <div className="w-20 h-20 mx-auto mb-6 relative group">
                        <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-indigo-400 to-purple-500 opacity-40 blur-xl group-hover:opacity-60 transition-opacity" />
                        <div className="relative w-full h-full rounded-2xl bg-white p-2.5 shadow-2xl shadow-indigo-500/30 flex items-center justify-center"
                            style={{ transform: 'rotate(-3deg)', transition: 'transform 0.3s ease' }}
                            onMouseEnter={e => e.currentTarget.style.transform = 'rotate(0deg) scale(1.05)'}
                            onMouseLeave={e => e.currentTarget.style.transform = 'rotate(-3deg)'}
                        >
                            <img src="/FRS_logo.jpg" alt="FRS Logo" className="object-contain w-full h-full rounded-xl" />
                        </div>
                    </div>

                    <h1 className="text-white text-[40px] font-black mb-2 tracking-tight leading-none">
                        CRM{' '}
                        <span style={{
                            background: 'linear-gradient(135deg, #c7d2fe 0%, #e9d5ff 50%, #fbcfe8 100%)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                        }}>Internal</span>
                    </h1>
                    <p className="text-white/50 text-sm mb-10 leading-relaxed max-w-[400px] mx-auto">
                        {t('Plateforme unifiée de gestion commerciale, support client et suivi des performances')}
                    </p>

                    {/* ── Active Feature Showcase ── */}
                    <div className="rounded-2xl p-6 mb-6 text-left relative overflow-hidden transition-all duration-700"
                        style={{
                            background: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(255,255,255,0.08)',
                            border: `1px solid ${isDark ? 'rgba(255,255,255,0.06)' : 'rgba(255,255,255,0.15)'}`,
                            backdropFilter: 'blur(20px)',
                        }}
                    >
                        {/* Shimmer overlay */}
                        <div className="absolute inset-0 login-shimmer pointer-events-none" />

                        <div className="flex items-start gap-4 relative z-10">
                            <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
                                style={{ background: features[activeFeature].gradient, boxShadow: `0 8px 24px ${features[activeFeature].color}40` }}>
                                <ActiveIcon className="h-6 w-6 text-white" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="text-white font-bold text-base mb-1">{features[activeFeature].title}</div>
                                <div className="text-white/50 text-[13px] leading-relaxed">{features[activeFeature].desc}</div>
                            </div>
                        </div>

                        {/* Progress bar */}
                        <div className="mt-4 h-[2px] rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
                            <div key={activeFeature} className="h-full rounded-full"
                                style={{
                                    background: features[activeFeature].gradient,
                                    animation: 'progress-fill 4s linear forwards',
                                }}
                            />
                        </div>
                    </div>

                    {/* ── Feature Dots Navigation ── */}
                    <div className="flex justify-center gap-6 mb-8">
                        {features.map((f, i) => {
                            const Icon = f.icon;
                            return (
                                <button key={i} onClick={() => setActiveFeature(i)}
                                    className="flex flex-col items-center gap-1.5 transition-all duration-300 group"
                                    style={{ opacity: activeFeature === i ? 1 : 0.4 }}
                                >
                                    <div className="w-9 h-9 rounded-lg flex items-center justify-center transition-all duration-300"
                                        style={{
                                            background: activeFeature === i ? `${f.color}25` : 'rgba(255,255,255,0.05)',
                                            border: activeFeature === i ? `1px solid ${f.color}40` : '1px solid transparent',
                                            transform: activeFeature === i ? 'scale(1.1)' : 'scale(1)',
                                        }}
                                    >
                                        <Icon className="h-4 w-4" style={{ color: activeFeature === i ? f.color : 'rgba(255,255,255,0.5)' }} />
                                    </div>
                                </button>
                            );
                        })}
                    </div>

                    {/* ── Stats ── */}
                    <div className="flex justify-center gap-10">
                        {[
                            { value: '5', label: t('Rôles'), icon: Shield },
                            { value: '∞', label: t('Modulaire'), icon: Zap },
                            { value: '24/7', label: t('Support'), icon: Globe },
                        ].map((s, i) => {
                            const Icon = s.icon;
                            return (
                                <div key={i} className="text-center group cursor-default">
                                    <div className="w-8 h-8 mx-auto mb-1.5 rounded-lg flex items-center justify-center transition-all duration-300"
                                        style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}
                                    >
                                        <Icon className="h-3.5 w-3.5 text-indigo-300" />
                                    </div>
                                    <div className="text-white text-lg font-extrabold">{s.value}</div>
                                    <div className="text-white/30 text-[10px] uppercase tracking-wider font-medium">{s.label}</div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* ═══ RIGHT — Login Form ═══ */}
            <div className="w-full lg:w-[480px] flex flex-col justify-center items-center px-6 sm:px-12 py-12 relative z-10"
                style={{
                    background: isDark
                        ? 'linear-gradient(180deg, rgba(10,10,25,0.98) 0%, rgba(15,15,35,0.98) 100%)'
                        : '#ffffff',
                    boxShadow: isDark
                        ? '-30px 0 80px rgba(0,0,0,0.6)'
                        : '-20px 0 60px rgba(0,0,0,0.08)',
                }}
            >
                {/* Toggles */}
                <div className="absolute top-5 right-5 flex items-center gap-2">
                    <LanguageSwitcher />
                    <button onClick={toggleTheme} className="w-9 h-9 rounded-xl border flex items-center justify-center transition-all duration-300 hover:scale-105"
                        style={{
                            background: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.02)',
                            borderColor: isDark ? 'rgba(255,255,255,0.1)' : '#e2e8f0',
                            color: isDark ? '#94a3b8' : '#64748b',
                        }}
                    >
                        {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                    </button>
                </div>

                <div className="max-w-[380px] w-full">
                    {/* Mobile logo */}
                    <div className="lg:hidden flex justify-center mb-8">
                        <div className="w-16 h-16 rounded-2xl bg-white p-2 shadow-xl shadow-indigo-500/20 flex items-center justify-center">
                            <img src="/FRS_logo.jpg" alt="FRS Logo" className="object-contain w-full h-full rounded-xl" />
                        </div>
                    </div>

                    {/* Header — Bienvenue */}
                    <div className="mb-10">
                        <h2 className="text-[36px] font-extrabold tracking-tight"
                            style={{ color: isDark ? '#94a3b8' : '#64748b', lineHeight: 1.2 }}
                        >
                            {t('Bienvenue')}
                        </h2>
                        <p className="text-[20px] font-extrabold mt-2" style={{ color: isDark ? '#f1f5f9' : '#0f172a' }}>
                            {t('Connexion')}
                        </p>
                    </div>

                    {/* OR separator */}
                    <div className="flex items-center gap-4 mb-8">
                        <div className="flex-1 h-px" style={{ background: isDark ? 'rgba(255,255,255,0.1)' : '#e2e8f0' }} />
                        <span className="text-[13px] font-medium" style={{ color: isDark ? '#64748b' : '#94a3b8' }}>CRM</span>
                        <div className="flex-1 h-px" style={{ background: isDark ? 'rgba(255,255,255,0.1)' : '#e2e8f0' }} />
                    </div>

                    {/* Form */}
                    <form onSubmit={onSubmit} className="space-y-6">
                        {/* Email field */}
                        <div className="space-y-2">
                            <label className="text-[14px] font-bold"
                                style={{ color: isDark ? '#e2e8f0' : '#1e293b' }}
                            >{t('Email')}</label>
                            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                                placeholder=""
                                autoComplete="email"
                                onFocus={() => setEmailFocused(true)}
                                onBlur={() => setEmailFocused(false)}
                                className="w-full outline-none text-[14px]"
                                style={{
                                    height: '50px',
                                    padding: '0 16px',
                                    borderRadius: '10px',
                                    border: `2px solid ${emailFocused ? '#6366f1' : (isDark ? 'rgba(255,255,255,0.15)' : '#d1d5db')}`,
                                    boxShadow: emailFocused ? '0 0 0 3px rgba(99,102,241,0.12)' : 'none',
                                    transition: 'border-color 0.2s, box-shadow 0.2s',
                                    background: isDark ? 'rgba(255,255,255,0.04)' : '#ffffff',
                                    color: isDark ? '#f1f5f9' : '#1e293b',
                                }}
                            />
                        </div>

                        {/* Password field */}
                        <div className="space-y-2">
                            <div className="flex items-center justify-between">
                                <label className="text-[14px] font-bold"
                                    style={{ color: isDark ? '#e2e8f0' : '#1e293b' }}
                                >{t('Mot de passe')}</label>
                                <button type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="flex items-center gap-1.5 text-[13px] font-medium transition-colors"
                                    style={{ color: isDark ? '#94a3b8' : '#64748b' }}
                                >
                                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                    {showPassword ? t('Masquer') : t('Afficher')}
                                </button>
                            </div>
                            <input type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)}
                                placeholder=""
                                autoComplete="current-password"
                                onFocus={() => setPasswordFocused(true)}
                                onBlur={() => setPasswordFocused(false)}
                                className="w-full outline-none text-[14px]"
                                style={{
                                    height: '50px',
                                    padding: '0 16px',
                                    borderRadius: '10px',
                                    border: `2px solid ${passwordFocused ? '#6366f1' : (isDark ? 'rgba(255,255,255,0.15)' : '#d1d5db')}`,
                                    boxShadow: passwordFocused ? '0 0 0 3px rgba(99,102,241,0.12)' : 'none',
                                    transition: 'border-color 0.2s, box-shadow 0.2s',
                                    background: isDark ? 'rgba(255,255,255,0.04)' : '#ffffff',
                                    color: isDark ? '#f1f5f9' : '#1e293b',
                                }}
                            />
                        </div>

                        {/* Remember me + Forgot password */}
                        <div className="flex items-center justify-between">
                            <label className="flex items-center gap-2.5 cursor-pointer select-none">
                                <div className="relative">
                                    <input type="checkbox" checked={rememberMe} onChange={(e) => setRememberMe(e.target.checked)}
                                        className="sr-only" />
                                    <div className="w-5 h-5 rounded border-2 flex items-center justify-center transition-all duration-200"
                                        style={{
                                            borderColor: rememberMe ? '#6366f1' : (isDark ? 'rgba(255,255,255,0.25)' : '#d1d5db'),
                                            background: rememberMe ? '#6366f1' : 'transparent',
                                        }}
                                    >
                                        {rememberMe && (
                                            <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                                                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                                            </svg>
                                        )}
                                    </div>
                                </div>
                                <span className="text-[13px]" style={{ color: isDark ? '#94a3b8' : '#64748b' }}>
                                    {t('Se souvenir 30 jours')}
                                </span>
                            </label>
                            <button type="button" className="text-[13px] font-semibold transition-colors hover:underline"
                                style={{ color: '#6366f1' }}
                            >
                                {t('Mot de passe oublié ?')}
                            </button>
                        </div>

                        {/* Submit button */}
                        <div className="pt-2">
                            <button type="submit" disabled={loading}
                                className="w-full flex items-center justify-center gap-2 text-white font-bold text-[16px] transition-all duration-300"
                                style={{
                                    height: '54px',
                                    borderRadius: '999px',
                                    background: 'linear-gradient(135deg, #6366f1 0%, #7c3aed 50%, #8b5cf6 100%)',
                                    boxShadow: '0 8px 28px rgba(99, 102, 241, 0.35)',
                                    cursor: loading ? 'not-allowed' : 'pointer',
                                    opacity: loading ? 0.7 : 1,
                                }}
                                onMouseEnter={e => {
                                    if (!loading) {
                                        e.currentTarget.style.boxShadow = '0 12px 36px rgba(99, 102, 241, 0.5)';
                                        e.currentTarget.style.transform = 'translateY(-2px)';
                                    }
                                }}
                                onMouseLeave={e => {
                                    e.currentTarget.style.boxShadow = '0 8px 28px rgba(99, 102, 241, 0.35)';
                                    e.currentTarget.style.transform = 'translateY(0)';
                                }}
                            >
                                {loading ? t('Connexion...') : t('Se Connecter')}
                            </button>
                        </div>
                    </form>

                    {/* Footer */}
                    <div className="text-center mt-10">
                        <span className="text-[13px]" style={{ color: isDark ? '#475569' : '#94a3b8' }}>
                            © 2026 CRM Internal — FRS
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
