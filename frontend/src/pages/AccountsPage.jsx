import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Label } from '../components/ui/shared';
import { Spinner, EmptyState, toast } from '../components/ui/shared';
import { Textarea } from '../components/ui/input';
import { Plus, Pencil, Trash2, Search, Building2 } from 'lucide-react';
import api from '../services/api';
import { useTranslation } from 'react-i18next';
import ConfirmDialog from '../components/ConfirmDialog';

const AccountsPage = () => {
    const [data, setData] = useState([]);
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
            const r = await api.get('/accounts', { params: { size: 100, search } });
            setData(r.data.items || []);
        } catch(e) { toast.error(e.response?.data?.detail || 'Erreur chargement'); }
        finally { setLoading(false); }
    }, [search]);

    useEffect(() => { fetchData(); }, [fetchData]);

    const handleSave = async () => {
        if (!form.name) { toast.error('Le nom est requis'); return; }
        try {
            if (editing) { await api.patch(`/accounts/${editing.id}`, form); toast.success('Compte mis à jour'); }
            else { await api.post('/accounts', form); toast.success('Compte créé'); }
            setModal(false); setEditing(null); setForm({}); fetchData();
        } catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); }
    };

    const handleDelete = async (id) => {
        try { await api.delete(`/accounts/${id}`); toast.success('Supprimé'); fetchData(); }
        catch(e) { toast.error(e.response?.data?.detail || 'Erreur suppression'); }
    };

    const openEdit = (record) => { setEditing(record); setForm({ ...record }); setModal(true); };
    const openCreate = () => { setEditing(null); setForm({}); setModal(true); };

    const fields = [
        ['name', t('Nom') + ' *', 'text'], ['sector', t('Secteur'), 'text'],
        ['industry', t('Industrie'), 'text'], ['website', t('Site web'), 'text'],
        ['phone', t('Téléphone'), 'text'], ['email', 'Email', 'email'],
        ['city', t('Ville'), 'text'], ['country', t('Pays'), 'text'],
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white shadow-lg">
                        <Building2 className="h-5 w-5" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold tracking-tight">{t('Comptes Clients')}</h1>
                        <p className="text-sm text-muted-foreground">{data.length} {t('entreprises enregistrées')}</p>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input placeholder="Rechercher..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9 w-[220px]" />
                    </div>
                    <Button onClick={openCreate}><Plus className="h-4 w-4 mr-2" /> {t('Nouveau Compte')}</Button>
                </div>
            </div>

            {/* Table */}
            <Card>
                <CardContent className="p-0">
                    {loading ? (
                        <div className="flex justify-center py-20"><Spinner /></div>
                    ) : data.length === 0 ? (
                        <EmptyState title={t('Aucun compte')} description={t('Créez votre premier compte client')} />
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>{t('Nom')}</TableHead>
                                    <TableHead>{t('Secteur')}</TableHead>
                                    <TableHead>{t('Industrie')}</TableHead>
                                    <TableHead>{t('Ville')}</TableHead>
                                    <TableHead>{t('Téléphone')}</TableHead>
                                    <TableHead>Email</TableHead>
                                    <TableHead className="w-[100px]">{t('Actions')}</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {data.map(row => (
                                    <TableRow key={row.id}>
                                        <TableCell className="font-semibold">{row.name}</TableCell>
                                        <TableCell>{row.sector ? <Badge variant="info">{row.sector}</Badge> : <span className="text-muted-foreground">—</span>}</TableCell>
                                        <TableCell>{row.industry || <span className="text-muted-foreground">—</span>}</TableCell>
                                        <TableCell>{row.city || <span className="text-muted-foreground">—</span>}</TableCell>
                                        <TableCell>{row.phone || <span className="text-muted-foreground">—</span>}</TableCell>
                                        <TableCell>{row.email ? <a href={`mailto:${row.email}`} className="text-primary hover:underline">{row.email}</a> : <span className="text-muted-foreground">—</span>}</TableCell>
                                        <TableCell>
                                            <div className="flex items-center gap-1">
                                                <Button variant="ghost" size="icon" onClick={() => openEdit(row)}><Pencil className="h-4 w-4" /></Button>
                                                <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(row.id)} className="text-destructive hover:text-destructive"><Trash2 className="h-4 w-4" /></Button>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>

            {/* Create / Edit Dialog */}
            <Dialog open={modal} onOpenChange={(open) => { if (!open) { setModal(false); setEditing(null); } }}>
                <DialogContent className="sm:max-w-[600px]">
                    <DialogHeader>
                        <DialogTitle>{editing ? t('Modifier le Compte') : t('Nouveau Compte')}</DialogTitle>
                    </DialogHeader>
                    <div className="grid grid-cols-2 gap-4 py-4">
                        {fields.map(([key, label, type]) => (
                            <div key={key} className="space-y-2">
                                <Label>{label}</Label>
                                <Input type={type} value={form[key] || ''} onChange={(e) => setForm({ ...form, [key]: e.target.value })} />
                            </div>
                        ))}
                    </div>
                    <div className="space-y-2">
                        <Label>{t('Notes')}</Label>
                        <Textarea rows={3} value={form.notes || ''} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setModal(false)}>{t('Annuler')}</Button>
                        <Button onClick={handleSave}>{t('Enregistrer')}</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
            <ConfirmDialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => handleDelete(deleteTarget)} />
        </div>
    );
};

export default AccountsPage;
