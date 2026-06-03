import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Spinner } from '../../components/ui/shared';
import { Headphones, CheckCircle, FileText, DollarSign } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import { useTranslation } from 'react-i18next';

const ClientDashboard = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const { user } = useAuth();
    const { t } = useTranslation();

    useEffect(() => {
        const fetch = async () => {
            try { const r = await api.get('/client/dashboard'); setData(r.data); }
            catch (e) { console.error(e); } finally { setLoading(false); }
        };
        fetch();
    }, []);

    if (loading) return <div className="flex justify-center pt-40"><Spinner size="lg" /></div>;

    const kpis = [
        { title: t('Tickets ouverts'), value: data?.open_tickets || 0, icon: Headphones, color: 'from-amber-500 to-orange-500' },
        { title: t('Tickets résolus'), value: data?.resolved_tickets || 0, icon: CheckCircle, color: 'from-emerald-500 to-teal-500' },
        { title: t('Devis reçus'), value: data?.total_quotes || 0, icon: FileText, color: 'from-indigo-500 to-purple-500' },
        { title: t('Total devis'), value: data?.total_quotes_value || 0, suffix: ' DT', icon: DollarSign, color: 'from-pink-500 to-rose-500' },
    ];

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold tracking-tight">{t('Bienvenue')}, {user?.name} 👋</h1>
                <p className="text-muted-foreground text-sm mt-1">{t('Portail client')} — {data?.account_name || t('Votre entreprise')}</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {kpis.map((kpi, i) => {
                    const Icon = kpi.icon;
                    return (
                        <Card key={i} className="stat-card">
                            <CardContent className="p-5">
                                <div className="flex items-start justify-between">
                                    <div>
                                        <p className="text-sm text-muted-foreground font-medium">{kpi.title}</p>
                                        <p className="text-3xl font-extrabold tracking-tight mt-2">{kpi.value.toLocaleString()}{kpi.suffix || ''}</p>
                                    </div>
                                    <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${kpi.color} flex items-center justify-center shadow-lg`}>
                                        <Icon className="h-5 w-5 text-white" />
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <Card>
                    <CardHeader><CardTitle>📌 {t('Besoin d\'aide ?')}</CardTitle></CardHeader>
                    <CardContent className="space-y-3 text-sm">
                        <p>{t('Utilisez la section **Mes Tickets** pour ouvrir un nouveau ticket de support.')}</p>
                        <p>{t('Notre équipe vous répondra dans les plus brefs délais.')}</p>
                        <p className="text-muted-foreground">{t('Horaires de support : Dimanche — Jeudi, 8h — 17h')}</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader><CardTitle>📄 {t('Vos devis')}</CardTitle></CardHeader>
                    <CardContent className="space-y-3 text-sm">
                        <p>{t('Consultez vos devis dans la section **Mes Devis**.')}</p>
                        <p>{data?.accepted_quotes || 0} {t('devis accepté(s) sur')} {data?.total_quotes || 0} {t('au total.')}</p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};
export default ClientDashboard;
