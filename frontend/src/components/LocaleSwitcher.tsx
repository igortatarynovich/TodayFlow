"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { getLocale, setLocale } from "@/lib/i18n";

const LOCALE_STORAGE_KEY = "todayflow_locale_v2";
const SUPPORTED_LOCALES = [
  { value: "ru", label: "RU" },
  { value: "en", label: "EN" },
];

export default function LocaleSwitcher() {
  const router = useRouter();
  const [locale, setLocaleState] = useState(getLocale());
  const initializedRef = useRef(false);

  useEffect(() => {
    if (initializedRef.current) {
      return;
    }
    initializedRef.current = true;
    if (typeof window === "undefined") {
      return;
    }
    const stored = window.localStorage.getItem(LOCALE_STORAGE_KEY);
    if (stored === "ru" || stored === "en") {
      if (stored !== locale) {
        setLocale(stored);
        setLocaleState(stored);
        router.refresh();
      }
      return;
    }
    // Product default: Russian (do not auto-pick browser English).
    const fallback = "ru";
    setLocale(fallback);
    setLocaleState(fallback);
    window.localStorage.setItem(LOCALE_STORAGE_KEY, fallback);
    if (fallback !== locale) {
      router.refresh();
    }
  }, [locale, router]);

  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const next = event.target.value;
    setLocale(next);
    setLocaleState(next);
    if (typeof window !== "undefined") {
      window.localStorage.setItem(LOCALE_STORAGE_KEY, next);
    }
    router.refresh();
  };

  return (
    <label style={{ display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.85rem" }}>
      <select value={locale} onChange={handleChange} style={{ padding: "0.2rem 0.4rem", borderRadius: 6 }}>
        {SUPPORTED_LOCALES.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}
