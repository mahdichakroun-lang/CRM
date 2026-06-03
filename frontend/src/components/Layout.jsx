import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Sidebar from './Sidebar';

const Layout = () => {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="h-screen w-screen flex items-center justify-center bg-slate-950">
                <div className="relative">
                    <div className="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin"></div>
                    <div className="mt-4 text-indigo-400 font-medium animate-pulse text-center">Loading...</div>
                </div>
            </div>
        );
    }

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    return (
        <div className="flex bg-slate-950 min-h-screen text-slate-200">
            <Sidebar />
            <main className="ml-64 flex-1 p-8">
                <Outlet />
            </main>
        </div>
    );
};

export default Layout;
