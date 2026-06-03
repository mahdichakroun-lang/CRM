import { useState, useRef, useEffect } from 'react';
import { Outlet, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { cn } from '../lib/utils';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Button } from './ui/button';
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from './ui/dropdown-menu';
import { Spinner } from './ui/shared';
import {
    LayoutDashboard, Building2, Users, Target, Briefcase, FileText,
    Headphones, CalendarDays, ScrollText, PanelLeftClose, PanelLeftOpen,
    Sun, Moon, LogOut, User, ChevronRight, Search, Bell, Shield,
    ChevronsUpDown, Brain,
} from 'lucide-react';
import ScrollToTop from './ScrollToTop';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from './LanguageSwitcher';

const menuGroups = [
    {
        items: [{ key: '/', icon: LayoutDashboard, label: 'Tableau de Bord' }],
    },
    {
        label: 'Commercial',
        items: [
            { key: '/leads', icon: Target, label: 'Leads' },
            { key: '/accounts', icon: Building2, label: 'Comptes' },
            { key: '/contacts', icon: Users, label: 'Contacts' },
            { key: '/deals', icon: Briefcase, label: 'Deals' },
            { key: '/quotes', icon: FileText, label: 'Devis' },
        ],
    },
    {
        label: 'Support',
        items: [{ key: '/tickets', icon: Headphones, label: 'Tickets' }],
    },
    {
        label: 'Intelligence',
        items: [
            { key: '/lead-scoring', icon: Brain, label: 'Lead Scoring IA' },
        ],
    },
    {
        label: 'Suivi',
        items: [
            { key: '/activities', icon: CalendarDays, label: 'Activités' },
        ],
    },
    {
        label: 'Administration',
        roles: ['admin', 'manager'],
        items: [
            { key: '/users', icon: Shield, label: 'Utilisateurs' },
        ]
    }
];

const pageTitle = {
    '/': 'Tableau de Bord', '/accounts': 'Comptes', '/contacts': 'Contacts',
    '/leads': 'Leads', '/deals': 'Deals', '/quotes': 'Devis',
    '/tickets': 'Tickets', '/activities': 'Activités', '/audit': 'Journal d\'Audit',
    '/profile': 'Mon Profil', '/users': 'Utilisateurs', '/lead-scoring': 'Lead Scoring IA'
};

/* ── Sidebar Nav Item ── */
const NavItem = ({ item, active, collapsed, onClick, t }) => {
    const Icon = item.icon;
    return (
        <button
            onClick={onClick}
            data-active={active}
            className={cn(
                'sidebar-item w-full flex items-center gap-3 rounded-lg text-[13px] font-medium group',
                collapsed ? 'justify-center h-10 mx-auto' : 'px-3 h-9',
                active
                    ? 'bg-primary/10 text-primary font-semibold'
                    : 'text-sidebar-muted hover:bg-accent hover:text-foreground'
            )}
        >
            <Icon className={cn(
                'shrink-0 transition-colors duration-150',
                active ? 'text-primary' : 'text-sidebar-muted/80 group-hover:text-foreground',
                collapsed ? 'w-5 h-5' : 'w-4 h-4'
            )} />
            {!collapsed && <span className="truncate">{t(item.label)}</span>}
        </button>
    );
};

