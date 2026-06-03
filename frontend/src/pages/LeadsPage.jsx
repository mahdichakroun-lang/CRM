import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '../components/ui/dialog';
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from '../components/ui/select';
import { Label, Spinner, EmptyState, toast } from '../components/ui/shared';
import { Plus, Pencil, Trash2, Search, Target, ArrowRightLeft } from 'lucide-react';
import api from '../services/api';
import { useTranslation } from 'react-i18next';
import ConfirmDialog from '../components/ConfirmDialog';

const STATUS_BADGE = { new: 'info', contacted: 'info', qualified: 'success', unqualified: 'secondary', converted: 'purple' };
const SOURCE_BADGE = { website: 'info', phone: 'success', referral: 'warning', trade_show: 'warning', social_media: 'purple', email: 'info', other: 'secondary' };
const STATUSES = ['new', 'contacted', 'qualified', 'unqualified', 'converted'];
const SOURCES = ['website', 'phone', 'referral', 'trade_show', 'social_media', 'email', 'other'];

const LeadsPage = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modal, setModal] = useState(false);
    const [convertModal, setConvertModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [convertingId, setConvertingId] = useState(null);
    const [search, setSearch] = useState('');
    const [filterStatus, setFilterStatus] = useState('');
    const [form, setForm] = useState({ source: 'website', status: 'new' });
    const [convertForm, setConvertForm] = useState({});
    const { t } = useTranslation();
    const [deleteTarget, setDeleteTarget] = useState(null);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const params = { size: 100, search };
            if (filterStatus) params.status = filterStatus;
            const r = await api.get('/leads', { params });
            setData(r.data.items || []);
        } catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); } finally { setLoading(false); }
    }, [search, filterStatus]);
    useEffect(() => { fetchData(); }, [fetchData]);

    const handleSave = async () => {
        if (!form.contact_name) { toast.error('Nom requis'); return; }
        try {
            if (editing) { await api.patch(`/leads/${editing.id}`, form); toast.success('Lead mis à jour'); }
            else { await api.post('/leads', form); toast.success('Lead créé'); }
            setModal(false); setEditing(null); setForm({ source: 'website', status: 'new' }); fetchData();
        } catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); }
    };
    const handleDelete = async (id) => { try { await api.delete(`/leads/${id}`); toast.success('Supprimé'); fetchData(); } catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); } };
    const handleConvert = async () => {
        if (!convertForm.deal_name) { toast.error('Nom du deal requis'); return; }
        try { await api.post(`/leads/${convertingId}/convert`, convertForm); toast.success('Lead converti avec succès !'); setConvertModal(false); fetchData(); }
        catch(e) { toast.error(e.response?.data?.detail || 'Échec conversion'); }
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-rose-500 to-pink-500 flex items-center justify-center text-white shadow-lg"><Target className="h-5 w-5" /></div>
                    <div><h1 className="text-xl font-bold tracking-tight">{t('Leads / Prospects')}</h1><p className="text-sm text-muted-foreground">{data.length} leads</p></div>
                </div>
                <div className="flex items-center gap-3">
                    <Select value={filterStatus} onValueChange={(v) => setFilterStatus(v === 'all' ? '' : v)}>
                        <SelectTrigger className="w-[140px]"><SelectValue placeholder="Statut" /></SelectTrigger>
                        <SelectContent><SelectItem value="all">{t('Tous')}</SelectItem>{STATUSES.map(s => <SelectItem key={s} value={s}>{s.toUpperCase()}</SelectItem>)}</SelectContent>
                    </Select>
                    <div className="relative"><Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" /><Input placeholder="Rechercher..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9 w-[200px]" /></div>
                    <Button onClick={() => { setEditing(null); setForm({ source: 'website', status: 'new' }); setModal(true); }}><Plus className="h-4 w-4 mr-2" /> {t('Nouveau Lead')}</Button>
                </div>
            </div>
            <Card><CardContent className="p-0">
                {loading ? <div className="flex justify-center py-20"><Spinner /></div> : data.length === 0 ? <EmptyState title={t('Aucun lead')} /> : (
                    <Table><TableHeader><TableRow><TableHead>{t('Contact')}</TableHead><TableHead>{t('Entreprise')}</TableHead><TableHead>Source</TableHead><TableHead>{t('Statut')}</TableHead><TableHead>{t('Valeur')}</TableHead><TableHead>Email</TableHead><TableHead className="w-[140px]">{t('Actions')}</TableHead></TableRow></TableHeader>
                        <TableBody>{data.map(row => (
                            <TableRow key={row.id}>
                                <TableCell className="font-semibold">{row.contact_name}</TableCell>
                                <TableCell>{row.company_name || '—'}</TableCell>
                                <TableCell><Badge variant={SOURCE_BADGE[row.source] || 'secondary'}>{row.source}</Badge></TableCell>
                                <TableCell><Badge variant={STATUS_BADGE[row.status] || 'secondary'}>{row.status?.toUpperCase()}</Badge></TableCell>
                                <TableCell>{row.estimated_value ? `${row.estimated_value.toLocaleString()} DT` : '—'}</TableCell>
                                <TableCell>{row.email || '—'}</TableCell>
                                <TableCell><div className="flex gap-1">
                                    {row.status === 'qualified' && <Button variant="ghost" size="icon" onClick={() => { setConvertingId(row.id); setConvertForm({ deal_name: `Deal - ${row.company_name}`, deal_value: row.estimated_value }); setConvertModal(true); }} className="text-emerald-500 hover:text-emerald-600"><ArrowRightLeft className="h-4 w-4" /></Button>}
                                    <Button variant="ghost" size="icon" onClick={() => { setEditing(row); setForm({ ...row }); setModal(true); }}><Pencil className="h-4 w-4" /></Button>
                                    <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(row.id)} className="text-destructive hover:text-destructive"><Trash2 className="h-4 w-4" /></Button>
                                </div></TableCell>
                            </TableRow>
                        ))}</TableBody></Table>
                )}
            </CardContent></Card>

            {/* Create/Edit */}
            <Dialog open={modal} onOpenChange={(o) => { if (!o) setModal(false); }}>
                <DialogContent className="sm:max-w-[600px]"><DialogHeader><DialogTitle>{editing ? t('Modifier Lead') : t('Nouveau Lead')}</DialogTitle></DialogHeader>
                    <div className="grid grid-cols-2 gap-4 py-4">
                        <div className="space-y-2"><Label>{t('Nom contact')} *</Label><Input value={form.contact_name || ''} onChange={(e) => setForm({ ...form, contact_name: e.target.value })} /></div>
                        <div className="space-y-2"><Label>{t('Entreprise')}</Label><Input value={form.company_name || ''} onChange={(e) => setForm({ ...form, company_name: e.target.value })} /></div>
                        <div className="space-y-2"><Label>Email</Label><Input type="email" value={form.email || ''} onChange={(e) => setForm({ ...form, email: e.target.value })} /></div>
                        <div className="space-y-2"><Label>{t('Téléphone')}</Label><Input value={form.phone || ''} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></div>
                        <div className="space-y-2"><Label>Source</Label><Select value={form.source || 'website'} onValueChange={(v) => setForm({ ...form, source: v })}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{SOURCES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent></Select></div>
                        <div className="space-y-2"><Label>{t('Statut')}</Label><Select value={form.status || 'new'} onValueChange={(v) => setForm({ ...form, status: v })}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{STATUSES.map(s => <SelectItem key={s} value={s}>{s.toUpperCase()}</SelectItem>)}</SelectContent></Select></div>
                        <div className="space-y-2 col-span-2"><Label>{t('Valeur estimée')} (DT)</Label><Input type="number" value={form.estimated_value || ''} onChange={(e) => setForm({ ...form, estimated_value: parseFloat(e.target.value) || 0 })} /></div>
                    </div>
                    <DialogFooter><Button variant="outline" onClick={() => setModal(false)}>{t('Annuler')}</Button><Button onClick={handleSave}>{t('Enregistrer')}</Button></DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Convert */}
            <Dialog open={convertModal} onOpenChange={(o) => { if (!o) setConvertModal(false); }}>
                <DialogContent><DialogHeader><DialogTitle>{t('Convertir le Lead')}</DialogTitle><DialogDescription>{t('Cette action va créer automatiquement un Compte, un Contact et un Deal.')}</DialogDescription></DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2"><Label>{t('Nom du Deal')} *</Label><Input value={convertForm.deal_name || ''} onChange={(e) => setConvertForm({ ...convertForm, deal_name: e.target.value })} /></div>
                        <div className="space-y-2"><Label>{t('Valeur du Deal')} (DT)</Label><Input type="number" value={convertForm.deal_value || ''} onChange={(e) => setConvertForm({ ...convertForm, deal_value: parseFloat(e.target.value) || 0 })} /></div>
                    </div>
                    <DialogFooter><Button variant="outline" onClick={() => setConvertModal(false)}>{t('Annuler')}</Button><Button onClick={handleConvert} className="bg-emerald-500 hover:bg-emerald-600">{t('Convertir')}</Button></DialogFooter>
                </DialogContent>
            </Dialog>
            <ConfirmDialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => handleDelete(deleteTarget)} />
        </div>
    );
};
export default LeadsPage;
