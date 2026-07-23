"use client";

import Link from "next/link";
import { Suspense, useEffect, useMemo, useState } from "react";
import { postJson } from "@/lib/api";
import { getLocale } from "@/lib/i18n";
import { useAuth } from "@/lib/useAuth";
import { COMPATIBILITY_GENERATION_TEMPLATE } from "@/lib/compatibilityDynamicsMode";
import {
  buildCompatibilityCheckKey,
  canGuestAccessCompatibility,
  tryConsumeGuestCompatibility,
} from "@/lib/guestAccessStore";
import {
  compatPersonLimitations,
  patchGuestCompatPair,
  readGuestCompatPair,
} from "@/lib/guestCompatPair";
import { prepareGuestClaimBeforeAuth } from "@/lib/claimGuestProfile";
import { GuestAccessLimitGate } from "@/components/guest/GuestAccessLimitGate";
import { GUEST_ACCESS_COPY } from "@/components/guest/guestAccessCopy";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { CompatibilityDynamicsSurface, type SignCompatProductSurface } from "@/components/compatibility/CompatibilityDynamicsSurface";
import { CompatibilityFunnelSection, type CompatibilityFunnelArtifact } from "@/components/compatibility/CompatibilityFunnelSection";
import { VALUE_FIRST_PATHS } from "@/lib/guestProfileDraft";

type QuickReading = {
  headline?: string;
  strongest?: string;
  friction?: string;
  next_step?: string;
  strengths?: string[];
  cautions?: string[];
} | null;

type CompatibilityDynamicsApiResponse = {
  score: number;
  summary: string;
  quick_reading?: QuickReading;
  is_paid?: boolean;
  free_paragraphs: string[];
  full_paragraphs: string[];
  product_surface: SignCompatProductSurface;
  funnel_artifact?: CompatibilityFunnelArtifact | null;
  personalized?: {
    headline?: string;
    hint?: string;
    do_focus?: string;
    avoid_focus?: string;
  } | null;
};

type CompatibilityBirthdatesResult = {
  label1: string;
  label2: string;
  date1: string;
  date2: string;
  location1: string;
  location2: string;
  relationship_context?: string;
  score: number;
  summary: string;
  quick_reading?: QuickReading;
  product_surface: SignCompatProductSurface;
  detail_paragraphs: string[];
  is_paid: boolean;
  funnel_artifact?: CompatibilityFunnelArtifact | null;
};

