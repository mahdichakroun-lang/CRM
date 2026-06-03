import { useTranslation } from 'react-i18next';
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from './ui/dropdown-menu';
import { Button } from './ui/button';

const LanguageSwitcher = () => {
    const { i18n } = useTranslation();

    const changeLanguage = (lng) => {
        i18n.changeLanguage(lng);
    };

    const currentLang = i18n.resolvedLanguage || 'fr';

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8 rounded-lg flex items-center justify-center">
                    {currentLang.startsWith('en')
                        ? <img src="https://flagcdn.com/w40/gb.png" alt="English" className="w-5 h-auto rounded-sm shadow-sm" />
                        : <img src="https://flagcdn.com/w40/fr.png" alt="Français" className="w-5 h-auto rounded-sm shadow-sm" />}
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-36">
                <DropdownMenuItem onClick={() => changeLanguage('fr')} className="flex items-center gap-2 cursor-pointer">
                    <img src="https://flagcdn.com/w40/fr.png" alt="Français" className="w-5 h-auto rounded-sm shadow-sm" />
                    <span className="font-medium text-sm">Français</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => changeLanguage('en')} className="flex items-center gap-2 cursor-pointer">
                    <img src="https://flagcdn.com/w40/gb.png" alt="English" className="w-5 h-auto rounded-sm shadow-sm" />
                    <span className="font-medium text-sm">English</span>
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
};

export default LanguageSwitcher;
