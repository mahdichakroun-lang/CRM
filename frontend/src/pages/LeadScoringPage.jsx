import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from '../components/ui/select';
import { Label, Spinner, toast } from '../components/ui/shared';
import { Brain, Zap, TrendingUp, Activity, Target, ThermometerSun, Snowflake, Flame, ChevronRight, Cpu, BarChart3, Sparkles } from 'lucide-react';
import api from '../services/api';
import { useTranslation } from 'react-i18next';

const SOURCES  = ['website','phone','referral','trade_show','social_media','email','other'];
const SECTORS  = ['IT / Digital','Finance / Banque','Santé','Industrie','Commerce','Éducation','Immobilier','Tourisme'];

const defaultForm = {
    source: 'website', sector: 'IT / Digital', estimated_value: 25000,
    days_in_pipeline: 30, has_email: 1, has_phone: 1,
    activities_count: 3, calls: 1, emails_sent: 1, meetings: 1,
};

/* ── Score Gauge ── */
const ScoreGauge = ({ score, label }) => {
    const color = score >= 70 ? '#22c55e' : score >= 40 ? '#f59e0b' : '#ef4444';
    const circum = 2 * Math.PI * 54;
    const offset = circum - (score / 100) * circum;
    const Icon = score >= 70 ? Flame : score >= 40 ? ThermometerSun : Snowflake;
    return (
        <div className="flex flex-col items-center gap-3">
            <div className="relative w-36 h-36">
                <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
                    <circle cx="60" cy="60" r="54" fill="none" stroke="currentColor" strokeWidth="8"
                        className="text-muted/20" />
                    <circle cx="60" cy="60" r="54" fill="none" stroke={color} strokeWidth="8"
                        strokeLinecap="round" strokeDasharray={circum} strokeDashoffset={offset}
                        style={{ transition: 'stroke-dashoffset 1s ease-out' }} />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-3xl font-bold" style={{ color }}>{score}%</span>
                    <Icon className="w-4 h-4 mt-0.5" style={{ color }} />
                </div>
            </div>
            <Badge variant={score >= 70 ? 'success' : score >= 40 ? 'warning' : 'destructive'}
                className="text-sm px-3 py-1">{label}</Badge>
        </div>
    );
};

/* ── Factor Card ── */
const FactorCard = ({ factor }) => (
    <div className={`flex items-start gap-3 p-3 rounded-lg border ${
        factor.impact === 'positive'
            ? 'border-emerald-500/20 bg-emerald-500/5'
            : 'border-red-500/20 bg-red-500/5'
    }`}>
        <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${
            factor.impact === 'positive' ? 'bg-emerald-500' : 'bg-red-500'
        }`} />
        <div>
            <p className="text-sm font-semibold">{factor.factor}</p>
            <p className="text-xs text-muted-foreground">{factor.detail}</p>
        </div>
    </div>
);

/* ── KPI Mini ── */
const MiniKpi = ({ icon: Icon, label, value, gradient }) => (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-card border border-border/60">
        <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${gradient} flex items-center justify-center shadow-sm`}>
            <Icon className="w-4 h-4 text-white" />
        </div>
        <div>
            <p className="text-[11px] text-muted-foreground uppercase tracking-wide">{label}</p>
            <p className="text-sm font-bold">{value}</p>
        </div>
    </div>
);