function formatDate(isoDate: string) {
  const tag = getLocale() === "ru" ? "ru-RU" : "en-US";
  return new Date(isoDate).toLocaleDateString(tag, {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function CompatibilityBirthdatesResultContent() {
  const { isAuthenticated } = useAuth();
  const pair = useMemo(() => readGuestCompatPair(), []);
  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<CompatibilityBirthdatesResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const date1 = pair?.person_a.birth_date || "";
  const date2 = pair?.person_b.birth_date || "";
  const label1 = pair?.person_a.label || "Первый человек";
  const label2 = pair?.person_b.label || "Второй человек";
  const location1 = pair?.person_a.location_name || "";
  const location2 = pair?.person_b.location_name || "";
  const relationshipContext = pair?.relationship_context || "";

  const compatCheckKey = buildCompatibilityCheckKey({
    mode: "precise",
    birth_date_1: date1,
    birth_date_2: date2,
    relationship_context: relationshipContext || undefined,
  });

  const limitations = useMemo(() => {
    if (!pair) return [] as string[];
    const a = compatPersonLimitations(pair.person_a);
    const b = compatPersonLimitations(pair.person_b);
    return Array.from(new Set([...a, ...b]));
  }, [pair]);

  useEffect(() => {
    if (!pair || !date1 || !date2) {
      setError("Нет сохранённых черновиков пары — вернись к форме.");
      setLoading(false);
      return;
    }

    if (!isAuthenticated && !canGuestAccessCompatibility(compatCheckKey)) {
      setLoading(false);
      return;
    }

    const loadCompatibility = async () => {
      try {
        // Guest preview: gated — no deep personalized advice layer.
        const response = await postJson<CompatibilityDynamicsApiResponse>("/compatibility/dynamics", {
          mode: "precise",
          birth_date_1: date1,
          birth_date_2: date2,
          relationship_context: relationshipContext || undefined,
          generation: COMPATIBILITY_GENERATION_TEMPLATE,
          include_personalized: false,
          locale: getLocale(),
          name_1: label1,
          name_2: label2,
        });

        const detailParagraphs = Array.isArray(response?.free_paragraphs)
          ? response.free_paragraphs.filter(Boolean)
          : [];

        setResult({
          label1,
          label2,
          date1,
          date2,
          location1,
          location2,
          relationship_context: relationshipContext || undefined,
          score: response?.score ?? 0,
          summary: response?.summary || "Совместимость рассчитана.",
          quick_reading: response?.quick_reading || null,
          product_surface: response.product_surface,
          detail_paragraphs: detailParagraphs,
          is_paid: Boolean(response?.is_paid),
          funnel_artifact: response.funnel_artifact ?? null,
        });

        patchGuestCompatPair({ preview_seen_at: new Date().toISOString() });

        if (!isAuthenticated) {
          tryConsumeGuestCompatibility(compatCheckKey);
        }
      } catch (err) {
        console.error("Failed to load compatibility", err);
        setError("Не удалось открыть результат совместимости.");
      } finally {
        setLoading(false);
      }
    };

    void loadCompatibility();
  }, [
    pair,
    date1,
    date2,
    label1,
    label2,
    location1,
    location2,
    relationshipContext,
    isAuthenticated,
    compatCheckKey,
  ]);

  const onSaveClick = async () => {
    patchGuestCompatPair({ save_ready_at: new Date().toISOString() });
    try {
      await prepareGuestClaimBeforeAuth();
    } catch {
      /* best-effort */
    }
  };

  if (loading) {
    return (
      <ProductPageScreen
        testId="compat-birthdates-result-page"
        title="Совместимость"
        loading
        loadingLabel="Загрузка…"
      />
    );
  }

  if (!isAuthenticated && !canGuestAccessCompatibility(compatCheckKey) && !result) {
    return (
      <ProductPageScreen
        testId="compat-birthdates-result-page"
        title="Совместимость"
        hideHeader
        mainWide
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
        <section className="tf-shell" style={{ paddingTop: "2rem", paddingBottom: "4.5rem" }}>
          <GuestAccessLimitGate
            title={GUEST_ACCESS_COPY.compatLimitTitle}
            body={GUEST_ACCESS_COPY.compatLimitBody}
            secondaryHref="/compatibility/birthdates"
            secondaryLabel="← К форме"
            testId="guest-compat-birthdates-result-limit"
          />
        </section>
      </ProductPageScreen>
    );
  }

  if (error || !result) {
    return (
      <ProductPageScreen
        testId="compat-birthdates-result-page"
        title="Совместимость"
        hideHeader
        mainWide
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
        <section className="tf-shell" style={{ paddingTop: "2rem", paddingBottom: "3rem" }}>
          <div className="compat-desktop-card">
            <h1 className="orbit-display-sm" style={{ margin: 0 }}>
              Не удалось загрузить
            </h1>
            <p className="orbit-body compat-desktop-muted" style={{ margin: "0.65rem 0 0" }}>
              {error || "Вернись к форме и заполни две даты."}
            </p>
            <Link
              href="/compatibility/birthdates"
              className="orbit-button orbit-button-primary"
              style={{ textDecoration: "none", marginTop: "1rem", display: "inline-flex" }}
            >
              К форме
            </Link>
          </div>
        </section>
      </ProductPageScreen>
    );
  }

  const quickReading = result.quick_reading || null;

  return (
    <ProductPageScreen
      testId="compat-birthdates-result-page"
      title={`${result.label1} × ${result.label2}`}
      hideHeader
      mainWide
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <section className="tf-shell" style={{ paddingTop: "2rem", paddingBottom: "4.5rem" }}>
        <div
          className="tf-surface"
          style={{
            position: "relative",
            overflow: "hidden",
            display: "grid",
            gap: "1.2rem",
            padding: "clamp(1.4rem, 4vw, 2.4rem)",
          }}
        >
          <div className="compat-analyze-topbar" style={{ position: "relative", zIndex: 1 }}>
            <Link href="/compatibility/birthdates" className="compat-analyze-back">
              ← К форме
            </Link>
            <Link href="/compatibility/signs" className="compat-analyze-back">
              Игровая по знакам
            </Link>
          </div>

          <div className="compat-desktop-card" style={{ position: "relative", zIndex: 1 }}>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Черновики двух профилей
            </p>
            <h2 className="orbit-heading-2" style={{ margin: "0.35rem 0 0" }}>
              {result.label1} × {result.label2}
            </h2>
            <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "var(--orbit-color-muted)" }}>
              {formatDate(result.date1)} и {formatDate(result.date2)}
            </p>
            {limitations.length > 0 ? (
              <p className="orbit-body-sm" style={{ margin: "0.55rem 0 0", color: "#5f4930", lineHeight: 1.65 }} data-testid="compat-preview-limitations">
                Пока закрыто без времени/места: {limitations.join(", ")}. Глубокие советы и интимный слой — после сохранения
                профилей в аккаунте.
              </p>
            ) : null}
          </div>

          <div style={{ position: "relative", zIndex: 1 }}>
            <CompatibilityDynamicsSurface
              pairDisplay={`${result.label1} × ${result.label2}`}
              youColumnLabel={result.label1}
              partnerColumnLabel={result.label2}
              score={result.score}
              readingLead={quickReading?.headline || null}
              productSurface={result.product_surface}
              extraParagraphs={result.detail_paragraphs}
              paragraphsDetailTitle="Ещё о паре"
              showParagraphsUpsell
              omitIntroHero
            />
          </div>

          {result.funnel_artifact ? (
            <div style={{ position: "relative", zIndex: 1 }}>
              <CompatibilityFunnelSection artifact={result.funnel_artifact} omitTopMargin />
            </div>
          ) : null}

          <div className="compat-desktop-card" style={{ position: "relative", zIndex: 1 }}>
            <p className="orbit-body-sm" style={{ margin: 0, color: "#334155", lineHeight: 1.7 }}>
              {result.summary}
            </p>
          </div>

          {!isAuthenticated ? (
            <div className="compat-desktop-card" style={{ position: "relative", zIndex: 1, display: "grid", gap: "0.75rem" }}>
              <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", lineHeight: 1.65 }}>
                Сохрани оба профиля через email — совместимость останется привязанной к ним, а не к ссылке.
              </p>
              <Link
                href={VALUE_FIRST_PATHS.save}
                className="orbit-button orbit-button-primary"
                style={{ textDecoration: "none", textAlign: "center" }}
                data-testid="compat-preview-save"
                onClick={() => void onSaveClick()}
              >
                Сохранить оба профиля
              </Link>
            </div>
          ) : null}
        </div>
      </section>
    </ProductPageScreen>
  );
}

export default function CompatibilityBirthdatesResultPage() {
  return (
    <Suspense fallback={null}>
      <CompatibilityBirthdatesResultContent />
    </Suspense>
  );
}
