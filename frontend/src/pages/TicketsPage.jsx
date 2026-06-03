import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input, Textarea } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from '../components/ui/select';
import { Label, Sheet, Spinner, EmptyState, toast } from '../components/ui/shared';
import { Avatar, AvatarFallback } from '../components/ui/avatar';
import { Plus, Pencil, Trash2, Search, Headphones, Eye, Send, Mail } from 'lucide-react';
import api from '../services/api';
import { useTranslation } from 'react-i18next';
import ConfirmDialog from '../components/ConfirmDialog';

const PRIORITY_BADGE = { low: 'success', medium: 'info', high: 'warning', urgent: 'danger' };
const STATUS_BADGE = { open: 'info', in_progress: 'info', waiting_customer: 'warning', resolved: 'success', closed: 'secondary' };
const CATEGORY_BADGE = { bug: 'danger', feature_request: 'purple', support: 'info', question: 'info', incident: 'warning', other: 'secondary' };
const PRIORITIES = ['low', 'medium', 'high', 'urgent'];
const STATUSES = ['open', 'in_progress', 'waiting_customer', 'resolved', 'closed'];
const CATEGORIES = ['bug', 'feature_request', 'support', 'question', 'incident', 'other'];
const EMPTY_FORM = { priority: 'medium', category: 'support' };

