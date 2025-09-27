import React, { createContext, useContext, useState, ReactNode } from 'react';

export type Tenant = {
  id: number;
  name: string;
};

export type User = {
  id: number;
  name: string;
  role: string;
};

export type Theme = 'light' | 'dark';

export type AppContextType = {
  tenant: Tenant | null;
  setTenant: (tenant: Tenant | null) => void;
  user: User | null;
  setUser: (user: User | null) => void;
  theme: Theme;
  setTheme: (theme: Theme) => void;
  i18nLang: string;
  setI18nLang: (lang: string) => void;
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useAppContext must be used within AppProvider');
  return context;
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [theme, setTheme] = useState<Theme>('light');
  const [i18nLang, setI18nLang] = useState<string>('en');

  return (
    <AppContext.Provider value={{ tenant, setTenant, user, setUser, theme, setTheme, i18nLang, setI18nLang }}>
      {children}
    </AppContext.Provider>
  );
}
