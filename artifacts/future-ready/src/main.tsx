import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import '@fontsource-variable/manrope';
import './styles.css';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WelcomeGate } from './components/welcome/WelcomeGate';
import { LanguageProvider } from './i18n';

const queryClient = new QueryClient({ defaultOptions: { queries: { refetchOnWindowFocus: false } } });

createRoot(document.getElementById('root')!).render(<StrictMode><QueryClientProvider client={queryClient}><LanguageProvider><WelcomeGate /></LanguageProvider></QueryClientProvider></StrictMode>);
