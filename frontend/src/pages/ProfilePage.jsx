import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Label, Separator, toast } from '../components/ui/shared';
import { Avatar, AvatarFallback } from '../components/ui/avatar';
import { User, Phone, Mail, Lock, Shield, Calendar, Pencil, Save } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const ROLE_LABELS = { admin: '👑 Administrateur', manager: '📈 Manager', commercial: '💼 Commercial', support: '🎧 Support', client: '🏢 Client' };
const ROLE_VARIANT = { admin: 'danger', manager: 'purple', commercial: 'warning', support: 'success', client: 'info' };

const ProfilePage = () => {
    const { user } = useAuth();
    const [editing, setEditing] = useState(false);
    const [profileForm, setProfileForm] = useState({ name: user?.name || '', phone: user?.phone || '' });
    const [passwordForm, setPasswordForm] = useState({ old_password: '', new_password: '' });
    const [loadingProfile, setLoadingProfile] = useState(false);
    const [loadingPassword, setLoadingPassword] = useState(false);

    const onUpdateProfile = async () => {
        if (!profileForm.name || profileForm.name.length < 2) { toast.error('Nom requis (min 2 car.)'); return; }
        setLoadingProfile(true);
        try { await api.patch('/auth/me', profileForm); toast.success('Profil mis à jour !'); setEditing(false); window.location.reload(); }
        catch (err) { toast.error(err?.response?.data?.detail || 'Erreur'); } finally { setLoadingProfile(false); }
    };
    const onChangePassword = async () => {
        if (!passwordForm.old_password || !passwordForm.new_password || passwordForm.new_password.length < 6) { toast.error('Mot de passe requis (min 6 car.)'); return; }
        setLoadingPassword(true);
        try { await api.post('/auth/me/change-password', passwordForm); toast.success('Mot de passe changé !'); setPasswordForm({ old_password: '', new_password: '' }); }
        catch (err) { toast.error(err?.response?.data?.detail || 'Ancien mot de passe incorrect'); } finally { setLoadingPassword(false); }
    };

    return (
        <div className="max-w-5xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left — Profile Card */}
                <Card className="lg:col-span-1">
                    <CardContent className="p-6 text-center">
                        <Avatar className="h-24 w-24 mx-auto mb-4 text-2xl"><AvatarFallback>{user?.name?.charAt(0)?.toUpperCase()}</AvatarFallback></Avatar>
                        <h2 className="text-xl font-bold">{user?.name}</h2>
                        <p className="text-sm text-muted-foreground mb-3">{user?.email}</p>
                        <Badge variant={ROLE_VARIANT[user?.role] || 'secondary'} className="text-sm px-4 py-1">{ROLE_LABELS[user?.role] || user?.role}</Badge>
                        <Separator className="my-5" />
                        <div className="space-y-3 text-left text-sm">
                            <div className="flex justify-between"><span className="text-muted-foreground flex items-center gap-2"><Phone className="h-3.5 w-3.5" /> Téléphone</span><span className="font-medium">{user?.phone || '—'}</span></div>
                            <div className="flex justify-between"><span className="text-muted-foreground flex items-center gap-2"><Shield className="h-3.5 w-3.5" /> Statut</span><Badge variant={user?.is_active ? 'success' : 'danger'}>{user?.is_active ? 'Actif' : 'Inactif'}</Badge></div>
                            <div className="flex justify-between"><span className="text-muted-foreground flex items-center gap-2"><Calendar className="h-3.5 w-3.5" /> Inscrit le</span><span>{user?.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR') : '—'}</span></div>
                        </div>
                    </CardContent>
                </Card>

                {/* Right — Forms */}
                <div className="lg:col-span-2 space-y-6">
                    <Card>
                        <CardHeader className="flex-row items-center justify-between">
                            <CardTitle className="flex items-center gap-2"><Pencil className="h-4 w-4" /> Modifier mon profil</CardTitle>
                            {!editing && <Button variant="ghost" size="sm" onClick={() => setEditing(true)}><Pencil className="h-3.5 w-3.5 mr-1" /> Modifier</Button>}
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div className="space-y-2"><Label>Nom complet</Label><Input disabled={!editing} value={profileForm.name} onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })} /></div>
                                <div className="space-y-2"><Label>Téléphone</Label><Input disabled={!editing} value={profileForm.phone} onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })} placeholder="+216 XX XXX XXX" /></div>
                            </div>
                            <div className="space-y-2">
                                <Label>Email</Label>
                                <Input disabled value={user?.email} className="text-muted-foreground" />
                                <p className="text-[11px] text-muted-foreground">L'email ne peut pas être modifié. Contactez l'administrateur.</p>
                            </div>
                            {editing && (
                                <div className="flex gap-2 pt-2">
                                    <Button onClick={onUpdateProfile} disabled={loadingProfile}><Save className="h-4 w-4 mr-2" /> {loadingProfile ? 'Enregistrement...' : 'Enregistrer'}</Button>
                                    <Button variant="outline" onClick={() => { setEditing(false); setProfileForm({ name: user.name, phone: user.phone }); }}>Annuler</Button>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader><CardTitle className="flex items-center gap-2"><Lock className="h-4 w-4" /> Changer le mot de passe</CardTitle></CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div className="space-y-2"><Label>Mot de passe actuel</Label><Input type="password" placeholder="••••••••" value={passwordForm.old_password} onChange={(e) => setPasswordForm({ ...passwordForm, old_password: e.target.value })} /></div>
                                <div className="space-y-2"><Label>Nouveau mot de passe</Label><Input type="password" placeholder="••••••••" value={passwordForm.new_password} onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })} /></div>
                            </div>
                            <Button onClick={onChangePassword} disabled={loadingPassword} className="bg-gradient-to-r from-amber-500 to-red-500 hover:from-amber-600 hover:to-red-600">
                                <Lock className="h-4 w-4 mr-2" /> {loadingPassword ? 'Changement...' : 'Changer le mot de passe'}
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
};
export default ProfilePage;