const AppLayout = () => {
    const { user, loading, logout } = useAuth();
    const { isDark, toggleTheme } = useTheme();
    const [collapsed, setCollapsed] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchOpen, setSearchOpen] = useState(false);
    const searchRef = useRef(null);
    const navigate = useNavigate();
    const location = useLocation();
    const { t } = useTranslation();

    const searchItems = [
        { label: t('Tableau de Bord'), path: '/', icon: LayoutDashboard },
        { label: t('Leads'), path: '/leads', icon: Target },
        { label: t('Comptes'), path: '/accounts', icon: Building2 },
        { label: t('Contacts'), path: '/contacts', icon: Users },
        { label: t('Deals'), path: '/deals', icon: Briefcase },
        { label: t('Devis'), path: '/quotes', icon: FileText },
        { label: t('Tickets'), path: '/tickets', icon: Headphones },
        { label: t('Activités'), path: '/activities', icon: CalendarDays },
        { label: t('Audit'), path: '/audit', icon: ScrollText },
        { label: t('Mon Profil'), path: '/profile', icon: User },
        { label: t('Utilisateurs'), path: '/users', icon: Shield },
        { label: t('Lead Scoring IA'), path: '/lead-scoring', icon: Brain },
    ];

    const filteredSearch = searchQuery.trim()
        ? searchItems.filter(item => item.label.toLowerCase().includes(searchQuery.toLowerCase()))
        : [];

    useEffect(() => {
        const handleKeyDown = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                searchRef.current?.focus();
                setSearchOpen(true);
            }
            if (e.key === 'Escape') { setSearchOpen(false); setSearchQuery(''); }
        };
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, []);

    if (loading) {
        return (
            <div className="h-screen flex items-center justify-center bg-background">
                <Spinner size="lg" />
            </div>
        );
    }

    if (!user) return <Navigate to="/login" replace />;
    if (user.role === 'client') return <Navigate to="/portal" replace />;

    return (
        <div className="h-screen flex overflow-hidden bg-background">
            {/* ─── Sidebar ─── */}
            <aside className={cn(
                'h-full flex flex-col bg-sidebar border-r border-sidebar-border transition-all duration-300 shrink-0 z-30',
                collapsed ? 'w-[68px]' : 'w-[256px]'
            )}>
                {/* Logo Block */}
                <div className={cn(
                    'h-[60px] flex items-center shrink-0 border-b border-sidebar-border',
                    collapsed ? 'justify-center px-2' : 'px-4 gap-3'
                )}>
                    <div className="w-9 h-9 rounded-lg overflow-hidden flex items-center justify-center shrink-0 ring-1 ring-border/50 shadow-sm">
                        <img src="/FRS_logo.jpg" alt="FRS Logo" className="object-contain w-full h-full" />
                    </div>
                    {!collapsed && (
                        <div className="flex flex-col min-w-0">
                            <span className="font-bold text-sm tracking-tight leading-none truncate">CRM Internal</span>
                            <span className="text-[10px] text-muted-foreground/60 mt-0.5 font-medium">Enterprise Suite</span>
                        </div>
                    )}
                </div>

                {/* Navigation */}
                <nav className="flex-1 overflow-y-auto py-3 px-2.5 space-y-0.5">
                    {menuGroups
                        .filter(group => !group.roles || group.roles.includes(user?.role))
                        .map((group, gi) => (
                            <div key={gi} className={gi > 0 ? 'pt-4' : ''}>
                                {group.label && !collapsed && (
                                    <p className="sidebar-group-label">{t(group.label)}</p>
                                )}
                                {group.label && collapsed && (
                                    <div className="mx-3 my-2.5 h-px bg-border/60" />
                                )}
                                <div className="space-y-0.5">
                                    {group.items.map(item => (
                                        <NavItem
                                            key={item.key}
                                            item={item}
                                            active={location.pathname === item.key}
                                            collapsed={collapsed}
                                            onClick={() => navigate(item.key)}
                                            t={t}
                                        />
                                    ))}
                                    {/* Audit - admin/manager only */}
                                    {group.label === 'Suivi' && (user?.role === 'admin' || user?.role === 'manager') && (
                                        <NavItem
                                            item={{ key: '/audit', icon: ScrollText, label: 'Audit' }}
                                            active={location.pathname === '/audit'}
                                            collapsed={collapsed}
                                            onClick={() => navigate('/audit')}
                                            t={t}
                                        />
                                    )}
                                </div>
                            </div>
                        ))}
                </nav>

                {/* Bottom User Block */}
                {!collapsed && (
                    <div className="p-3 border-t border-sidebar-border">
                        <button
                            onClick={() => navigate('/profile')}
                            className="w-full flex items-center gap-2.5 rounded-lg px-2.5 py-2 hover:bg-accent transition-colors group"
                        >
                            <Avatar className="h-8 w-8 ring-2 ring-primary/10 shrink-0">
                                <AvatarFallback className="bg-gradient-to-br from-primary/90 to-violet-600 text-white text-xs font-bold">
                                    {user?.name?.charAt(0)?.toUpperCase()}
                                </AvatarFallback>
                            </Avatar>
                            <div className="flex-1 text-left min-w-0">
                                <p className="text-[13px] font-semibold leading-none truncate">{user?.name}</p>
                                <p className="text-[11px] text-muted-foreground/60 capitalize mt-0.5 font-medium">{t(user?.role)}</p>
                            </div>
                            <ChevronsUpDown className="h-3.5 w-3.5 text-muted-foreground/40 group-hover:text-muted-foreground transition-colors shrink-0" />
                        </button>
                    </div>
                )}
                {collapsed && (
                    <div className="p-2 border-t border-sidebar-border flex justify-center">
                        <button onClick={() => navigate('/profile')} className="rounded-lg p-1.5 hover:bg-accent transition-colors">
                            <Avatar className="h-8 w-8 ring-2 ring-primary/10">
                                <AvatarFallback className="bg-gradient-to-br from-primary/90 to-violet-600 text-white text-xs font-bold">
                                    {user?.name?.charAt(0)?.toUpperCase()}
                                </AvatarFallback>
                            </Avatar>
                        </button>
                    </div>
                )}
            </aside>

            {/* ─── Main Content ─── */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Header */}
                <header className="h-[60px] shrink-0 flex items-center justify-between px-4 lg:px-6 border-b bg-background/80 glass sticky top-0 z-20">
                    <div className="flex items-center gap-2.5">
                        <Button variant="ghost" size="icon" onClick={() => setCollapsed(!collapsed)} className="text-muted-foreground h-8 w-8 rounded-lg hover:bg-accent">
                            {collapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
                        </Button>
                        <div className="h-5 w-px bg-border hidden sm:block" />
                        <h2 className="font-semibold text-sm tracking-tight hidden sm:block">
                            {t(pageTitle[location.pathname] || 'CRM')}
                        </h2>
                    </div>

                    <div className="flex items-center gap-1 h-8">
                        {/* Search */}
                        <div className="hidden md:flex items-center gap-2 bg-muted/60 rounded-lg px-3 h-8 text-sm text-muted-foreground border border-transparent focus-within:border-primary/20 focus-within:bg-background focus-within:shadow-sm transition-all w-52 relative shrink-0">
                            <Search className="h-3.5 w-3.5 shrink-0 opacity-50" />
                            <input
                                ref={searchRef}
                                type="text"
                                placeholder={t('Rechercher...')}
                                value={searchQuery}
                                onChange={(e) => { setSearchQuery(e.target.value); setSearchOpen(true); }}
                                onFocus={() => setSearchOpen(true)}
                                onBlur={() => setTimeout(() => setSearchOpen(false), 200)}
                                className="bg-transparent outline-none text-foreground text-[13px] w-full placeholder:text-muted-foreground/50"
                            />
                            <kbd className="text-[10px] font-mono bg-background/80 px-1.5 py-0.5 rounded border text-muted-foreground/40 shrink-0">⌘K</kbd>
                            {searchOpen && filteredSearch.length > 0 && (
                                <div className="absolute top-full left-0 right-0 mt-1.5 bg-popover border rounded-lg shadow-lg overflow-hidden z-50 animate-scale-in">
                                    {filteredSearch.map((item) => {
                                        const SIcon = item.icon;
                                        return (
                                            <button
                                                key={item.path}
                                                onMouseDown={(e) => { e.preventDefault(); navigate(item.path); setSearchQuery(''); setSearchOpen(false); }}
                                                className="flex items-center gap-2.5 w-full px-3 py-2 text-left text-[13px] hover:bg-accent transition-colors"
                                            >
                                                <SIcon className="h-4 w-4 text-muted-foreground/60" />
                                                <span className="font-medium">{item.label}</span>
                                            </button>
                                        );
                                    })}
                                </div>
                            )}
                            {searchOpen && searchQuery.trim() && filteredSearch.length === 0 && (
                                <div className="absolute top-full left-0 right-0 mt-1.5 bg-popover border rounded-lg shadow-lg overflow-hidden z-50 p-3 text-center text-[13px] text-muted-foreground">
                                    {t('Aucun résultat')}
                                </div>
                            )}
                        </div>

                        <LanguageSwitcher />

                        <Button variant="ghost" size="icon" onClick={toggleTheme} className="text-muted-foreground rounded-lg shrink-0 h-8 w-8 hover:bg-accent">
                            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                        </Button>

                        {/* Notifications */}
                        <Button variant="ghost" size="icon" className="text-muted-foreground rounded-lg relative shrink-0 h-8 w-8 hover:bg-accent">
                            <Bell className="h-4 w-4" />
                            <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 rounded-full text-[9px] text-white flex items-center justify-center font-bold ring-2 ring-background">3</span>
                        </Button>

                        <div className="w-px h-5 bg-border mx-1 shrink-0" />

                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <button className="flex items-center gap-2 rounded-lg px-1.5 h-8 hover:bg-accent transition-colors shrink-0">
                                    <Avatar className="h-7 w-7 ring-2 ring-primary/10 shrink-0">
                                        <AvatarFallback className="bg-gradient-to-br from-primary/90 to-violet-600 text-white text-[11px] font-bold">
                                            {user?.name?.charAt(0)?.toUpperCase()}
                                        </AvatarFallback>
                                    </Avatar>
                                    <span className="text-[13px] font-medium hidden lg:inline leading-none">{user?.name}</span>
                                </button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-48">
                                <DropdownMenuItem onClick={() => navigate('/profile')}>
                                    <User className="mr-2 h-4 w-4" /> {t('Mon Profil')}
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem onClick={logout} className="text-destructive focus:text-destructive">
                                    <LogOut className="mr-2 h-4 w-4" /> {t('Déconnexion')}
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </div>
                </header>

                {/* Page content */}
                <main className="flex-1 overflow-auto p-4 lg:p-6">
                    <div className="animate-fade-in max-w-[1440px] mx-auto">
                        <Outlet />
                    </div>
                </main>
            </div>
            <ScrollToTop />
        </div>
    );
};

export default AppLayout;
