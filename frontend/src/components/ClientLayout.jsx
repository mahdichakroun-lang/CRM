import { Outlet, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { cn } from '../lib/utils';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Button } from './ui/button';
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from './ui/dropdown-menu';
import { Separator, Spinner } from './ui/shared';
import { LayoutDashboard, Headphones, FileText, Sun, Moon, LogOut, User, ChevronRight, Bell } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from './LanguageSwitcher';
import ChatbotWidget from './ChatbotWidget';
import ScrollToTop from './ScrollToTop';

const menuItems = [
    { key: '/portal', icon: LayoutDashboard, label: 'Mon Espace' },
    { key: '/portal/tickets', icon: Headphones, label: 'Mes Tickets' },
    { key: '/portal/quotes', icon: FileText, label: 'Mes Devis' },
];

const pageTitle = {
    '/portal': 'Mon Espace', '/portal/tickets': 'Mes Tickets',
    '/portal/quotes': 'Mes Devis', '/portal/profile': 'Mon Profil',
};

const ClientLayout = () => {
    const { user, loading, logout } = useAuth();
    const { isDark, toggleTheme } = useTheme();
    const navigate = useNavigate();
    const location = useLocation();
    const { t } = useTranslation();

    if (loading) return <div className="h-screen flex items-center justify-center bg-background"><Spinner size="lg" /></div>;
    if (!user) return <Navigate to="/login" replace />;
    if (user.role !== 'client') return <Navigate to="/" replace />;

    return (
        <div className="h-screen flex overflow-hidden">
            {/* Sidebar */}
            <aside className="w-[260px] h-full flex flex-col border-r border-sidebar-border bg-sidebar shrink-0 z-30">
                <div className="h-14 flex items-center px-5 gap-3 border-b border-sidebar-border shrink-0">
                    <div className="w-9 h-9 rounded-xl overflow-hidden bg-white/10 p-0.5 flex items-center justify-center shrink-0 ring-1 ring-emerald-500/20">
                        <img src="/FRS_logo.jpg" alt="FRS Logo" className="object-contain w-full h-full rounded-lg" />
                    </div>
                    <div className="flex flex-col">
                        <span className="font-bold text-[15px] tracking-tight leading-none">{t('Portail Client')}</span>
                        <span className="text-[10px] text-muted-foreground mt-0.5">Enterprise Suite</span>
                    </div>
                </div>
                <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
                    {menuItems.map(item => {
                        const Icon = item.icon;
                        const active = location.pathname === item.key;
                        return (
                            <button key={item.key} onClick={() => navigate(item.key)}
                                className={cn('w-full flex items-center gap-3 rounded-xl text-[13px] font-medium px-3 h-10 transition-all duration-200 group relative',
                                    active ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'text-muted-foreground hover:bg-accent/80 hover:text-foreground'
                                )}>
                                {active && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r-full bg-emerald-500" />}
                                <Icon className={cn('w-[17px] h-[17px] shrink-0 transition-colors', active && 'text-emerald-600 dark:text-emerald-400')} />
                                <span>{t(item.label)}</span>
                            </button>
                        );
                    })}
                    <Separator className="my-3 mx-2 opacity-30" />
                    <button onClick={() => navigate('/portal/profile')}
                        className={cn('w-full flex items-center gap-3 rounded-xl text-[13px] font-medium px-3 h-10 transition-all duration-200 group relative',
                            location.pathname === '/portal/profile' ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'text-muted-foreground hover:bg-accent/80 hover:text-foreground'
                        )}>
                        {location.pathname === '/portal/profile' && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r-full bg-emerald-500" />}
                        <User className="w-[17px] h-[17px] shrink-0" />
                        <span>{t('Mon Profil')}</span>
                    </button>
                </nav>

                {/* Bottom user */}
                <div className="p-3 border-t border-sidebar-border">
                    <div className="flex items-center gap-3 rounded-xl px-2.5 py-2">
                        <Avatar className="h-8 w-8 ring-2 ring-emerald-500/20">
                            <AvatarFallback className="bg-gradient-to-br from-emerald-500 to-teal-600 text-white text-xs font-bold">
                                {user?.name?.charAt(0)?.toUpperCase()}
                            </AvatarFallback>
                        </Avatar>
                        <div className="flex-1 min-w-0">
                            <p className="text-[13px] font-semibold leading-none truncate">{user?.name}</p>
                            <p className="text-[10px] text-muted-foreground mt-0.5">{t('Client')}</p>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main */}
            <div className="flex-1 flex flex-col min-w-0">
                <header className="h-14 shrink-0 flex items-center justify-between px-5 border-b bg-background/60 glass sticky top-0 z-20">
                    <span className="font-semibold text-[15px] tracking-tight">{t(pageTitle[location.pathname] || 'Portail Client')}</span>
                    <div className="flex items-center gap-1.5 h-8">
                        <LanguageSwitcher />
                        <Button variant="ghost" size="icon" onClick={toggleTheme} className="text-muted-foreground rounded-lg shrink-0">
                            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                        </Button>
                        <Button variant="ghost" size="icon" className="text-muted-foreground rounded-lg relative shrink-0">
                            <Bell className="h-4 w-4" />
                        </Button>
                        <div className="w-px h-5 bg-border mx-1 shrink-0" />
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <button className="flex items-center gap-2 rounded-lg px-1.5 h-8 hover:bg-accent transition-colors shrink-0">
                                    <Avatar className="h-7 w-7 ring-2 ring-emerald-500/20 shrink-0">
                                        <AvatarFallback className="bg-gradient-to-br from-emerald-500 to-teal-600 text-white text-[11px] font-bold">
                                            {user?.name?.charAt(0)?.toUpperCase()}
                                        </AvatarFallback>
                                    </Avatar>
                                    <span className="text-[13px] font-semibold hidden lg:inline leading-none">{user?.name}</span>
                                </button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-48">
                                <DropdownMenuItem onClick={() => navigate('/portal/profile')}><User className="mr-2 h-4 w-4" /> {t('Mon Profil')}</DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem onClick={logout} className="text-destructive focus:text-destructive"><LogOut className="mr-2 h-4 w-4" /> {t('Déconnexion')}</DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </div>
                </header>
                <main className="flex-1 overflow-auto p-5 lg:p-7"><div className="animate-fade-in"><Outlet /></div></main>
            </div>
            <ChatbotWidget />
            <ScrollToTop />
        </div>
    );
};
export default ClientLayout;
