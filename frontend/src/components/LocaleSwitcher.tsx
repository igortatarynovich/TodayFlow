"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { getJson, putJson, postJson } from "@/lib/api";
import { getLocale, setLocale } from "@/lib/i18n";
import { publishCoreProfileUpdate } from "@/lib/coreProfileCacheStorage";
import type { CoreProfile, UserSettings } from "@/lib/types";

const LOCALE_STORAGE_KEY = "todayflow_locale_v2";
const SUPPORTED_LOCALES = [
  { value: "ru", label: "RU" },
  { value: "en", label: "EN" },
];

async function syncLocaleToAccount(next: string): Promise<void> {
  try {
    await putJson<UserSettings>("/account/profile", { locale: next });
  } catch {
    /* guest / offline */
  }
}

async function refreshPortraitForLocale(): Promise<void> {
  try {
    const profile = await postJson<CoreProfile>("/account/core-profile/refresh", {});
    if (profile) publishCoreProfileUpdate(profile);
  } catch {
    /* refresh is best-effort; UI filters still hide wrong-language copy */
  }
}

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
      void (async () => {
        try {
          const settings = await getJson<UserSettings>("/account/profile");
          if (settings && settings.locale !== stored) {
            await syncLocaleToAccount(stored);
            if (stored === "ru" && String(settings.locale || "").toLowerCase().startsWith("en")) {
              await refreshPortraitForLocale();
            }
          }
        } catch {
          /* not authenticated */
        }
      })();
      return;
    }
    // Product default: Russian (do not auto-pick browser English).
    const fallback = "ru";
    setLocale(fallback);
    setLocaleState(fallback);
    window.localStorage.setItem(LOCALE_STORAGE_KEY, fallback);
    void syncLocaleToAccount(fallback);
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
    void (async () => {
      await syncLocaleToAccount(next);
      await refreshPortraitForLocale();
      router.refresh();
    })();
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
