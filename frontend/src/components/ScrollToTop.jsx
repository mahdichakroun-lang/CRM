import { useState, useEffect } from 'react';
import { ArrowUp } from 'lucide-react';

const ScrollToTop = () => {
    const [visible, setVisible] = useState(false);

    useEffect(() => {
        // Find the scrollable main content area
        const handleScroll = () => {
            const scrollY = window.scrollY || document.documentElement.scrollTop;
            setVisible(scrollY > 100);
        };
        window.addEventListener('scroll', handleScroll, true);
        // Also listen on the main element
        const main = document.querySelector('main');
        if (main) {
            const onMainScroll = () => setVisible(main.scrollTop > 100);
            main.addEventListener('scroll', onMainScroll);
            return () => {
                window.removeEventListener('scroll', handleScroll, true);
                main.removeEventListener('scroll', onMainScroll);
            };
        }
        return () => window.removeEventListener('scroll', handleScroll, true);
    }, []);

    const scrollToTop = () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        const main = document.querySelector('main');
        if (main) main.scrollTo({ top: 0, behavior: 'smooth' });
    };

    return (
        <button
            onClick={scrollToTop}
            aria-label="Scroll to top"
            className="fixed bottom-6 right-6 z-50 transition-all duration-300"
            style={{
                opacity: visible ? 1 : 0,
                pointerEvents: visible ? 'auto' : 'none',
                transform: visible ? 'translateY(0) scale(1)' : 'translateY(20px) scale(0.8)',
                width: 44,
                height: 44,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                boxShadow: '0 4px 20px rgba(99,102,241,0.4)',
                border: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                color: '#fff',
            }}
        >
            <ArrowUp className="h-5 w-5" />
        </button>
    );
};

export default ScrollToTop;
