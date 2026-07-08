"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useMemo } from "react";
import { LoadingSpinner } from "@/components/orbit";
import { ProductWebShellConfigBridge, type ProductWebShellConfig } from "@/components/product-ui/productWebShellConfig";
import { productWebShellChromeBundle } from "@/components/product-ui/productWebShellChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";
import type { CoreProfile } from "@/lib/types";
import s from "@/components/product-ui/productWebScreens.module.css";

export type PracticeSessionMetaItem = {
  label: string;
  value: string;
  tone?: "default" | "success" | "accent";
};

export type PracticeSessionWebScreenProps = {
  displayName?: string | null;
  profileMeta?: string | null;
  coreProfile?: CoreProfile | null;
  locale?: FlowPracticesChromeLocale;
  backHref?: string;
  backLabel?: string;
  title?: string;
  subtitle?: string;
  meta?: PracticeSessionMetaItem[];
  rail?: ReactNode;
  loading?: boolean;
  children?: ReactNode;
};

export function PracticeSessionWebScreen({
  displayName,
  profileMeta,
  coreProfile,
  locale,
  backHref = "/practices",
  backLabel,
  title,
  subtitle,
  meta = [],
  rail,
  loading = false,
  children,
}: PracticeSessionWebScreenProps) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const shell = useMemo(() => productWebShellChromeBundle(resolvedLocale), [resolvedLocale]);
  const resolvedBackLabel = backLabel ?? shell.practicesBackLabel;

  const shellConfig = useMemo((): ProductWebShellConfig => {
    return {
      testId: "practice-session-web-screen",
      displayName,
      profileMeta,
      coreProfile,
      rail,
    };
  }, [coreProfile, displayName, profileMeta, rail]);

  return (
    <>
      <ProductWebShellConfigBridge config={shellConfig} />
      <div className={s.practiceSessionRoot}>
        <Link href={backHref} className={s.practiceSessionBack}>
          ← {resolvedBackLabel}
        </Link>

        {loading ? (
          <div className={s.practiceSessionLoading}>
            <LoadingSpinner size="lg" />
          </div>
        ) : (
          <>
            {title ? (
              <header className={s.practiceSessionHeader}>
                <h1 className={s.practiceSessionTitle}>{title}</h1>
                {subtitle ? <p className={s.practiceSessionSubtitle}>{subtitle}</p> : null}
              </header>
            ) : null}

            {meta.length > 0 ? (
              <div className={s.practiceSessionMetaRow}>
                {meta.map((item) => (
                  <div key={item.label} className={s.practiceSessionMetaItem}>
                    <p className={s.practiceSessionMetaLabel}>{item.label}</p>
                    <p
                      className={`${s.practiceSessionMetaValue} ${
                        item.tone === "success"
                          ? s.practiceSessionMetaSuccess
                          : item.tone === "accent"
                            ? s.practiceSessionMetaAccent
                            : ""
                      }`}
                    >
                      {item.value}
                    </p>
                  </div>
                ))}
              </div>
            ) : null}

            {children}
          </>
        )}
      </div>
    </>
  );
}
