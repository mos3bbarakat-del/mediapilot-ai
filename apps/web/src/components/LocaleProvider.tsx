"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

type LocaleContextValue = {
  lang: "ar" | "en";
  toggle: () => void;
  t: (ar: string, en: string) => string;
};

const LocaleContext = createContext<LocaleContextValue | null>(null);

export function LocaleProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<"ar" | "en">("ar");

  useEffect(() => {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    document.body.classList.toggle("en", lang === "en");
  }, [lang]);

  const value = useMemo<LocaleContextValue>(() => ({
    lang,
    toggle: () => setLang((current) => current === "ar" ? "en" : "ar"),
    t: (ar, en) => lang === "ar" ? ar : en,
  }), [lang]);

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useLocale() {
  const value = useContext(LocaleContext);
  if (!value) throw new Error("useLocale must be used inside LocaleProvider");
  return value;
}