const TicketsPage = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modal, setModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [selectedTicket, setSelectedTicket] = useState(null);
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [accounts, setAccounts] = useState([]);
    const [contacts, setContacts] = useState([]);
    const [users, setUsers] = useState([]);
    const [filterStatus, setFilterStatus] = useState('');
    const [filterPriority, setFilterPriority] = useState('');
    const [search, setSearch] = useState('');
    const [emailModal, setEmailModal] = useState(false);
    const [emailLoading, setEmailLoading] = useState(false);
    const [emailForm, setEmailForm] = useState({});
    const [form, setForm] = useState(EMPTY_FORM);
    const { t } = useTranslation();
    const [deleteTarget, setDeleteTarget] = useState(null);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const params = { size: 100, search };
            if (filterStatus) params.status = filterStatus;
            if (filterPriority) params.priority = filterPriority;
            const [r, a, u] = await Promise.all([
                api.get('/tickets', { params }),
                api.get('/accounts', { params: { size: 100 } }),
                api.get('/users/assignable').catch(() => ({ data: [] })),
            ]);
            setData(r.data.items || []);
            setAccounts(a.data.items || []);
            setUsers(u.data || []);
        } catch(e) { toast.error(e.response?.data?.detail || 'Erreur chargement'); } finally { setLoading(false); }
    }, [search, filterStatus, filterPriority]);
    useEffect(() => { fetchData(); }, [fetchData]);

    const loadContacts = useCallback(async (accountId) => {
        if (!accountId) {
            setContacts([]);
            return;
        }
        try {
            const r = await api.get('/contacts', { params: { account_id: accountId, size: 100 } });
            setContacts(r.data.items || []);
        } catch {
            setContacts([]);
        }
    }, []);

    const openDetail = async (ticket) => {
        setSelectedTicket(ticket); setDrawerOpen(true);
        try { const r = await api.get(`/tickets/${ticket.id}/messages`); setMessages(r.data || []); } catch(e) { setMessages([]); }
    };

    const sendMessage = async () => {
        if (!newMessage.trim()) return;
        try { await api.post(`/tickets/${selectedTicket.id}/messages`, { message: newMessage }); setNewMessage(''); const r = await api.get(`/tickets/${selectedTicket.id}/messages`); setMessages(r.data || []); toast.success('Message envoyé'); }
        catch(e) { toast.error(e.response?.data?.detail || 'Erreur envoi'); }
    };

    const handleSave = async () => {
        if (!form.subject || !form.account_id) { toast.error('Champs requis'); return; }
        try {
            const payload = { ...form };
            if (!editing) {
                delete payload.status;
            }
            if (editing) { await api.patch(`/tickets/${editing.id}`, payload); toast.success('Ticket mis à jour'); }
            else { await api.post('/tickets', payload); toast.success('Ticket créé'); }
            setModal(false); setEditing(null); setContacts([]); setForm({ ...EMPTY_FORM }); fetchData();
        } catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); }
    };
    const handleDelete = async (id) => { try { await api.delete(`/tickets/${id}`); toast.success('Supprimé'); fetchData(); } catch(e) { toast.error(e.response?.data?.detail || 'Erreur'); } };

    const handleSendEmail = async () => {
        if (!emailForm.emailMessage) { toast.error('Message requis'); return; }
        setEmailLoading(true);
        try {
            const res = await api.post(`/email/ticket/${selectedTicket.id}/notify`, { subject: emailForm.emailSubject || null, message: emailForm.emailMessage });
            toast.success(res.data.message);
            setEmailModal(false); setEmailForm({});
        } catch (err) { toast.error(err.response?.data?.detail || 'Erreur envoi email'); } finally { setEmailLoading(false); }
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-yellow-500 flex items-center justify-center text-white shadow-lg"><Headphones className="h-5 w-5" /></div>
                    <div><h1 className="text-xl font-bold tracking-tight">{t('Helpdesk — Tickets')}</h1><p className="text-sm text-muted-foreground">{data.length} tickets</p></div>
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                    <Select value={filterPriority} onValueChange={(v) => setFilterPriority(v === 'all' ? '' : v)}><SelectTrigger className="w-[120px]"><SelectValue placeholder="Priorité" /></SelectTrigger><SelectContent><SelectItem value="all">Toutes</SelectItem>{PRIORITIES.map(s => <SelectItem key={s} value={s}>{s.toUpperCase()}</SelectItem>)}</SelectContent></Select>
                    <Select value={filterStatus} onValueChange={(v) => setFilterStatus(v === 'all' ? '' : v)}><SelectTrigger className="w-[140px]"><SelectValue placeholder="Statut" /></SelectTrigger><SelectContent><SelectItem value="all">Tous</SelectItem>{STATUSES.map(s => <SelectItem key={s} value={s}>{s.replace('_', ' ').toUpperCase()}</SelectItem>)}</SelectContent></Select>
                    <div className="relative"><Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" /><Input placeholder="Rechercher..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9 w-[180px]" /></div>
                    <Button onClick={() => { setEditing(null); setContacts([]); setForm({ ...EMPTY_FORM }); setModal(true); }}><Plus className="h-4 w-4 mr-2" /> {t('Nouveau Ticket')}</Button>
                </div>
            </div>

            <Card><CardContent className="p-0">
                {loading ? <div className="flex justify-center py-20"><Spinner /></div> : data.length === 0 ? <EmptyState title={t('Aucun ticket')} /> : (
                    <Table><TableHeader><TableRow><TableHead className="w-[60px]">#</TableHead><TableHead>{t('Sujet')}</TableHead><TableHead>{t('Priorité')}</TableHead><TableHead>{t('Statut')}</TableHead><TableHead>{t('Catégorie')}</TableHead><TableHead>{t('Compte')}</TableHead><TableHead className="w-[140px]">{t('Actions')}</TableHead></TableRow></TableHeader>
                        <TableBody>{data.map(row => {
                            const acc = accounts.find(x => x.id === row.account_id); return (
                                <TableRow key={row.id}>
                                    <TableCell className="text-muted-foreground">#{row.id}</TableCell>
                                    <TableCell className="font-semibold max-w-[250px] truncate">{row.subject}</TableCell>
                                    <TableCell><Badge variant={PRIORITY_BADGE[row.priority]}>{row.priority?.toUpperCase()}</Badge></TableCell>
                                    <TableCell><Badge variant={STATUS_BADGE[row.status]}>{row.status?.replace('_', ' ').toUpperCase()}</Badge></TableCell>
                                    <TableCell><Badge variant={CATEGORY_BADGE[row.category]}>{row.category?.replace('_', ' ')}</Badge></TableCell>
                                    <TableCell>{acc?.name || '—'}</TableCell>
                                    <TableCell><div className="flex gap-1">
                                        <Button variant="ghost" size="icon" onClick={() => openDetail(row)} className="text-emerald-500"><Eye className="h-4 w-4" /></Button>
                                        <Button variant="ghost" size="icon" onClick={() => { setEditing(row); setForm({ ...row }); loadContacts(row.account_id); setModal(true); }}><Pencil className="h-4 w-4" /></Button>
                                        <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(row.id)} className="text-destructive hover:text-destructive"><Trash2 className="h-4 w-4" /></Button>
                                    </div></TableCell>
                                </TableRow>
                            );
                        })}</TableBody></Table>
                )}
            </CardContent></Card>

            {/* Create/Edit */}
            <Dialog open={modal} onOpenChange={(o) => { if (!o) setModal(false); }}>
                <DialogContent className="sm:max-w-[600px]"><DialogHeader><DialogTitle>{editing ? t('Modifier Ticket') : t('Nouveau Ticket')}</DialogTitle></DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2"><Label>{t('Sujet')} *</Label><Input value={form.subject || ''} onChange={(e) => setForm({ ...form, subject: e.target.value })} /></div>
                        <div className="grid grid-cols-2 gap-3">
                            <div className="space-y-2"><Label>{t('Compte')} *</Label><Select value={form.account_id?.toString() || ''} onValueChange={(v) => { const aid = parseInt(v); setForm({ ...form, account_id: aid, contact_id: null }); loadContacts(aid); }}><SelectTrigger><SelectValue placeholder={t('Sélectionner...')} /></SelectTrigger><SelectContent>{accounts.map(a => <SelectItem key={a.id} value={a.id.toString()}>{a.name}</SelectItem>)}</SelectContent></Select></div>
                            <div className="space-y-2"><Label>{t('Contact')}</Label><Select value={form.contact_id?.toString() || ''} onValueChange={(v) => setForm({ ...form, contact_id: v ? parseInt(v) : null })}><SelectTrigger><SelectValue placeholder={t('Aucun')} /></SelectTrigger><SelectContent><SelectItem value="">— {t('Aucun')} —</SelectItem>{contacts.map(c => <SelectItem key={c.id} value={c.id.toString()}>{c.first_name} {c.last_name}</SelectItem>)}</SelectContent></Select></div>
                        </div>
                            <div className="space-y-2"><Label>{t('Assigné à')}</Label><Select value={form.assigned_to?.toString() || ''} onValueChange={(v) => setForm({ ...form, assigned_to: v ? parseInt(v) : null })}><SelectTrigger><SelectValue placeholder={t('Non assigné')} /></SelectTrigger><SelectContent><SelectItem value="">— {t('Non assigné')} —</SelectItem>{users.map(u => <SelectItem key={u.id} value={u.id.toString()}>{u.name} ({u.role})</SelectItem>)}</SelectContent></Select></div>
                        <div className="grid grid-cols-3 gap-3">
                            <div className="space-y-2"><Label>{t('Catégorie')}</Label><Select value={form.category || 'support'} onValueChange={(v) => setForm({ ...form, category: v })}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{CATEGORIES.map(s => <SelectItem key={s} value={s}>{s.replace('_', ' ')}</SelectItem>)}</SelectContent></Select></div>
                            <div className="space-y-2"><Label>{t('Priorité')}</Label><Select value={form.priority || 'medium'} onValueChange={(v) => setForm({ ...form, priority: v })}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{PRIORITIES.map(s => <SelectItem key={s} value={s}>{s.toUpperCase()}</SelectItem>)}</SelectContent></Select></div>
                            {editing ? <div className="space-y-2"><Label>{t('Statut')}</Label><Select value={form.status || 'open'} onValueChange={(v) => setForm({ ...form, status: v })}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{STATUSES.map(s => <SelectItem key={s} value={s}>{s.replace('_', ' ').toUpperCase()}</SelectItem>)}</SelectContent></Select></div> : <div />}
                        </div>
                        <div className="space-y-2"><Label>Description</Label><Textarea rows={3} value={form.description || ''} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
                    </div>
                    <DialogFooter><Button variant="outline" onClick={() => setModal(false)}>{t('Annuler')}</Button><Button onClick={handleSave}>{t('Enregistrer')}</Button></DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Detail Sheet */}
            <Sheet open={drawerOpen} onClose={() => setDrawerOpen(false)} title={`Ticket #${selectedTicket?.id}`}>
                {selectedTicket && (
                    <div className="space-y-5">
                        <h3 className="text-lg font-bold">{selectedTicket.subject}</h3>
                        <div className="flex flex-wrap gap-2">
                            <Badge variant={PRIORITY_BADGE[selectedTicket.priority]}>{selectedTicket.priority?.toUpperCase()}</Badge>
                            <Badge variant={STATUS_BADGE[selectedTicket.status]}>{selectedTicket.status?.replace('_', ' ').toUpperCase()}</Badge>
                            <Badge variant={CATEGORY_BADGE[selectedTicket.category]}>{selectedTicket.category?.replace('_', ' ')}</Badge>
                        </div>
                        {selectedTicket.description && <Card><CardContent className="p-4 text-sm text-muted-foreground">{selectedTicket.description}</CardContent></Card>}

                        <Button onClick={() => { setEmailForm({ emailSubject: `À propos de votre ticket #${selectedTicket.id} — ${selectedTicket.subject}`, emailMessage: '' }); setEmailModal(true); }} className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-lg">
                            <Mail className="h-4 w-4 mr-2" /> {t('Envoyer un email au client')}
                        </Button>

                        <div className="border-t pt-4">
                            <p className="text-sm font-semibold mb-3">{t('Messages')} ({messages.length})</p>
                            <div className="max-h-[350px] overflow-y-auto space-y-3 mb-4">
                                {messages.length === 0 && <p className="text-sm text-muted-foreground">{t('Aucun message')}</p>}
                                {messages.map((m, i) => (
                                    <div key={m.id || i} className={`p-3 rounded-xl border text-sm ${m.is_internal ? 'bg-primary/5 border-primary/20' : 'bg-muted/50'}`}>
                                        <div className="flex items-center gap-2 mb-1">
                                            <Avatar className="h-6 w-6"><AvatarFallback className="text-[10px]">{(m.author_name || 'U')[0]}</AvatarFallback></Avatar>
                                            <span className="font-semibold text-xs">{m.author_name || 'Utilisateur'}</span>
                                            {m.is_internal && <Badge variant="purple" className="text-[10px]">INTERNE</Badge>}
                                        </div>
                                        <p className="pl-8 text-muted-foreground">{m.message}</p>
                                    </div>
                                ))}
                            </div>
                            <div className="flex gap-2">
                                <Input value={newMessage} onChange={(e) => setNewMessage(e.target.value)} placeholder="Écrire un message..." className="flex-1" onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }} />
                                <Button onClick={sendMessage} size="icon"><Send className="h-4 w-4" /></Button>
                            </div>
                        </div>
                    </div>
                )}
            </Sheet>

            {/* Email Modal */}
            <Dialog open={emailModal} onOpenChange={(o) => { if (!o) setEmailModal(false); }}>
                <DialogContent><DialogHeader><DialogTitle><Mail className="inline h-4 w-4 mr-2" />Envoyer un email au client</DialogTitle></DialogHeader>
                    <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-xl p-3 text-sm text-blue-700 dark:text-blue-300">L'email sera envoyé au client associé au ticket #{selectedTicket?.id}</div>
                    <div className="space-y-4 py-2">
                        <div className="space-y-2"><Label>Sujet</Label><Input value={emailForm.emailSubject || ''} onChange={(e) => setEmailForm({ ...emailForm, emailSubject: e.target.value })} /></div>
                        <div className="space-y-2"><Label>Message *</Label><Textarea rows={4} placeholder="Écrivez votre message ici..." value={emailForm.emailMessage || ''} onChange={(e) => setEmailForm({ ...emailForm, emailMessage: e.target.value })} /></div>
                    </div>
                    <DialogFooter><Button variant="outline" onClick={() => setEmailModal(false)}>Annuler</Button><Button onClick={handleSendEmail} disabled={emailLoading} className="bg-gradient-to-r from-blue-600 to-blue-700">{emailLoading ? 'Envoi...' : 'Envoyer'}</Button></DialogFooter>
                </DialogContent>
            </Dialog>
            <ConfirmDialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => handleDelete(deleteTarget)} />
        </div>
    );
};
export default TicketsPage;
