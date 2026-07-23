"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useMemo } from "react";
import { LoadingSpinner } from "@/components/orbit";
import {
  ProductJourneyScene,
} from "@/components/product-ui/ProductJourneyScene";
import journeyStyles from "@/components/product-ui/ProductJourneyScene.module.css";
import { ProductWebShellConfigBridge, type ProductWebShellConfig } from "@/components/product-ui/productWebShellConfig";
import { productWebShellChromeBundle } from "@/components/product-ui/productWebShellChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";
import { useProductDayNightTheme } from "@/lib/useProductDayNightTheme";
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
  /** Living lead under the title — catalog description or day_story reason. */
  subtitle?: string;
  /** Soft why from Today `day_story.practice_recommendation.reason` when present. */
  dayWhy?: string | null;
  dayWhyLabel?: string;
  meta?: PracticeSessionMetaItem[];
  rail?: ReactNode;
  loading?: boolean;
  children?: ReactNode;
};

const SESSION_COPY = {
  ru: {
    leadTitle: "Практика",
    leadDefault: "Живой ход дня — шаги ниже, без лишнего шума.",
    stepsTitle: "Шаги",
    stepsLead: "Иди по порядку — или остановись на том, что нужно сейчас.",
    whyLabel: "Почему это важно сегодня",
  },
  en: {
    leadTitle: "Practice",
    leadDefault: "A living move for today — steps below, without noise.",
    stepsTitle: "Steps",
    stepsLead: "Walk in order — or pause where you need to.",
    whyLabel: "Why this matters today",
  },
} as const;

export function PracticeSessionWebScreen({
  displayName,
  profileMeta,
  coreProfile,
  locale,
  backHref = "/practices",
  backLabel,
  title,
  subtitle,
  dayWhy = null,
  dayWhyLabel,
  meta = [],
  rail,
  loading = false,
  children,
}: PracticeSessionWebScreenProps) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const copy = SESSION_COPY[resolvedLocale === "ru" ? "ru" : "en"];
  const shell = useMemo(() => productWebShellChromeBundle(resolvedLocale), [resolvedLocale]);
  const resolvedBackLabel = backLabel ?? shell.practicesBackLabel;
  const theme = useProductDayNightTheme();
  const whyLabel = dayWhyLabel ?? copy.whyLabel;
  const livingLead = (subtitle || copy.leadDefault).trim();

  const shellConfig = useMemo((): ProductWebShellConfig => {
    return {
      testId: "practice-session-web-screen",
      displayName,
      profileMeta,
      coreProfile,
      theme,
      mainWide: true,
      rail,
    };
  }, [coreProfile, displayName, profileMeta, rail, theme]);

  return (
    <>
      <ProductWebShellConfigBridge config={shellConfig} />
      <div className={s.practiceSessionRoot} data-testid="practice-session-journey">
        <Link href={backHref} className={s.practiceSessionBack}>
          ← {resolvedBackLabel}
        </Link>

        {loading ? (
          <div className={s.practiceSessionLoading}>
            <LoadingSpinner size="lg" />
          </div>
        ) : (
          <>
            <ProductJourneyScene
              step={1}
              title={copy.leadTitle}
              lead={livingLead}
              motif="effort"
              testId="practice-session-lead"
            >
              {title ? (
                <header className={s.practiceSessionHeader}>
                  <h1 className={s.practiceSessionTitle}>{title}</h1>
                </header>
              ) : null}

              {dayWhy ? (
                <p className={s.practiceSessionDayWhy} data-testid="practice-session-day-why">
                  <span className={journeyStyles.softWhyLabel}>{whyLabel}</span>
                  {dayWhy}
                </p>
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
            </ProductJourneyScene>

            <ProductJourneyScene
              step={2}
              title={copy.stepsTitle}
              lead={copy.stepsLead}
              motif="today"
              testId="practice-session-steps"
            >
              <div className={s.practiceSessionCard}>{children}</div>
            </ProductJourneyScene>
          </>
        )}
      </div>
    </>
  );
}
