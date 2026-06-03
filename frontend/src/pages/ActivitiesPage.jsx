import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from '../components/ui/select';
import { Label, Spinner, EmptyState, toast } from '../components/ui/shared';
import { Textarea } from '../components/ui/input';
import { Plus, Pencil, Trash2, CalendarDays, Phone, Mail, Users, FileText, Search } from 'lucide-react';
import api from '../services/api';
import dayjs from 'dayjs';
import { useTranslation } from 'react-i18next';
import ConfirmDialog from '../components/ConfirmDialog';

const TYPE_BADGE = { call: 'success', email: 'info', meeting: 'purple', note: 'secondary' };
const TYPE_ICON = { call: Phone, email: Mail, meeting: Users, note: FileText };
const TYPES = ['call', 'email', 'meeting', 'note'];

const ActivitiesPage = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modal, setModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [accounts, setAccounts] = useState([]);
    const [deals, setDeals] = useState([]);
    const [filterType, setFilterType] = useState('');
    const [search, setSearch] = useState('');
    const [form, setForm] = useState({ type: 'call' });
    const { t } = useTranslation();
    const [deleteTarget, setDeleteTarget] = useState(null);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const params = { size: 100, search };
            if (filterType) params.type = filterType;
            const [r, a, d] = await Promise.all([api.get('/activities', { params }), api.get('/accounts', { params: { size: 100 } }), api.get('/deals', { params: { size: 100 } })]);
            setData(r.data.items || []); setAccounts(a.data.items || []); setDeals(d.data.items || []);
        } catch(e) { toast.error(e.response?.data?.detail || t('Erreur')); } finally { setLoading(false); }
    }, [filterType, search]);
    useEffect(() => { fetchData(); }, [fetchData]);

    const handleSave = async () => {
        if (!form.type || !form.subject) { toast.error(t('Champs requis')); return; }
        const payload = { ...form };
        if (payload.due_date) payload.due_date = new Date(payload.due_date).toISOString();
        try {
            if (editing) { await api.patch(`/activities/${editing.id}`, payload); toast.success(t('Activité MAJ')); }
            else { await api.post('/activities', payload); toast.success(t('Activité créée')); }
            setModal(false); setEditing(null); setForm({ type: 'call' }); fetchData();
        } catch(e) { toast.error(e.response?.data?.detail || t('Erreur')); }
    };
    const handleDelete = async (id) => { try { await api.delete(`/activities/${id}`); toast.success(t('Supprimé')); fetchData(); } catch(e) { toast.error(e.response?.data?.detail || t('Erreur')); } };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center text-white shadow-lg"><CalendarDays className="h-5 w-5" /></div>
                    <div><h1 className="text-xl font-bold tracking-tight">{t('Activités')}</h1><p className="text-sm text-muted-foreground">{data.length} {t('activités enregistrées')}</p></div>
                </div>
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input placeholder={t('Rechercher...')} value={search} onChange={e => setSearch(e.target.value)} className="pl-9 w-[200px]" />
                    </div>
                    <Select value={filterType} onValueChange={(v) => setFilterType(v === 'all' ? '' : v)}>
                        <SelectTrigger className="w-[130px]"><SelectValue placeholder="Type" /></SelectTrigger>
                        <SelectContent><SelectItem value="all">{t('Tous')}</SelectItem>{TYPES.map(s => <SelectItem key={s} value={s}>{s.toUpperCase()}</SelectItem>)}</SelectContent>
                    </Select>
                    <Button onClick={() => { setEditing(null); setForm({ type: 'call' }); setModal(true); }}><Plus className="h-4 w-4 mr-2" /> {t('Nouvelle Activité')}</Button>
                </div>
            </div>
            <Card><CardContent className="p-0">
                {loading ? <div className="flex justify-center py-20"><Spinner /></div> : data.length === 0 ? <EmptyState title={t('Aucune activité')} /> : (
                    <Table><TableHeader><TableRow><TableHead>{t('Type')}</TableHead><TableHead>{t('Sujet')}</TableHead><TableHead>{t('Note')}</TableHead><TableHead>{t('Compte')}</TableHead><TableHead>{t('Deal')}</TableHead><TableHead>{t('Relance')}</TableHead><TableHead className="w-[100px]">{t('Actions')}</TableHead></TableRow></TableHeader>
                        <TableBody>{data.map(row => {
                            const acc = accounts.find(x => x.id === row.account_id); const deal = deals.find(x => x.id === row.deal_id); const Icon = TYPE_ICON[row.type] || FileText; return (
                                <TableRow key={row.id}>
                                    <TableCell><Badge variant={TYPE_BADGE[row.type] || 'secondary'} className="gap-1"><Icon className="h-3 w-3" />{row.type?.toUpperCase()}</Badge></TableCell>
                                    <TableCell className="font-semibold">{row.subject}</TableCell>
                                    <TableCell className="max-w-[200px] truncate text-muted-foreground">{row.note || '—'}</TableCell>
                                    <TableCell>{acc ? <Badge variant="info">{acc.name}</Badge> : '—'}</TableCell>
                                    <TableCell>{deal ? <Badge variant="purple">{deal.name}</Badge> : '—'}</TableCell>
                                    <TableCell>{row.due_date ? dayjs(row.due_date).format('DD/MM/YYYY HH:mm') : '—'}</TableCell>
                                    <TableCell><div className="flex gap-1"><Button variant="ghost" size="icon" onClick={() => { setEditing(row); setForm({ ...row, due_date: row.due_date ? dayjs(row.due_date).format('YYYY-MM-DDTHH:mm') : '' }); setModal(true); }}><Pencil className="h-4 w-4" /></Button><Button variant="ghost" size="icon" onClick={() => setDeleteTarget(row.id)} className="text-destructive hover:text-destructive"><Trash2 className="h-4 w-4" /></Button></div></TableCell>
                                </TableRow>
                            );
                        })}</TableBody></Table>
                )}
            </CardContent></Card>
            <Dialog open={modal} onOpenChange={(o) => { if (!o) setModal(false); }}>
                <DialogContent className="sm:max-w-[550px]"><DialogHeader><DialogTitle>{editing ? t('Modifier') : t('Nouvelle Activité')}</DialogTitle></DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="grid grid-cols-3 gap-4">
                            <div className="space-y-2"><Label>{t('Type')} *</Label><Select value={form.type || 'call'} onValueChange={(v) => setForm({ ...form, type: v })}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{TYPES.map(s => <SelectItem key={s} value={s}>{s.toUpperCase()}</SelectItem>)}</SelectContent></Select></div>
                            <div className="space-y-2 col-span-2"><Label>{t('Sujet')} *</Label><Input value={form.subject || ''} onChange={(e) => setForm({ ...form, subject: e.target.value })} /></div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2"><Label>{t('Compte')}</Label><Select value={form.account_id?.toString() || 'none'} onValueChange={(v) => setForm({ ...form, account_id: v === 'none' ? null : parseInt(v) })}><SelectTrigger><SelectValue placeholder={t('Choisir...')} /></SelectTrigger><SelectContent><SelectItem value="none">{t('Aucun')}</SelectItem>{accounts.map(a => <SelectItem key={a.id} value={a.id.toString()}>{a.name}</SelectItem>)}</SelectContent></Select></div>
                            <div className="space-y-2"><Label>{t('Deal')}</Label><Select value={form.deal_id?.toString() || 'none'} onValueChange={(v) => setForm({ ...form, deal_id: v === 'none' ? null : parseInt(v) })}><SelectTrigger><SelectValue placeholder={t('Choisir...')} /></SelectTrigger><SelectContent><SelectItem value="none">{t('Aucun')}</SelectItem>{deals.map(d => <SelectItem key={d.id} value={d.id.toString()}>{d.name}</SelectItem>)}</SelectContent></Select></div>
                        </div>
                        <div className="space-y-2"><Label>{t('Date de relance')}</Label><Input type="datetime-local" value={form.due_date || ''} onChange={(e) => setForm({ ...form, due_date: e.target.value })} /></div>
                        <div className="space-y-2"><Label>{t('Notes')}</Label><Textarea rows={3} value={form.note || ''} onChange={(e) => setForm({ ...form, note: e.target.value })} /></div>
                    </div>
                    <DialogFooter><Button variant="outline" onClick={() => setModal(false)}>{t('Annuler')}</Button><Button onClick={handleSave}>{t('Enregistrer')}</Button></DialogFooter>
                </DialogContent>
            </Dialog>
            <ConfirmDialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => handleDelete(deleteTarget)} />
        </div>
    );
};
export default ActivitiesPage;
