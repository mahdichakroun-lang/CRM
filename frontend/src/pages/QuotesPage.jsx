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
import { Plus, Pencil, Trash2, FileText, Search } from 'lucide-react';
import api from '../services/api';
import { useTranslation } from 'react-i18next';
import ConfirmDialog from '../components/ConfirmDialog';

const STATUS_BADGE = { draft: 'secondary', sent: 'info', accepted: 'success', rejected: 'danger' };
const STATUSES = ['draft', 'sent', 'accepted', 'rejected'];

const QuotesPage = () => {
    const [data, setData] = useState([]);
    const [deals, setDeals] = useState([]);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const [modal, setModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({ status: 'draft' });
    const { t } = useTranslation();
    const [deleteTarget, setDeleteTarget] = useState(null);

    const fetchAll = useCallback(async () => {
        setLoading(true);
        try {
            const [r, d] = await Promise.all([api.get('/quotes', { params: { size: 100, search } }), api.get('/deals', { params: { size: 100 } })]);
            setData(r.data.items || []); setDeals(d.data.items || []);
        } catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); } finally { setLoading(false); }
    }, [search]);
    useEffect(() => { fetchAll(); }, [fetchAll]);

    const handleSave = async () => {
        if (!form.deal_id || !form.amount) { toast.error('Champs requis'); return; }
        try {
            if (editing) { await api.patch(`/quotes/${editing.id}`, form); toast.success('Devis mis à jour'); }
            else { await api.post('/quotes', form); toast.success('Devis créé'); }
            setModal(false); setEditing(null); setForm({ status: 'draft' }); fetchAll();
        } catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); }
    };
    const handleDelete = async (id) => { try { await api.delete(`/quotes/${id}`); toast.success('Supprimé'); fetchAll(); } catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); } };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center text-white shadow-lg"><FileText className="h-5 w-5" /></div>
                    <div><h1 className="text-xl font-bold tracking-tight">{t('Devis')}</h1><p className="text-sm text-muted-foreground">{data.length} {t('devis')}</p></div>
                </div>
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input placeholder={t('Rechercher...')} value={search} onChange={e => setSearch(e.target.value)} className="pl-9 w-[200px]" />
                    </div>
                    <Button onClick={() => { setEditing(null); setForm({ status: 'draft' }); setModal(true); }}><Plus className="h-4 w-4 mr-2" /> {t('Nouveau Devis')}</Button>
                </div>
            </div>
            <Card><CardContent className="p-0">
                {loading ? <div className="flex justify-center py-20"><Spinner /></div> : data.length === 0 ? <EmptyState title={t('Aucun devis')} /> : (
                    <Table><TableHeader><TableRow><TableHead>{t('Référence')}</TableHead><TableHead>Deal</TableHead><TableHead>{t('Montant')}</TableHead><TableHead>{t('Statut')}</TableHead><TableHead>{t('Notes')}</TableHead><TableHead className="w-[100px]">{t('Actions')}</TableHead></TableRow></TableHeader>
                        <TableBody>{data.map(row => {
                            const deal = deals.find(x => x.id === row.deal_id); return (
                                <TableRow key={row.id}>
                                    <TableCell className="font-semibold">{row.reference || '—'}</TableCell>
                                    <TableCell>{deal ? <Badge variant="info">{deal.name}</Badge> : '—'}</TableCell>
                                    <TableCell className="font-medium">{(row.amount || 0).toLocaleString()} DT</TableCell>
                                    <TableCell><Badge variant={STATUS_BADGE[row.status]}>{row.status?.toUpperCase()}</Badge></TableCell>
                                    <TableCell className="max-w-[200px] truncate">{row.notes || '—'}</TableCell>
                                    <TableCell><div className="flex gap-1"><Button variant="ghost" size="icon" onClick={() => { setEditing(row); setForm({ ...row }); setModal(true); }}><Pencil className="h-4 w-4" /></Button><Button variant="ghost" size="icon" onClick={() => setDeleteTarget(row.id)} className="text-destructive hover:text-destructive"><Trash2 className="h-4 w-4" /></Button></div></TableCell>
                                </TableRow>
                            );
                        })}</TableBody></Table>
                )}
            </CardContent></Card>
            <Dialog open={modal} onOpenChange={(o) => { if (!o) setModal(false); }}>
                <DialogContent><DialogHeader><DialogTitle>{editing ? t('Modifier Devis') : t('Nouveau Devis')}</DialogTitle></DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2"><Label>{t('Deal associé')} *</Label><Select value={form.deal_id?.toString() || ''} onValueChange={(v) => setForm({ ...form, deal_id: parseInt(v) })}><SelectTrigger><SelectValue placeholder={t('Sélectionner...')} /></SelectTrigger><SelectContent>{deals.map(d => <SelectItem key={d.id} value={d.id.toString()}>{d.name}</SelectItem>)}</SelectContent></Select></div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2"><Label>{t('Référence')}</Label><Input placeholder="DEV-2026-XXX" value={form.reference || ''} onChange={(e) => setForm({ ...form, reference: e.target.value })} /></div>
                            <div className="space-y-2"><Label>{t('Montant')} (DT) *</Label><Input type="number" value={form.amount || ''} onChange={(e) => setForm({ ...form, amount: parseFloat(e.target.value) || 0 })} /></div>
                        </div>
                        <div className="space-y-2"><Label>{t('Statut')}</Label><Select value={form.status || 'draft'} onValueChange={(v) => setForm({ ...form, status: v })}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{STATUSES.map(s => <SelectItem key={s} value={s}>{s.toUpperCase()}</SelectItem>)}</SelectContent></Select></div>
                        <div className="space-y-2"><Label>{t('Notes')}</Label><Textarea rows={2} value={form.notes || ''} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></div>
                    </div>
                    <DialogFooter><Button variant="outline" onClick={() => setModal(false)}>{t('Annuler')}</Button><Button onClick={handleSave}>{t('Enregistrer')}</Button></DialogFooter>
                </DialogContent>
            </Dialog>
            <ConfirmDialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => handleDelete(deleteTarget)} />
        </div>
    );
};
export default QuotesPage;
