import enCatalog from "../../../CONTENT/i18n/app.en.json";
import ruCatalog from "../../../CONTENT/i18n/app.ru.json";

type Catalog = Record<string, string>;

const catalogs: Record<string, Catalog> = {
  en: enCatalog,
  ru: ruCatalog
};

/** Product default is Russian; English remains available via LocaleSwitcher. */
const FALLBACK_LOCALE = "ru";
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

/** v2: reset stale EN prefs from earlier English-default builds. */
const LOCALE_STORAGE_KEY = "todayflow_locale_v2";

function readStoredLocale(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const stored = window.localStorage.getItem(LOCALE_STORAGE_KEY);
    if (stored && catalogs[stored]) return stored;
  } catch {
    // ignore storage errors
  }
  return null;
}

export function getLocale(): string {
  const stored = readStoredLocale();
  if (stored) return stored;
  return activeLocale;
}

/** Client: prefer persisted locale (LocaleSwitcher) before module default. */
export function resolveClientLocale(): string {
  return getLocale();
}

export function setLocale(nextLocale: string): void {
  activeLocale = catalogs[nextLocale] ? nextLocale : FALLBACK_LOCALE;
  if (typeof window !== "undefined") {
    try {
      window.localStorage.setItem(LOCALE_STORAGE_KEY, activeLocale);
    } catch {
      // ignore
    }
  }
}

export function t(
  key: string,
  defaultValue?: string,
  params?: Record<string, string | number>,
  locale?: string
): string {
  const selectedLocale = locale ?? getLocale();
  const catalog = catalogs[selectedLocale] ?? catalogs[FALLBACK_LOCALE];
  // Prefer RU catalog, then explicit defaultValue (often Russian inline copy), then EN, then key.
  const enCatalog = catalogs.en;
  const template =
    catalog[key] ??
    defaultValue ??
    (selectedLocale !== "en" ? enCatalog?.[key] : undefined) ??
    key;
  return applyParams(template, params);
}
