import { useState, useEffect } from 'react';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input, Textarea } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../../components/ui/dialog';
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from '../../components/ui/select';
import { Label, Sheet, Spinner, EmptyState, toast } from '../../components/ui/shared';
import { Avatar, AvatarFallback } from '../../components/ui/avatar';
import { Plus, Eye, Send, Headphones } from 'lucide-react';
import api from '../../services/api';

const PRIORITY_BADGE = { low: 'success', medium: 'info', high: 'warning', urgent: 'danger' };
const STATUS_BADGE = { open: 'info', in_progress: 'info', waiting_customer: 'warning', resolved: 'success', closed: 'secondary' };
const PRIORITIES = ['low', 'medium', 'high', 'urgent'];
const CATEGORIES = [
    { value: 'bug', label: 'Bug' }, { value: 'support', label: 'Support' },
    { value: 'question', label: 'Question' }, { value: 'feature_request', label: 'Demande de fonctionnalité' },
    { value: 'incident', label: 'Incident' }, { value: 'other', label: 'Autre' },
];

const ClientTicketsPage = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modal, setModal] = useState(false);
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [selectedTicket, setSelectedTicket] = useState(null);
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [form, setForm] = useState({ category: 'support', priority: 'medium' });

    const fetchAll = async () => {
        setLoading(true);
        try { const r = await api.get('/client/tickets'); setData(r.data || []); }
        catch { toast.error('Erreur chargement tickets'); } finally { setLoading(false); }
    };
    useEffect(() => { fetchAll(); }, []);

    const openDetail = async (ticket) => {
        setSelectedTicket(ticket); setDrawerOpen(true);
        try { const r = await api.get(`/client/tickets/${ticket.id}/messages`); setMessages(r.data || []); } catch { setMessages([]); }
    };
    const sendMsg = async () => {
        if (!newMessage.trim()) return;
        try { await api.post(`/client/tickets/${selectedTicket.id}/messages`, { message: newMessage }); setNewMessage(''); const r = await api.get(`/client/tickets/${selectedTicket.id}/messages`); setMessages(r.data || []); toast.success('Message envoyé'); }
        catch { toast.error('Erreur envoi'); }
    };
    const handleCreate = async () => {
        if (!form.subject) { toast.error('Sujet requis'); return; }
        try { await api.post('/client/tickets', form); toast.success('Ticket créé !'); setModal(false); setForm({ category: 'support', priority: 'medium' }); fetchAll(); }
        catch { toast.error('Erreur création'); }
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white shadow-lg"><Headphones className="h-5 w-5" /></div>
                    <div><h1 className="text-xl font-bold tracking-tight">Mes Tickets</h1><p className="text-sm text-muted-foreground">{data.length} tickets</p></div>
                </div>
                <Button onClick={() => { setForm({ category: 'support', priority: 'medium' }); setModal(true); }} className="bg-gradient-to-r from-emerald-500 to-teal-600 shadow-lg"><Plus className="h-4 w-4 mr-2" /> Nouveau Ticket</Button>
            </div>

            <Card><CardContent className="p-0">
                {loading ? <div className="flex justify-center py-20"><Spinner /></div> : data.length === 0 ? <EmptyState title="Aucun ticket" description="Ouvrez votre premier ticket de support" /> : (
                    <Table><TableHeader><TableRow><TableHead className="w-[60px]">#</TableHead><TableHead>Sujet</TableHead><TableHead>Catégorie</TableHead><TableHead>Priorité</TableHead><TableHead>Statut</TableHead><TableHead>Date</TableHead><TableHead className="w-[60px]"></TableHead></TableRow></TableHeader>
                        <TableBody>{data.map(row => (
                            <TableRow key={row.id}>
                                <TableCell className="text-muted-foreground">#{row.id}</TableCell>
                                <TableCell className="font-semibold max-w-[250px] truncate">{row.subject}</TableCell>
                                <TableCell><Badge variant="outline">{row.category?.replace('_', ' ')}</Badge></TableCell>
                                <TableCell><Badge variant={PRIORITY_BADGE[row.priority]}>{row.priority?.toUpperCase()}</Badge></TableCell>
                                <TableCell><Badge variant={STATUS_BADGE[row.status]}>{row.status?.replace('_', ' ').toUpperCase()}</Badge></TableCell>
                                <TableCell className="text-muted-foreground">{row.created_at ? new Date(row.created_at).toLocaleDateString('fr-FR') : '—'}</TableCell>
                                <TableCell><Button variant="ghost" size="icon" onClick={() => openDetail(row)} className="text-emerald-500"><Eye className="h-4 w-4" /></Button></TableCell>
                            </TableRow>
                        ))}</TableBody></Table>
                )}
            </CardContent></Card>

            {/* Create */}
            <Dialog open={modal} onOpenChange={(o) => { if (!o) setModal(false); }}>
                <DialogContent><DialogHeader><DialogTitle>Nouveau Ticket</DialogTitle></DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2"><Label>Sujet *</Label><Input placeholder="Décrivez brièvement votre problème..." value={form.subject || ''} onChange={(e) => setForm({ ...form, subject: e.target.value })} /></div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2"><Label>Catégorie</Label><Select value={form.category} onValueChange={(v) => setForm({ ...form, category: v })}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{CATEGORIES.map(c => <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>)}</SelectContent></Select></div>
                            <div className="space-y-2"><Label>Priorité</Label><Select value={form.priority} onValueChange={(v) => setForm({ ...form, priority: v })}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{PRIORITIES.map(s => <SelectItem key={s} value={s}>{s.toUpperCase()}</SelectItem>)}</SelectContent></Select></div>
                        </div>
                        <div className="space-y-2"><Label>Description détaillée</Label><Textarea rows={4} placeholder="Expliquez le problème en détail..." value={form.description || ''} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
                    </div>
                    <DialogFooter><Button variant="outline" onClick={() => setModal(false)}>Annuler</Button><Button onClick={handleCreate} className="bg-emerald-500 hover:bg-emerald-600">Envoyer</Button></DialogFooter>
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
                        </div>
                        {selectedTicket.description && <Card><CardContent className="p-4 text-sm text-muted-foreground">{selectedTicket.description}</CardContent></Card>}
                        <div className="border-t pt-4">
                            <p className="text-sm font-semibold mb-3">Conversation ({messages.length})</p>
                            <div className="max-h-[350px] overflow-y-auto space-y-3 mb-4">
                                {messages.length === 0 && <p className="text-sm text-muted-foreground">Aucun message pour l'instant</p>}
                                {messages.map((m, i) => (
                                    <div key={m.id || i} className="p-3 rounded-xl border bg-muted/50 text-sm">
                                        <div className="flex items-center gap-2 mb-1">
                                            <Avatar className="h-6 w-6"><AvatarFallback className="text-[10px] bg-emerald-500 text-white">{(m.author_name || 'S')[0]}</AvatarFallback></Avatar>
                                            <span className="font-semibold text-xs">{m.author_name || 'Support'}</span>
                                            <span className="text-[10px] text-muted-foreground">{m.created_at ? new Date(m.created_at).toLocaleString('fr-FR') : ''}</span>
                                        </div>
                                        <p className="pl-8 text-muted-foreground">{m.message}</p>
                                    </div>
                                ))}
                            </div>
                            <div className="flex gap-2">
                                <Input value={newMessage} onChange={(e) => setNewMessage(e.target.value)} placeholder="Écrire un message..." className="flex-1" onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMsg(); } }} />
                                <Button onClick={sendMsg} size="icon" className="bg-emerald-500 hover:bg-emerald-600"><Send className="h-4 w-4" /></Button>
                            </div>
                        </div>
                    </div>
                )}
            </Sheet>
        </div>
    );
};
export default ClientTicketsPage;
