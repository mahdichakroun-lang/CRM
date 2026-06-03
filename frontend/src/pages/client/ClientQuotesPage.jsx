import { useState, useEffect } from 'react';
import { Card, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../components/ui/table';
import { Spinner, EmptyState } from '../../components/ui/shared';
import { FileText, DollarSign } from 'lucide-react';
import api from '../../services/api';

const STATUS_BADGE = { draft: 'secondary', sent: 'info', accepted: 'success', rejected: 'danger' };
const STATUS_LABELS = { draft: 'Brouillon', sent: 'Envoyé', accepted: 'Accepté', rejected: 'Refusé' };

const ClientQuotesPage = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetch = async () => {
            try { const r = await api.get('/client/quotes'); setData(r.data || []); }
            catch { setData([]); } finally { setLoading(false); }
        };
        fetch();
    }, []);

    const totalAmount = data.reduce((s, q) => s + (q.amount || 0), 0);
    const acceptedAmount = data.filter(q => q.status === 'accepted').reduce((s, q) => s + (q.amount || 0), 0);

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white shadow-lg"><FileText className="h-5 w-5" /></div>
                <div><h1 className="text-xl font-bold tracking-tight">Mes Devis</h1><p className="text-sm text-muted-foreground">{data.length} devis</p></div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Card className="stat-card">
                    <CardContent className="p-5">
                        <div className="flex items-start justify-between">
                            <div><p className="text-sm text-muted-foreground font-medium">Total devis</p><p className="text-2xl font-extrabold mt-1">{totalAmount.toLocaleString()} DT</p></div>
                            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center"><DollarSign className="h-5 w-5 text-indigo-500" /></div>
                        </div>
                    </CardContent>
                </Card>
                <Card className="stat-card">
                    <CardContent className="p-5">
                        <div className="flex items-start justify-between">
                            <div><p className="text-sm text-muted-foreground font-medium">Devis acceptés</p><p className="text-2xl font-extrabold mt-1 text-emerald-500">{acceptedAmount.toLocaleString()} DT</p></div>
                            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center"><FileText className="h-5 w-5 text-emerald-500" /></div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Card><CardContent className="p-0">
                {loading ? <div className="flex justify-center py-20"><Spinner /></div> : data.length === 0 ? <EmptyState title="Aucun devis" /> : (
                    <Table><TableHeader><TableRow><TableHead>Référence</TableHead><TableHead>Projet</TableHead><TableHead>Montant</TableHead><TableHead>Statut</TableHead><TableHead>Date</TableHead></TableRow></TableHeader>
                        <TableBody>{data.map(row => (
                            <TableRow key={row.id}>
                                <TableCell className="font-semibold">{row.reference || 'N/A'}</TableCell>
                                <TableCell>{row.deal_name || '—'}</TableCell>
                                <TableCell className="font-medium">{(row.amount || 0).toLocaleString()} DT</TableCell>
                                <TableCell><Badge variant={STATUS_BADGE[row.status]}>{STATUS_LABELS[row.status] || row.status?.toUpperCase()}</Badge></TableCell>
                                <TableCell className="text-muted-foreground">{row.created_at ? new Date(row.created_at).toLocaleDateString('fr-FR') : '—'}</TableCell>
                            </TableRow>
                        ))}</TableBody></Table>
                )}
            </CardContent></Card>
        </div>
    );
};
export default ClientQuotesPage;
