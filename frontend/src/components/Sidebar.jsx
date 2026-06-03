import { NavLink } from 'react-router-dom';
import {
    History, Users, Building2, Target, Briefcase,
    FileText, Ticket, BarChart3, LogOut, LayoutDashboard
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
    const { user, logout } = useAuth();

    const menuItems = [
        { name: 'Dashboard', icon: LayoutDashboard, path: '/' },
        { name: 'Accounts', icon: Building2, path: '/accounts' },
        { name: 'Contacts', icon: Users, path: '/contacts' },
        { name: 'Leads', icon: Target, path: '/leads' },
        { name: 'Deals', icon: Briefcase, path: '/deals' },
        { name: 'Quotes', icon: FileText, path: '/quotes' },
        { name: 'Tickets', icon: Ticket, path: '/tickets' },
        { name: 'Audit Logs', icon: History, path: '/audit', role: 'admin' },
    ];

    return (
        <div className="w-64 h-screen glass border-r border-white/10 flex flex-col fixed left-0 top-0">
            <div className="p-6 flex items-center space-x-3 border-b border-white/10">
                <div className="w-10 h-10 bg-indigo-500 rounded-lg flex items-center justify-center font-bold text-xl">
                    C
                </div>
                <span className="font-bold text-xl tracking-tight">CRM INTERNAL</span>
            </div>

            <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
                {menuItems.map((item) => (
                    (!item.role || (user && user.role === item.role)) && (
                        <NavLink
                            key={item.name}
                            to={item.path}
                            className={({ isActive }) =>
                                `flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${isActive
                                    ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 shadow-[0_0_15px_rgba(99,102,241,0.2)]'
                                    : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
                                }`
                            }
                        >
                            <item.icon size={20} />
                            <span className="font-medium">{item.name}</span>
                        </NavLink>
                    )
                ))}
            </div>

            <div className="p-4 border-t border-white/10 bg-white/5">
                <div className="flex items-center space-x-3 mb-4 px-2">
                    <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold uppercase transition-transform hover:scale-110">
                        {user?.name?.charAt(0) || 'U'}
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold truncate">{user?.name || 'User'}</p>
                        <p className="text-xs text-slate-500 truncate capitalize">{user?.role || 'Role'}</p>
                    </div>
                </div>
                <button
                    onClick={logout}
                    className="w-full flex items-center space-x-3 px-4 py-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                >
                    <LogOut size={18} />
                    <span className="text-sm font-medium">Logout</span>
                </button>
            </div>
        </div>
    );
};

export default Sidebar;
