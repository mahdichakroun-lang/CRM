import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from './ui/dialog';
import { Button } from './ui/button';
import { AlertTriangle } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const ConfirmDialog = ({ open, onClose, onConfirm, title, description, confirmLabel, variant = 'destructive' }) => {
    const { t } = useTranslation();
    return (
        <Dialog open={open} onOpenChange={(o) => { if (!o) onClose(); }}>
            <DialogContent className="sm:max-w-[420px]">
                <DialogHeader>
                    <div className="mx-auto w-14 h-14 rounded-full bg-red-500/10 flex items-center justify-center mb-2">
                        <AlertTriangle className="h-7 w-7 text-red-500" />
                    </div>
                    <DialogTitle className="text-center text-lg">
                        {title || t('Confirmer la suppression')}
                    </DialogTitle>
                    <DialogDescription className="text-center text-sm text-muted-foreground">
                        {description || t('Cette action est irréversible. Voulez-vous vraiment continuer ?')}
                    </DialogDescription>
                </DialogHeader>
                <DialogFooter className="flex gap-3 sm:justify-center pt-2">
                    <Button variant="outline" onClick={onClose} className="min-w-[100px]">
                        {t('Annuler')}
                    </Button>
                    <Button
                        onClick={() => { onConfirm(); onClose(); }}
                        className="min-w-[100px] bg-red-500 hover:bg-red-600 text-white"
                    >
                        {confirmLabel || t('Supprimer')}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
};

export default ConfirmDialog;