/* ═══════════ Main Page ═══════════ */
const LeadScoringPage = () => {
    const [form, setForm] = useState({ ...defaultForm });
    const [result, setResult] = useState(null);
    const [modelInfo, setModelInfo] = useState(null);
    const [loading, setLoading] = useState(false);
    const [infoLoading, setInfoLoading] = useState(true);
    const { t } = useTranslation();

    // Load model info on mount
    useEffect(() => {
        (async () => {
            try {
                const r = await api.get('/ml/info');
                setModelInfo(r.data);
            } catch { setModelInfo(null); }
            finally { setInfoLoading(false); }
        })();
    }, []);

    const handlePredict = async () => {
        setLoading(true);
        try {
            const payload = {
                ...form,
                estimated_value: Number(form.estimated_value),
                days_in_pipeline: Number(form.days_in_pipeline),
                activities_count: Number(form.activities_count),
                calls: Number(form.calls),
                emails_sent: Number(form.emails_sent),
                meetings: Number(form.meetings),
                has_email: Number(form.has_email),
                has_phone: Number(form.has_phone),
            };
            const r = await api.post('/ml/score', payload);
            setResult(r.data);
        } catch (e) {
            toast.error(e.response?.data?.detail || 'Erreur de prédiction');
        } finally { setLoading(false); }
    };

    const updateField = (key, val) => setForm(p => ({ ...p, [key]: val }));

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg">
                        <Brain className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold">{t('Lead Scoring IA')}</h1>
                        <p className="text-sm text-muted-foreground">{t('Prédiction de conversion par Machine Learning')}</p>
                    </div>
                </div>
                {modelInfo && (
                    <Badge variant={modelInfo.status === 'online' ? 'success' : 'secondary'}
                        className="gap-1.5">
                        <span className={`w-1.5 h-1.5 rounded-full ${modelInfo.status === 'online' ? 'bg-emerald-500 animate-pulse' : 'bg-muted-foreground'}`} />
                        {modelInfo.status === 'online' ? 'Modèle Actif' : 'Hors ligne'}
                    </Badge>
                )}
            </div>

            {/* Model Info KPIs */}
            {modelInfo && modelInfo.status === 'online' && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <MiniKpi icon={Cpu} label="Modèle" value={modelInfo.model_name} gradient="from-violet-500 to-purple-600" />
                    <MiniKpi icon={BarChart3} label="F1-Score" value={`${(modelInfo.metrics.F1 * 100).toFixed(1)}%`} gradient="from-emerald-500 to-green-600" />
                    <MiniKpi icon={Activity} label="AUC-ROC" value={`${(modelInfo.metrics.AUC * 100).toFixed(1)}%`} gradient="from-blue-500 to-cyan-600" />
                    <MiniKpi icon={Sparkles} label="Features" value={modelInfo.features_count} gradient="from-amber-500 to-orange-600" />
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
                {/* ── LEFT: Formulaire ── */}
                <Card className="lg:col-span-3 border-border/60">
                    <CardHeader className="pb-4">
                        <CardTitle className="text-base flex items-center gap-2">
                            <Target className="w-4 h-4 text-primary" />
                            {t('Caractéristiques du Lead')}
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-5">
                        {/* Row 1: Source + Sector */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-1.5">
                                <Label>{t('Source')}</Label>
                                <Select value={form.source} onValueChange={v => updateField('source', v)}>
                                    <SelectTrigger><SelectValue /></SelectTrigger>
                                    <SelectContent>
                                        {SOURCES.map(s => <SelectItem key={s} value={s}>{s.replace('_',' ')}</SelectItem>)}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-1.5">
                                <Label>{t('Secteur')}</Label>
                                <Select value={form.sector} onValueChange={v => updateField('sector', v)}>
                                    <SelectTrigger><SelectValue /></SelectTrigger>
                                    <SelectContent>
                                        {SECTORS.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        {/* Row 2: Value + Days */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-1.5">
                                <Label>{t('Valeur estimée (DT)')}</Label>
                                <Input type="number" value={form.estimated_value}
                                    onChange={e => updateField('estimated_value', e.target.value)} />
                            </div>
                            <div className="space-y-1.5">
                                <Label>{t('Jours dans le pipeline')}</Label>
                                <Input type="number" value={form.days_in_pipeline}
                                    onChange={e => updateField('days_in_pipeline', e.target.value)} />
                            </div>
                        </div>

                        {/* Row 3: Contact */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-1.5">
                                <Label>{t('Email disponible')}</Label>
                                <Select value={String(form.has_email)} onValueChange={v => updateField('has_email', Number(v))}>
                                    <SelectTrigger><SelectValue /></SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="1">Oui</SelectItem>
                                        <SelectItem value="0">Non</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-1.5">
                                <Label>{t('Téléphone disponible')}</Label>
                                <Select value={String(form.has_phone)} onValueChange={v => updateField('has_phone', Number(v))}>
                                    <SelectTrigger><SelectValue /></SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="1">Oui</SelectItem>
                                        <SelectItem value="0">Non</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        {/* Row 4: Activities */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="space-y-1.5">
                                <Label>{t('Activités')}</Label>
                                <Input type="number" value={form.activities_count}
                                    onChange={e => updateField('activities_count', e.target.value)} />
                            </div>
                            <div className="space-y-1.5">
                                <Label>{t('Appels')}</Label>
                                <Input type="number" value={form.calls}
                                    onChange={e => updateField('calls', e.target.value)} />
                            </div>
                            <div className="space-y-1.5">
                                <Label>{t('Emails')}</Label>
                                <Input type="number" value={form.emails_sent}
                                    onChange={e => updateField('emails_sent', e.target.value)} />
                            </div>
                            <div className="space-y-1.5">
                                <Label>{t('Réunions')}</Label>
                                <Input type="number" value={form.meetings}
                                    onChange={e => updateField('meetings', e.target.value)} />
                            </div>
                        </div>

                        {/* Predict Button */}
                        <Button onClick={handlePredict} disabled={loading}
                            className="w-full h-11 text-sm font-semibold gap-2 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 shadow-lg shadow-violet-500/20">
                            {loading ? <Spinner className="w-4 h-4" /> : <Zap className="w-4 h-4" />}
                            {loading ? t('Analyse en cours...') : t('Prédire le Score')}
                        </Button>
                    </CardContent>
                </Card>

                {/* ── RIGHT: Résultat ── */}
                <Card className="lg:col-span-2 border-border/60">
                    <CardHeader className="pb-4">
                        <CardTitle className="text-base flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-primary" />
                            {t('Résultat de la Prédiction')}
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {!result ? (
                            <div className="flex flex-col items-center justify-center py-12 text-center">
                                <div className="w-16 h-16 rounded-2xl bg-muted/50 flex items-center justify-center mb-4">
                                    <Brain className="w-8 h-8 text-muted-foreground/40" />
                                </div>
                                <p className="text-sm text-muted-foreground">
                                    {t('Remplissez le formulaire et cliquez sur')} <br />
                                    <strong>{t('"Prédire le Score"')}</strong>
                                </p>
                            </div>
                        ) : (
                            <div className="space-y-6">
                                {/* Gauge */}
                                <div className="flex justify-center pt-2">
                                    <ScoreGauge score={result.score} label={result.label} />
                                </div>

                                {/* Probability */}
                                <div className="text-center">
                                    <p className="text-xs text-muted-foreground">{t('Probabilité de conversion')}</p>
                                    <p className="text-lg font-bold">{(result.probability * 100).toFixed(2)}%</p>
                                </div>

                                {/* Factors */}
                                {result.top_factors?.length > 0 && (
                                    <div className="space-y-2">
                                        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                                            {t('Facteurs clés')}
                                        </p>
                                        {result.top_factors.map((f, i) => (
                                            <FactorCard key={i} factor={f} />
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default LeadScoringPage;
