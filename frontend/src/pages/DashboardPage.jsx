import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Spinner } from '../components/ui/shared';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, AreaChart, Area } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Target, Headphones, Clock, ArrowUpRight, Activity } from 'lucide-react';
import api from '../services/api';
import { useTheme } from '../context/ThemeContext';
import { useTranslation } from 'react-i18next';

const COLORS = ['#6366f1', '#ec4899', '#f59e0b', '#10b981', '#0ea5e9', '#f43f5e', '#8b5cf6'];

/* ── KPI Card Component ── */
const KpiCard = ({ title, value, suffix, icon: Icon, gradient, trend, up, t }) => (
    <Card className="stat-card group cursor-default border-border/60 dark:border-white/[0.06] h-full flex flex-col">
        <CardContent className="p-5 flex flex-col h-full justify-between gap-4">
            <div className="flex items-start justify-between">
                <div className="space-y-1.5">
                    <p className="text-[12px] text-muted-foreground font-medium uppercase tracking-wide">{title}</p>
                    <div className="flex items-baseline gap-1.5">
                        <p className="text-[26px] font-bold tracking-tight leading-none tabular-nums">
                            {suffix === '%' ? value.toFixed(1) : Math.round(value).toLocaleString()}
                        </p>
                        {suffix && <span className="text-[13px] font-medium text-muted-foreground/70">{suffix}</span>}
                    </div>
                </div>
                <div className={`w-10 h-10 shrink-0 rounded-lg bg-gradient-to-br ${gradient} flex items-center justify-center shadow-md group-hover:shadow-lg group-hover:scale-105 transition-all duration-300`}>
                    <Icon className="h-[18px] w-[18px] text-white" />
                </div>
            </div>
            <div className="flex items-center">
                {trend != null ? (
                    <div className={cn(
                        'inline-flex items-center gap-1 text-[11px] font-semibold rounded-md px-2 py-0.5',
                        up ? 'bg-emerald-500/8 text-emerald-600 dark:text-emerald-400' : 'bg-red-500/8 text-red-600 dark:text-red-400'
                    )}>
                        {up ? <ArrowUpRight className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                        {trend}% {t('vs mois dernier')}
                    </div>
                ) : (
                    <div className="inline-flex items-center gap-1 text-[11px] font-medium rounded-md px-2 py-0.5 bg-muted text-muted-foreground/60">
                        — {t('pas de données')}
                    </div>
                )}
            </div>
        </CardContent>
    </Card>
);

/* ── Chart Wrapper ── */
const ChartCard = ({ title, badge, children, className }) => (
    <Card className={cn('chart-card border-border/60 dark:border-white/[0.06]', className)}>
        <CardHeader className="pb-1 pt-5 px-5">
            <div className="flex items-center justify-between">
                <CardTitle className="text-[14px] font-semibold tracking-tight">{title}</CardTitle>
                {badge && <Badge variant="outline" className="text-[10px] font-medium h-5 px-2">{badge}</Badge>}
            </div>
        </CardHeader>
        <CardContent className="px-5 pb-5 pt-2">
            {children}
        </CardContent>
    </Card>
);

const DashboardPage = () => {
    const [sales, setSales] = useState(null);
    const [support, setSupport] = useState(null);
    const [timeline, setTimeline] = useState([]);
    const [loading, setLoading] = useState(true);
    const { isDark } = useTheme();
    const { t } = useTranslation();

    useEffect(() => {
        const fetch = async () => {
            try {
                const [s, sup, tl] = await Promise.all([
                    api.get('/reports/sales'),
                    api.get('/reports/support'),
                    api.get('/reports/activity-timeline').catch(() => ({ data: { timeline: [] } })),
                ]);
                setSales(s.data); setSupport(sup.data); setTimeline(tl.data.timeline || []);
            } catch (e) { console.error(e); } finally { setLoading(false); }
        };
        fetch();
    }, []);

    if (loading) return <div className="flex justify-center pt-40"><Spinner size="lg" /></div>;

    const pipelineData = sales?.pipeline_summary || [];
    const leadSources = sales?.leads_by_source ? Object.entries(sales.leads_by_source).map(([name, value]) => ({ name, value })) : [];
    const ticketsByStatus = support?.tickets_by_status ? Object.entries(support.tickets_by_status).map(([name, value]) => ({ name, value })) : [];
    const ticketsByPriority = support?.tickets_by_priority ? Object.entries(support.tickets_by_priority).map(([name, value]) => ({ name, value })) : [];

    const textColor = isDark ? '#71717a' : '#a1a1aa';
    const gridColor = isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)';
    const tooltipBg = isDark ? '#18181b' : '#ffffff';
    const tooltipBorder = isDark ? '#27272a' : '#e4e4e7';

    const tooltipStyle = {
        backgroundColor: tooltipBg,
        border: `1px solid ${tooltipBorder}`,
        borderRadius: 8,
        color: isDark ? '#f4f4f5' : '#18181b',
        boxShadow: '0 8px 30px rgba(0,0,0,0.12)',
        fontSize: 12,
        padding: '8px 12px',
    };

    const activePipeline = (sales?.pipeline_summary || [])
        .reduce((sum, p) => sum + (parseFloat(p.total_value) || 0), 0);

    const kpis = [
        {
            title: t('Pipeline Total'),
            value: activePipeline,
            suffix: 'DT',
            icon: DollarSign,
            gradient: 'from-indigo-500 to-violet-600',
            trend: sales?.pipeline_trend != null ? Math.abs(sales.pipeline_trend) : null,
            up: (sales?.pipeline_trend || 0) >= 0,
        },
        {
            title: t('Taux conversion'),
            value: sales?.conversion_rate || 0,
            suffix: '%',
            icon: Target,
            gradient: 'from-pink-500 to-rose-600',
            trend: sales?.conversion_trend != null ? Math.abs(sales.conversion_trend) : null,
            up: (sales?.conversion_trend || 0) >= 0,
        },
        {
            title: t('Tickets ouverts'),
            value: support?.open_tickets || 0,
            suffix: '',
            icon: Headphones,
            gradient: 'from-amber-500 to-orange-600',
            trend: support?.open_tickets_trend != null ? Math.abs(support.open_tickets_trend) : null,
            up: (support?.open_tickets_trend || 0) <= 0,
        },
        {
            title: t('Délai résolution'),
            value: Math.max(0, support?.avg_resolution_hours || 0),
            suffix: 'h',
            icon: Clock,
            gradient: 'from-emerald-500 to-teal-600',
            trend: support?.resolution_trend != null ? Math.abs(support.resolution_trend) : null,
            up: (support?.resolution_trend || 0) <= 0,
        },
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
                <div>
                    <h1 className="text-xl font-bold tracking-tight">{t('Tableau de bord')}</h1>
                    <p className="text-muted-foreground text-[13px] mt-1">{t('Bienvenue — Voici un aperçu de votre activité commerciale et support.')}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                    <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground bg-muted/60 rounded-lg px-2.5 py-1.5 border border-border/60 font-medium">
                        <span className="pulse-dot w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />
                        <span>{t('En temps réel')}</span>
                    </div>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
                {kpis.map((kpi, i) => (
                    <KpiCard key={i} {...kpi} t={t} />
                ))}
            </div>

            {/* Charts Row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-7 gap-4">
                <ChartCard
                    title={t('Pipeline par étape')}
                    badge={`${pipelineData.length} ${t('étapes')}`}
                    className="lg:col-span-4"
                >
                    <div className="h-[280px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={pipelineData} barSize={28}>
                                <CartesianGrid strokeDasharray="3 3" stroke={gridColor} vertical={false} />
                                <XAxis dataKey="stage" stroke={textColor} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                                <YAxis stroke={textColor} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: isDark ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.02)' }} />
                                <defs>
                                    <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#6366f1" />
                                        <stop offset="100%" stopColor="#8b5cf6" />
                                    </linearGradient>
                                </defs>
                                <Bar dataKey="total_value" fill="url(#barGrad)" radius={[6, 6, 2, 2]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </ChartCard>
                <ChartCard title={t('Sources des leads')} className="lg:col-span-3">
                    <div className="h-[280px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie data={leadSources} cx="50%" cy="48%" innerRadius={60} outerRadius={95} paddingAngle={3} dataKey="value" nameKey="name" strokeWidth={0}>
                                    {leadSources.map((_, i) => (<Cell key={i} fill={COLORS[i % COLORS.length]} />))}
                                </Pie>
                                <Tooltip contentStyle={tooltipStyle} />
                                <Legend iconType="circle" iconSize={7} wrapperStyle={{ color: textColor, fontSize: 11, paddingTop: 8 }} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </ChartCard>
            </div>

            {/* Activity Timeline Curves */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <ChartCard title={t('Activité Commerciale')} badge={t('6 mois')}>
                    <div className="h-[280px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={timeline}>
                                <defs>
                                    <linearGradient id="gradLeads" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3} />
                                        <stop offset="100%" stopColor="#6366f1" stopOpacity={0.02} />
                                    </linearGradient>
                                    <linearGradient id="gradDeals" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
                                        <stop offset="100%" stopColor="#10b981" stopOpacity={0.02} />
                                    </linearGradient>
                                    <linearGradient id="gradTickets" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.3} />
                                        <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.02} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke={gridColor} vertical={false} />
                                <XAxis dataKey="month" stroke={textColor} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                                <YAxis stroke={textColor} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
                                <Tooltip contentStyle={tooltipStyle} />
                                <Legend iconType="circle" iconSize={7} wrapperStyle={{ color: textColor, fontSize: 11, paddingTop: 8 }} />
                                <Area type="monotone" dataKey="leads" name="Leads" stroke="#6366f1" strokeWidth={2.5} fill="url(#gradLeads)" dot={{ r: 3, fill: '#6366f1' }} activeDot={{ r: 5 }} />
                                <Area type="monotone" dataKey="deals" name="Deals" stroke="#10b981" strokeWidth={2.5} fill="url(#gradDeals)" dot={{ r: 3, fill: '#10b981' }} activeDot={{ r: 5 }} />
                                <Area type="monotone" dataKey="tickets" name="Tickets" stroke="#f59e0b" strokeWidth={2.5} fill="url(#gradTickets)" dot={{ r: 3, fill: '#f59e0b' }} activeDot={{ r: 5 }} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </ChartCard>
                <ChartCard title={t('Revenus Gagnés')} badge="DT">
                    <div className="h-[280px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={timeline}>
                                <defs>
                                    <linearGradient id="gradRevenue" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#ec4899" stopOpacity={0.35} />
                                        <stop offset="100%" stopColor="#ec4899" stopOpacity={0.02} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke={gridColor} vertical={false} />
                                <XAxis dataKey="month" stroke={textColor} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                                <YAxis stroke={textColor} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v} />
                                <Tooltip contentStyle={tooltipStyle} formatter={(value) => [`${parseFloat(value).toLocaleString(undefined, { minimumFractionDigits: 2 })} DT`, t('Revenus')]} />
                                <Area type="monotone" dataKey="won_value" name={t('Revenus')} stroke="#ec4899" strokeWidth={2.5} fill="url(#gradRevenue)" dot={{ r: 4, fill: '#ec4899', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 6 }} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </ChartCard>
            </div>

            {/* Charts Row 2 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <ChartCard title={t('Tickets par statut')}>
                    <div className="h-[250px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={ticketsByStatus} layout="vertical" barSize={18}>
                                <CartesianGrid strokeDasharray="3 3" stroke={gridColor} horizontal={false} />
                                <XAxis type="number" stroke={textColor} axisLine={false} tickLine={false} tick={{ fontSize: 11 }} />
                                <YAxis type="category" dataKey="name" stroke={textColor} width={110} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: isDark ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.02)' }} />
                                <defs>
                                    <linearGradient id="ticketGrad" x1="0" y1="0" x2="1" y2="0">
                                        <stop offset="0%" stopColor="#f59e0b" />
                                        <stop offset="100%" stopColor="#f97316" />
                                    </linearGradient>
                                </defs>
                                <Bar dataKey="value" fill="url(#ticketGrad)" radius={[0, 6, 6, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </ChartCard>
                <ChartCard title={t('Tickets par priorité')}>
                    <div className="h-[250px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie data={ticketsByPriority} cx="50%" cy="48%" innerRadius={45} outerRadius={80} paddingAngle={3} dataKey="value" nameKey="name" strokeWidth={0}>
                                    {ticketsByPriority.map((_, i) => (<Cell key={i} fill={['#10b981', '#f59e0b', '#f97316', '#ef4444'][i] || COLORS[i]} />))}
                                </Pie>
                                <Tooltip contentStyle={tooltipStyle} />
                                <Legend iconType="circle" iconSize={7} wrapperStyle={{ color: textColor, fontSize: 11, paddingTop: 8 }} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </ChartCard>
            </div>
        </div>
    );
};

function cn(...args) {
    return args.filter(Boolean).join(' ');
}

export default DashboardPage;
