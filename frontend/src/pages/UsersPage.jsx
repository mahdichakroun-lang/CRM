import { useState, useEffect, useCallback } from 'react';
import {
    Table, TableHeader, TableRow, TableHead, TableBody, TableCell,
} from '../components/ui/table';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Spinner, toast } from '../components/ui/shared';
import { Plus, Pencil, Trash2, Search, Users, ShieldAlert } from 'lucide-react';
import api from '../services/api';
import { useTranslation } from 'react-i18next';
import ConfirmDialog from '../components/ConfirmDialog';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';

const ROLE_BADGE = { admin: 'danger', manager: 'warning', support: 'info', commercial: 'purple', client: 'secondary' };

const UsersPage = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modal, setModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [search, setSearch] = useState('');
    const [form, setForm] = useState({ role: 'commercial' });
    const { t } = useTranslation();
    const [deleteTarget, setDeleteTarget] = useState(null);
    const { user } = useAuth();
    const [total, setTotal] = useState(0);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const params = { size: 100 };
            if (search) params.search = search;
            const r = await api.get('/users', { params });
            setData(r.data.items);
            setTotal(r.data.total);
        } catch {
            toast.error(t('Erreur de chargement'));
        } finally {
            setLoading(false);
        }
    }, [t, search]);

    useEffect(() => { fetchData(); }, [fetchData]);

    if(user?.role !== 'admin' && user?.role !== 'manager') {
       return <Navigate to="/" replace />;
    }

    const handleSave = async () => {
        if (!form.name || !form.email || (!editing && !form.password)) {
            toast.error(t('Veuillez remplir les champs obligatoires')); return;
        }
        try {
            if (editing) {
                await api.patch(`/users/${editing.id}`, form);
                toast.success(t('Modifié'));
            } else {
                await api.post('/users', form);
                toast.success(t('Créé'));
            }
            setModal(false); setEditing(null); setForm({ role: 'commercial' }); fetchData();
        } catch(e) { 
            toast.error(e.response?.data?.detail || t('Erreur')); 
        }
    };
    
    const handleDelete = async (id) => { 
        try { await api.delete(`/users/${id}`); toast.success(t('Supprimé')); fetchData(); } 
        catch(e) { toast.error(e.response?.data?.detail || t('Erreur suppression')); } 
    };
    
    const openEdit = (r) => { setEditing(r); setForm({ name: r.name, email: r.email, role: r.role, phone: r.phone }); setModal(true); };

    if (loading && !data.length) return <div className="p-8 flex justify-center"><Spinner /></div>;

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-foreground">{t('Utilisateurs')}</h1>
                    <p className="text-sm text-muted-foreground mt-1">{total} {t('utilisateurs au total')}</p>
                </div>
                {user?.role === 'admin' && (
                    <Button onClick={() => { setEditing(null); setForm({ role: 'commercial' }); setModal(true); }} className="gap-2 bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 shadow-lg shadow-indigo-500/20">
                        <Plus className="h-4 w-4" /> {t('Nouvel utilisateur')}
                    </Button>
                )}
            </div>

            <div className="glass rounded-2xl border bg-card/50 shadow-sm overflow-hidden flex flex-col">
                <div className="p-4 border-b flex flex-col sm:flex-row gap-4 items-center bg-muted/20">
                    <div className="relative w-full sm:max-w-xs">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input placeholder={t('Rechercher un utilisateur...')} value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9 bg-background/50 border-muted-foreground/20 focus-visible:ring-indigo-500/50 rounded-xl" />
                    </div>
                </div>
                <div className="overflow-x-auto">
                    <Table>
                        <TableHeader className="bg-muted/30">
                            <TableRow className="hover:bg-transparent">
                                <TableHead className="w-[200px]">{t('Nom')}</TableHead>
                                <TableHead>{t('Email')}</TableHead>
                                <TableHead>{t('Rôle')}</TableHead>
                                <TableHead>{t('Téléphone')}</TableHead>
                                <TableHead className="text-right">{t('Actions')}</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading && !data.length ? (
                                <TableRow>
                                    <TableCell colSpan={5} className="h-24 text-center"><Spinner className="mx-auto" /></TableCell>
                                </TableRow>
                            ) : data.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={5} className="h-24 text-center text-muted-foreground flex flex-col items-center justify-center gap-2">
                                        <Users className="h-8 w-8 text-muted-foreground/50" />
                                        <p>{t('Aucun utilisateur trouvé')}</p>
                                    </TableCell>
                                </TableRow>
                            ) : (
                                data.map((row) => (
                                    <TableRow key={row.id} className="group hover:bg-muted/30 transition-colors">
                                        <TableCell className="font-medium">
                                            <div className="flex items-center gap-2">
                                                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary text-xs font-bold uppercase">
                                                    {row.name.charAt(0)}
                                                </div>
                                                {row.name}
                                            </div>
                                        </TableCell>
                                        <TableCell className="text-muted-foreground text-[13px]">{row.email}</TableCell>
                                        <TableCell>
                                            <Badge variant={ROLE_BADGE[row.role]}>{t(row.role.toUpperCase())}</Badge>
                                        </TableCell>
                                        <TableCell>{row.phone || '—'}</TableCell>
                                        <TableCell className="text-right">
                                            {user?.role === 'admin' && (
                                                <div className="flex justify-end gap-1">
                                                    <Button variant="ghost" size="icon" onClick={() => openEdit(row)} className="text-muted-foreground hover:text-indigo-600"><Pencil className="h-4 w-4" /></Button>
                                                    {user.id !== row.id && (
                                                        <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(row.id)} className="text-muted-foreground hover:text-destructive"><Trash2 className="h-4 w-4" /></Button>
                                                    )}
                                                </div>
                                            )}
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </div>
            </div>

            <Dialog open={modal} onOpenChange={setModal}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle className="text-xl flex items-center gap-2">
                            {editing ? <Pencil className="h-5 w-5 text-indigo-500" /> : <ShieldAlert className="h-5 w-5 text-indigo-500" />}
                            {editing ? t('Modifier l\'utilisateur') : t('Nouvel utilisateur')}
                        </DialogTitle>
                        <DialogDescription>{t('Remplissez les informations de l\'utilisateur')}</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">{t('Nom')} *</label>
                            <Input value={form.name || ''} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="John Doe" />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">{t('Email')} *</label>
                            <Input value={form.email || ''} onChange={e => setForm({ ...form, email: e.target.value })} placeholder="john@example.com" />
                        </div>
                        {!editing && (
                            <div className="space-y-2">
                                <label className="text-sm font-medium">{t('Mot de passe')} *</label>
                                <Input type="password" value={form.password || ''} onChange={e => setForm({ ...form, password: e.target.value })} placeholder="••••••" />
                            </div>
                        )}
                        <div className="space-y-2">
                            <label className="text-sm font-medium">{t('Rôle')} *</label>
                            <Select value={form.role || 'commercial'} onValueChange={v => setForm({ ...form, role: v })}>
                                <SelectTrigger><SelectValue /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="admin">{t('ADMIN')}</SelectItem>
                                    <SelectItem value="manager">{t('MANAGER')}</SelectItem>
                                    <SelectItem value="commercial">{t('COMMERCIAL')}</SelectItem>
                                    <SelectItem value="support">{t('SUPPORT')}</SelectItem>
                                    <SelectItem value="client">{t('CLIENT')}</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">{t('Téléphone')}</label>
                            <Input value={form.phone || ''} onChange={e => setForm({ ...form, phone: e.target.value })} />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setModal(false)}>{t('Annuler')}</Button>
                        <Button onClick={handleSave} className="bg-indigo-600 hover:bg-indigo-700">{t('Enregistrer')}</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
            <ConfirmDialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => handleDelete(deleteTarget)} />
        </div>
    );
};

export default UsersPage;
