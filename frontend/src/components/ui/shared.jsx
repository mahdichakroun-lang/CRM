import * as React from 'react';
import * as SeparatorPrimitive from '@radix-ui/react-separator';
import { cn } from '../../lib/utils';

const Separator = React.forwardRef(({ className, orientation = 'horizontal', decorative = true, ...props }, ref) => (
    <SeparatorPrimitive.Root
        ref={ref}
        decorative={decorative}
        orientation={orientation}
        className={cn('shrink-0 bg-border', orientation === 'horizontal' ? 'h-[1px] w-full' : 'h-full w-[1px]', className)}
        {...props}
    />
));
Separator.displayName = 'Separator';

const Label = React.forwardRef(({ className, ...props }, ref) => (
    <label ref={ref} className={cn('text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70', className)} {...props} />
));
Label.displayName = 'Label';

const ScrollArea = React.forwardRef(({ className, children, ...props }, ref) => (
    <div ref={ref} className={cn('relative overflow-auto', className)} {...props}>{children}</div>
));
ScrollArea.displayName = 'ScrollArea';

/* ── Sheet (Drawer replacement) ── */
const Sheet = ({ open, onClose, children, title, className }) => {
    if (!open) return null;
    return (
        <>
            <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm" onClick={onClose} />
            <div className={cn(
                'fixed inset-y-0 right-0 z-50 w-full max-w-lg border-l bg-card shadow-2xl',
                'animate-slide-in-right overflow-auto',
                className
            )}>
                <div className="flex items-center justify-between p-5 border-b">
                    <h2 className="text-lg font-semibold">{title}</h2>
                    <button onClick={onClose} className="rounded-lg p-1.5 hover:bg-accent transition-colors">
                        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                </div>
                <div className="p-5">{children}</div>
            </div>
        </>
    );
};

/* ── Toast notification ── */
const toastState = { listeners: [], toasts: [] };

export const toast = {
    success: (msg) => toast._emit({ type: 'success', message: msg }),
    error: (msg) => toast._emit({ type: 'error', message: msg }),
    info: (msg) => toast._emit({ type: 'info', message: msg }),
    _emit: (t) => {
        const id = Date.now();
        const item = { ...t, id };
        toastState.toasts.push(item);
        toastState.listeners.forEach(fn => fn([...toastState.toasts]));
        setTimeout(() => {
            toastState.toasts = toastState.toasts.filter(x => x.id !== id);
            toastState.listeners.forEach(fn => fn([...toastState.toasts]));
        }, 3500);
    },
};

export function Toaster() {
    const [toasts, setToasts] = React.useState([]);

    React.useEffect(() => {
        toastState.listeners.push(setToasts);
        return () => { toastState.listeners = toastState.listeners.filter(fn => fn !== setToasts); };
    }, []);

    return (
        <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
            {toasts.map(t => (
                <div
                    key={t.id}
                    className={cn(
                        'animate-fade-in rounded-xl px-4 py-3 text-sm font-medium shadow-xl border backdrop-blur-md min-w-[280px] flex items-center gap-2',
                        t.type === 'success' && 'bg-emerald-50 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800',
                        t.type === 'error' && 'bg-red-50 dark:bg-red-950/80 text-red-700 dark:text-red-300 border-red-200 dark:border-red-800',
                        t.type === 'info' && 'bg-sky-50 dark:bg-sky-950/80 text-sky-700 dark:text-sky-300 border-sky-200 dark:border-sky-800',
                    )}
                >
                    <span>{t.type === 'success' ? '✓' : t.type === 'error' ? '✕' : 'ℹ'}</span>
                    {t.message}
                </div>
            ))}
        </div>
    );
}

/* ── Spinner ── */
const Spinner = ({ className, size = 'md' }) => {
    const sizes = { sm: 'h-4 w-4', md: 'h-6 w-6', lg: 'h-10 w-10' };
    return (
        <svg className={cn('animate-spin text-primary', sizes[size], className)} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
    );
};

/* ── Empty State ── */
const EmptyState = ({ icon, title = 'Aucune donnée', description }) => (
    <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
        {icon || (
            <svg className="h-12 w-12 mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
        )}
        <p className="text-sm font-medium">{title}</p>
        {description && <p className="text-xs mt-1">{description}</p>}
    </div>
);

export { Separator, Label, ScrollArea, Sheet, Spinner, EmptyState };
