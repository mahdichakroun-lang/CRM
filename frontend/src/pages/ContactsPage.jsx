import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from '../components/ui/select';
import { Label, Spinner, EmptyState, toast } from '../components/ui/shared';
import { Plus, Pencil, Trash2, Search, Users } from 'lucide-react';
import api from '../services/api';
import { useTranslation } from 'react-i18next';
import ConfirmDialog from '../components/ConfirmDialog';

const ContactsPage = () => {
    const [data, setData] = useState([]);
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modal, setModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [search, setSearch] = useState('');
    const [form, setForm] = useState({});
    const { t } = useTranslation();
    const [deleteTarget, setDeleteTarget] = useState(null);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const [r, a] = await Promise.all([api.get('/contacts', { params: { size: 100, search } }), api.get('/accounts', { params: { size: 100 } })]);
            setData(r.data.items || []); setAccounts(a.data.items || []);
        } catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); } finally { setLoading(false); }
    }, [search]);
    useEffect(() => { fetchData(); }, [fetchData]);

    const handleSave = async () => {
        if (!form.first_name || !form.last_name || !form.account_id) { toast.error('Champs requis manquants'); return; }
        try {
            if (editing) { await api.patch(`/contacts/${editing.id}`, form); toast.success('Contact mis à jour'); }
            else { await api.post('/contacts', form); toast.success('Contact créé'); }
            setModal(false); setEditing(null); setForm({}); fetchData();
        } catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); }
    };
    const handleDelete = async (id) => { try { await api.delete(`/contacts/${id}`); toast.success('Supprimé'); fetchData(); } catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); } };
    const openEdit = (r) => { setEditing(r); setForm({ ...r }); setModal(true); };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-500 to-cyan-500 flex items-center justify-center text-white shadow-lg"><Users className="h-5 w-5" /></div>
                    <div><h1 className="text-xl font-bold tracking-tight">{t('Contacts')}</h1><p className="text-sm text-muted-foreground">{data.length} contacts</p></div>
                </div>
                <div className="flex items-center gap-3">
                    <div className="relative"><Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" /><Input placeholder="Rechercher..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9 w-[220px]" /></div>
                    <Button onClick={() => { setEditing(null); setForm({}); setModal(true); }}><Plus className="h-4 w-4 mr-2" /> {t('Nouveau Contact')}</Button>
                </div>
            </div>
            <Card><CardContent className="p-0">
                {loading ? <div className="flex justify-center py-20"><Spinner /></div> : data.length === 0 ? <EmptyState title={t('Aucun contact')} /> : (
                    <Table><TableHeader><TableRow>
                        <TableHead>{t('Prénom')}</TableHead><TableHead>{t('Nom')}</TableHead><TableHead>Email</TableHead><TableHead>{t('Poste')}</TableHead><TableHead>{t('Téléphone')}</TableHead><TableHead>{t('Entreprise')}</TableHead><TableHead className="w-[100px]">{t('Actions')}</TableHead>
                    </TableRow></TableHeader><TableBody>
                            {data.map(row => {
                                const acc = accounts.find(x => x.id === row.account_id); return (
                                    <TableRow key={row.id}>
                                        <TableCell className="font-semibold">{row.first_name}</TableCell>
                                        <TableCell>{row.last_name}</TableCell>
                                        <TableCell>{row.email ? <a href={`mailto:${row.email}`} className="text-primary hover:underline">{row.email}</a> : '—'}</TableCell>
                                        <TableCell>{row.position ? <Badge variant="purple">{row.position}</Badge> : '—'}</TableCell>
                                        <TableCell>{row.phone || '—'}</TableCell>
                                        <TableCell>{acc ? <Badge variant="info">{acc.name}</Badge> : '—'}</TableCell>
                                        <TableCell><div className="flex gap-1"><Button variant="ghost" size="icon" onClick={() => openEdit(row)}><Pencil className="h-4 w-4" /></Button><Button variant="ghost" size="icon" onClick={() => setDeleteTarget(row.id)} className="text-destructive hover:text-destructive"><Trash2 className="h-4 w-4" /></Button></div></TableCell>
                                    </TableRow>
                                );
                            })}
                        </TableBody></Table>
                )}
            </CardContent></Card>
            <Dialog open={modal} onOpenChange={(o) => { if (!o) { setModal(false); setEditing(null); } }}>
                <DialogContent className="sm:max-w-[600px]"><DialogHeader><DialogTitle>{editing ? t('Modifier') : t('Nouveau Contact')}</DialogTitle></DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2"><Label>{t('Entreprise')} *</Label>
                            <Select value={form.account_id?.toString() || ''} onValueChange={(v) => setForm({ ...form, account_id: parseInt(v) })}>
                                <SelectTrigger><SelectValue placeholder={t('Sélectionner...')} /></SelectTrigger>
                                <SelectContent>{accounts.map(a => <SelectItem key={a.id} value={a.id.toString()}>{a.name}</SelectItem>)}</SelectContent>
                            </Select>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2"><Label>{t('Prénom')} *</Label><Input value={form.first_name || ''} onChange={(e) => setForm({ ...form, first_name: e.target.value })} /></div>
                            <div className="space-y-2"><Label>{t('Nom')} *</Label><Input value={form.last_name || ''} onChange={(e) => setForm({ ...form, last_name: e.target.value })} /></div>
                            <div className="space-y-2"><Label>Email</Label><Input type="email" value={form.email || ''} onChange={(e) => setForm({ ...form, email: e.target.value })} /></div>
                            <div className="space-y-2"><Label>{t('Téléphone')}</Label><Input value={form.phone || ''} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></div>
                        </div>
                        <div className="space-y-2"><Label>{t('Poste')}</Label><Input value={form.position || ''} onChange={(e) => setForm({ ...form, position: e.target.value })} /></div>
                    </div>
                    <DialogFooter><Button variant="outline" onClick={() => setModal(false)}>{t('Annuler')}</Button><Button onClick={handleSave}>{t('Enregistrer')}</Button></DialogFooter>
                </DialogContent>
            </Dialog>
            <ConfirmDialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => handleDelete(deleteTarget)} />
        </div>
    );
};
export default ContactsPage;
