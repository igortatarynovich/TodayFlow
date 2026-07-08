import enCatalog from "../../../CONTENT/i18n/app.en.json";
import ruCatalog from "../../../CONTENT/i18n/app.ru.json";

type Catalog = Record<string, string>;

const catalogs: Record<string, Catalog> = {
  en: enCatalog,
  ru: ruCatalog
};

const FALLBACK_LOCALE = "en";
const runtimeLocale = process.env.NEXT_PUBLIC_APP_LOCALE ?? FALLBACK_LOCALE;
let activeLocale = catalogs[runtimeLocale] ? runtimeLocale : FALLBACK_LOCALE;

const applyParams = (template: string, params?: Record<string, string | number>): string => {
  if (!params) {
    return template;
  }
  return Object.entries(params).reduce(
    (acc, [key, value]) => acc.replace(new RegExp(`\\{${key}\\}`, "g"), String(value)),
    template
  );
};

const LOCALE_STORAGE_KEY = "todayflow_locale";

export function getLocale(): string {
  return activeLocale;
}

/** Client: prefer persisted locale (LocaleSwitcher) before module default. */
export function resolveClientLocale(): string {
  if (typeof window !== "undefined") {
    const stored = window.localStorage.getItem(LOCALE_STORAGE_KEY);
    if (stored && catalogs[stored]) return stored;
  }
  return getLocale();
}

export function setLocale(nextLocale: string): void {
  activeLocale = catalogs[nextLocale] ? nextLocale : FALLBACK_LOCALE;
}

export function t(
  key: string,
  defaultValue?: string,
  params?: Record<string, string | number>,
  locale?: string
): string {
  const selectedLocale = locale ?? activeLocale;
  const catalog = catalogs[selectedLocale] ?? catalogs[FALLBACK_LOCALE];
  const fallbackCatalog = catalogs[FALLBACK_LOCALE];
  const template =
    catalog[key] ??
    (selectedLocale !== FALLBACK_LOCALE ? fallbackCatalog[key] : undefined) ??
    defaultValue ??
    key;
  return applyParams(template, params);
}
