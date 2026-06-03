import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '../components/ui/dialog';
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from '../components/ui/select';
import { Label, Spinner, EmptyState, toast } from '../components/ui/shared';
import { Plus, Pencil, Trash2, Briefcase, Zap, Search } from 'lucide-react';
import api from '../services/api';
import { useTranslation } from 'react-i18next';
import ConfirmDialog from '../components/ConfirmDialog';

const STAGE_BADGE = { qualification: 'info', proposal: 'warning', negotiation: 'warning', won: 'success', lost: 'danger' };
const STAGE_ORDER = ['qualification', 'proposal', 'negotiation', 'won', 'lost'];
const STAGE_BORDER = { qualification: 'border-blue-500', proposal: 'border-amber-500', negotiation: 'border-orange-500', won: 'border-emerald-500', lost: 'border-red-500' };

const DealsPage = () => {
    const [data, setData] = useState([]);
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modal, setModal] = useState(false);
    const [stageModal, setStageModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [selectedDeal, setSelectedDeal] = useState(null);
    const [filterStage, setFilterStage] = useState('');
    const [search, setSearch] = useState('');
    const [form, setForm] = useState({ stage: 'qualification', probability: 30 });
    const [stageForm, setStageForm] = useState({});
    const { t } = useTranslation();
    const [deleteTarget, setDeleteTarget] = useState(null);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const params = { size: 100, search };
            if (filterStage) params.stage = filterStage;
            const [r, a] = await Promise.all([api.get('/deals', { params }), api.get('/accounts', { params: { size: 100 } })]);
            setData(r.data.items || []); setAccounts(a.data.items || []);
        } catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); } finally { setLoading(false); }
    }, [filterStage, search]);
    useEffect(() => { fetchData(); }, [fetchData]);

    const handleSave = async () => {
        if (!form.name || !form.account_id) { toast.error('Champs requis'); return; }
        try {
            if (editing) { await api.patch(`/deals/${editing.id}`, form); toast.success('Deal mis à jour'); }
            else { await api.post('/deals', form); toast.success('Deal créé'); }
            setModal(false); setEditing(null); setForm({ stage: 'qualification', probability: 30 }); fetchData();
        } catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); }
    };
    const handleStageChange = async () => {
        try { await api.patch(`/deals/${selectedDeal.id}/stage`, stageForm); toast.success(`Étape → ${stageForm.stage?.toUpperCase()}`); setStageModal(false); fetchData(); }
        catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); }
    };
    const handleDelete = async (id) => { try { await api.delete(`/deals/${id}`); toast.success('Supprimé'); fetchData(); } catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); } };

    const totalPipeline = data.filter(d => !['won', 'lost'].includes(d.stage)).reduce((s, d) => s + (parseFloat(d.value) || 0), 0);
    const wonTotal = data.filter(d => d.stage === 'won').reduce((s, d) => s + (parseFloat(d.value) || 0), 0);

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center text-white shadow-lg"><Briefcase className="h-5 w-5" /></div>
                    <div><h1 className="text-xl font-bold tracking-tight">{t('Pipeline Commercial')}</h1><p className="text-sm text-muted-foreground">Pipeline: {totalPipeline.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} DT | {t('Gagné')}: {wonTotal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} DT</p></div>
                </div>
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input placeholder={t('Rechercher...')} value={search} onChange={e => setSearch(e.target.value)} className="pl-9 w-[200px]" />
                    </div>
                    <Select value={filterStage} onValueChange={(v) => setFilterStage(v === 'all' ? '' : v)}>
                        <SelectTrigger className="w-[150px]"><SelectValue placeholder="Étape" /></SelectTrigger>
                        <SelectContent><SelectItem value="all">{t('Toutes')}</SelectItem>{STAGE_ORDER.map(s => <SelectItem key={s} value={s}>{s.toUpperCase()}</SelectItem>)}</SelectContent>
                    </Select>
                    <Button onClick={() => { setEditing(null); setForm({ stage: 'qualification', probability: 30 }); setModal(true); }}><Plus className="h-4 w-4 mr-2" /> {t('Nouveau Deal')}</Button>
                </div>
            </div>

            {/* Pipeline Overview */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                {STAGE_ORDER.map(stage => {
                    const count = data.filter(d => d.stage === stage).length;
                    const value = data.filter(d => d.stage === stage).reduce((s, d) => s + (parseFloat(d.value) || 0), 0);
                    return (
                        <Card key={stage} className={`border-t-4 ${STAGE_BORDER[stage]}`}>
                            <CardContent className="p-4 text-center">
                                <p className="text-[11px] uppercase font-bold text-muted-foreground tracking-wider">{stage}</p>
                                <p className="text-2xl font-extrabold mt-1">{count}</p>
                                <p className="text-xs text-muted-foreground">{value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} DT</p>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>

            <Card><CardContent className="p-0">
                {loading ? <div className="flex justify-center py-20"><Spinner /></div> : data.length === 0 ? <EmptyState title={t('Aucun deal')} /> : (
                    <Table><TableHeader><TableRow><TableHead>Deal</TableHead><TableHead>{t('Compte')}</TableHead><TableHead>{t('Étape')}</TableHead><TableHead>{t('Montant')}</TableHead><TableHead>{t('Probabilité')}</TableHead><TableHead>{t('Clôture')}</TableHead><TableHead className="w-[140px]">{t('Actions')}</TableHead></TableRow></TableHeader>
                        <TableBody>{data.map(row => {
                            const acc = accounts.find(x => x.id === row.account_id); return (
                                <TableRow key={row.id}>
                                    <TableCell className="font-semibold">{row.name}</TableCell>
                                    <TableCell>{acc ? <Badge variant="info">{acc.name}</Badge> : '—'}</TableCell>
                                    <TableCell><Badge variant={STAGE_BADGE[row.stage] || 'secondary'}>{row.stage?.toUpperCase()}</Badge></TableCell>
                                    <TableCell className="font-medium">{(parseFloat(row.value) || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} DT</TableCell>
                                    <TableCell>
                                        <div className="flex items-center gap-2">
                                            <div className="h-2 w-16 rounded-full bg-muted overflow-hidden"><div className="h-full rounded-full transition-all" style={{ width: `${row.probability || 0}%`, background: (row.probability || 0) >= 70 ? '#10b981' : (row.probability || 0) >= 40 ? '#f59e0b' : '#ef4444' }} /></div>
                                            <span className="text-xs text-muted-foreground">{row.probability || 0}%</span>
                                        </div>
                                    </TableCell>
                                    <TableCell>{row.expected_close_date || '—'}</TableCell>
                                    <TableCell><div className="flex gap-1">
                                        <Button variant="ghost" size="icon" onClick={() => { setSelectedDeal(row); setStageForm({ stage: row.stage }); setStageModal(true); }} className="text-amber-500 hover:text-amber-600"><Zap className="h-4 w-4" /></Button>
                                        <Button variant="ghost" size="icon" onClick={() => { setEditing(row); setForm({ ...row }); setModal(true); }}><Pencil className="h-4 w-4" /></Button>
                                        <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(row.id)} className="text-destructive hover:text-destructive"><Trash2 className="h-4 w-4" /></Button>
                                    </div></TableCell>
                                </TableRow>
                            );
                        })}</TableBody></Table>
                )}
            </CardContent></Card>

            {/* Create/Edit */}
            <Dialog open={modal} onOpenChange={(o) => { if (!o) setModal(false); }}>
                <DialogContent className="sm:max-w-[600px]"><DialogHeader><DialogTitle>{editing ? t('Modifier Deal') : t('Nouveau Deal')}</DialogTitle></DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2"><Label>{t('Nom du Deal')} *</Label><Input value={form.name || ''} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
                        <div className="space-y-2"><Label>{t('Compte')} *</Label>
                            <Select value={form.account_id?.toString() || ''} onValueChange={(v) => setForm({ ...form, account_id: parseInt(v) })}><SelectTrigger><SelectValue placeholder={t('Sélectionner...')} /></SelectTrigger><SelectContent>{accounts.map(a => <SelectItem key={a.id} value={a.id.toString()}>{a.name}</SelectItem>)}</SelectContent></Select>
                        </div>
                        <div className="grid grid-cols-3 gap-4">
                            <div className="space-y-2"><Label>{t('Étape')}</Label><Select value={form.stage || 'qualification'} onValueChange={(v) => setForm({ ...form, stage: v })}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{STAGE_ORDER.map(s => <SelectItem key={s} value={s}>{s.toUpperCase()}</SelectItem>)}</SelectContent></Select></div>
                            <div className="space-y-2"><Label>{t('Montant')} (DT)</Label><Input type="number" value={form.value || ''} onChange={(e) => setForm({ ...form, value: parseFloat(e.target.value) || 0 })} /></div>
                            <div className="space-y-2"><Label>{t('Probabilité')} %</Label><Input type="number" min={0} max={100} value={form.probability || ''} onChange={(e) => setForm({ ...form, probability: parseInt(e.target.value) || 0 })} /></div>
                        </div>
                        <div className="space-y-2"><Label>{t('Date clôture prévue')}</Label><Input type="date" value={form.expected_close_date || ''} onChange={(e) => setForm({ ...form, expected_close_date: e.target.value })} /></div>
                        <div className="space-y-2"><Label>{t('Raison de perte')}</Label><Input placeholder={t('Si perdu...')} value={form.lost_reason || ''} onChange={(e) => setForm({ ...form, lost_reason: e.target.value })} /></div>
                    </div>
                    <DialogFooter><Button variant="outline" onClick={() => setModal(false)}>{t('Annuler')}</Button><Button onClick={handleSave}>{t('Enregistrer')}</Button></DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Stage Change */}
            <Dialog open={stageModal} onOpenChange={(o) => { if (!o) setStageModal(false); }}>
                <DialogContent><DialogHeader><DialogTitle>{t('Changer l\'étape')}</DialogTitle><DialogDescription>Deal: {selectedDeal?.name}</DialogDescription></DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2"><Label>{t('Nouvelle étape')} *</Label><Select value={stageForm.stage || ''} onValueChange={(v) => setStageForm({ ...stageForm, stage: v })}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{STAGE_ORDER.map(s => <SelectItem key={s} value={s}>{s.toUpperCase()}</SelectItem>)}</SelectContent></Select></div>
                        <div className="space-y-2"><Label>{t('Raison (si perdu)')}</Label><Input value={stageForm.lost_reason || ''} onChange={(e) => setStageForm({ ...stageForm, lost_reason: e.target.value })} /></div>
                    </div>
                    <DialogFooter><Button variant="outline" onClick={() => setStageModal(false)}>{t('Annuler')}</Button><Button onClick={handleStageChange}>{t('Confirmer')}</Button></DialogFooter>
                </DialogContent>
            </Dialog>
            <ConfirmDialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => handleDelete(deleteTarget)} />
        </div>
    );
};
export default DealsPage;
