import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

export type Language = 'en' | 'zh';
type Locale = { language: Language; setLanguage: (value: Language) => void; t: (en: string, zh: string) => string };
const Context = createContext<Locale | null>(null);
export function savedLanguage(key: string): Language {
  try { return localStorage.getItem(key) === 'zh' ? 'zh' : 'en'; } catch { return 'en'; }
}
export function saveLanguage(key: string, value: Language) {
  try { localStorage.setItem(key, value); } catch { /* Preferences are optional. Resume data is never stored. */ }
}
export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(() => savedLanguage('fr-interface-language'));
  useEffect(() => { saveLanguage('fr-interface-language', language); document.documentElement.lang = language === 'zh' ? 'zh-CN' : 'en'; }, [language]);
  return <Context.Provider value={{ language, setLanguage, t: (en, zh) => language === 'zh' ? zh : en }}>{children}</Context.Provider>;
}
export function useLanguage() {
  const value = useContext(Context);
  if (!value) throw new Error('LanguageProvider is missing.');
  return value;
}
export function LanguageSwitcher() {
  const { language, setLanguage, t } = useLanguage();
  return <label className="language-picker"><span>{t('Language', '界面语言')}</span><select aria-label={t('Interface language', '界面语言')} value={language} onChange={e => setLanguage(e.target.value as Language)}>
    <option value="en">English</option><option value="zh">简体中文</option>
  </select></label>;
}
