import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from '../components/ui/select';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/table';
import { Spinner, EmptyState, toast } from '../components/ui/shared';
import { ScrollText, Search } from 'lucide-react';
import api from '../services/api';
import dayjs from 'dayjs';
import { useTranslation } from 'react-i18next';

const ACTION_BADGE = { create: 'success', update: 'info', delete: 'danger', stage_change: 'warning', convert: 'purple', add_message: 'info' };
const ENTITIES = ['lead', 'deal', 'account', 'contact', 'ticket', 'activity', 'quote', 'user'];

const AuditPage = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [filterEntity, setFilterEntity] = useState('');
    const { t } = useTranslation();

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const params = { size: 100 };
            if (search) params.search = search;
            if (filterEntity) params.entity = filterEntity;
            const r = await api.get('/reports/audit-logs', { params });
            setData(r.data.items || r.data || []);
        } catch(e) { toast.error(e.response?.data?.detail || t('Erreur chargement')); setData([]); }
        finally { setLoading(false); }
    }, [search, filterEntity, t]);

    useEffect(() => { fetchData(); }, [fetchData]);

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-slate-500 to-gray-600 flex items-center justify-center text-white shadow-lg"><ScrollText className="h-5 w-5" /></div>
                    <div><h1 className="text-xl font-bold tracking-tight">{t("Journal d'Audit")}</h1><p className="text-sm text-muted-foreground">{data.length} {t('entrées')}</p></div>
                </div>
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input placeholder={t('Rechercher...')} value={search} onChange={e => setSearch(e.target.value)} className="pl-9 w-[200px]" />
                    </div>
                    <Select value={filterEntity} onValueChange={(v) => setFilterEntity(v === 'all' ? '' : v)}>
                        <SelectTrigger className="w-[140px]"><SelectValue placeholder={t('Entité')} /></SelectTrigger>
                        <SelectContent><SelectItem value="all">{t('Toutes')}</SelectItem>{ENTITIES.map(e => <SelectItem key={e} value={e}>{e.toUpperCase()}</SelectItem>)}</SelectContent>
                    </Select>
                </div>
            </div>
            <Card><CardContent className="p-0">
                {loading ? <div className="flex justify-center py-20"><Spinner /></div> : data.length === 0 ? <EmptyState title={t('Aucune entrée')} /> : (
                    <Table><TableHeader><TableRow><TableHead className="w-[160px]">{t('Date')}</TableHead><TableHead>{t('Utilisateur')}</TableHead><TableHead>{t('Action')}</TableHead><TableHead>{t('Entité')}</TableHead><TableHead className="w-[60px]">ID</TableHead><TableHead>{t('Description')}</TableHead></TableRow></TableHeader>
                        <TableBody>{data.map(row => (
                            <TableRow key={row.id}>
                                <TableCell className="text-muted-foreground">{row.created_at ? dayjs(row.created_at).format('DD/MM/YYYY HH:mm') : '—'}</TableCell>
                                <TableCell>User #{row.actor_user_id}</TableCell>
                                <TableCell><Badge variant={ACTION_BADGE[row.action] || 'secondary'}>{row.action?.toUpperCase()}</Badge></TableCell>
                                <TableCell><Badge variant="outline">{row.entity}</Badge></TableCell>
                                <TableCell>{row.entity_id}</TableCell>
                                <TableCell className="max-w-[300px] truncate text-muted-foreground">{row.description || '—'}</TableCell>
                            </TableRow>
                        ))}</TableBody></Table>
                )}
            </CardContent></Card>
        </div>
    );
};
export default AuditPage;
