"use client";

import Link from "next/link";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { postJson } from "@/lib/api";
import { buildGuidancePrefillFromCompatibilityDynamics, stashGuidanceCompatibilityPrefill } from "@/lib/guidanceCompatibilityPrefill";
import { getLocale } from "@/lib/i18n";
import { useAuth } from "@/lib/useAuth";
import { COMPATIBILITY_GENERATION_TEMPLATE } from "@/lib/compatibilityDynamicsMode";
import {
  buildCompatibilityCheckKey,
  canGuestAccessCompatibility,
  tryConsumeGuestCompatibility,
} from "@/lib/guestAccessStore";
import { GuestAccessLimitGate } from "@/components/guest/GuestAccessLimitGate";
import { GUEST_ACCESS_COPY } from "@/components/guest/guestAccessCopy";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { CompatibilityDynamicsSurface, type SignCompatProductSurface } from "@/components/compatibility/CompatibilityDynamicsSurface";
import { CompatibilityFunnelSection, type CompatibilityFunnelArtifact } from "@/components/compatibility/CompatibilityFunnelSection";

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
  name_numbers_pair?: {
    status?: string;
    claim_lines?: string[];
  } | null;
};

type CompatibilityBirthdatesResult = {
  date1: string;
  date2: string;
  label1: string;
  label2: string;
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
  personalized?: CompatibilityDynamicsApiResponse["personalized"];
  name_numbers_pair?: CompatibilityDynamicsApiResponse["name_numbers_pair"];
};

function toBirthDateParam(raw: string): string {
  const t = raw.trim();
  if (!t) return t;
  return t.includes("T") ? (t.split("T")[0] ?? t) : t.slice(0, 10);
}

function formatDate(isoDate: string) {
  const tag = getLocale() === "ru" ? "ru-RU" : "en-US";
  return new Date(isoDate).toLocaleDateString(tag, {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function CompatibilityBirthdatesResultContent() {
  const searchParams = useSearchParams();
  const { isAuthenticated } = useAuth();
  const date1 = searchParams?.get("date1") || "";
  const date2 = searchParams?.get("date2") || "";
  const label1 = searchParams?.get("label1") || "Первый человек";
  const label2 = searchParams?.get("label2") || "Второй человек";
  const location1 = searchParams?.get("loc1") || "";
  const location2 = searchParams?.get("loc2") || "";
  const relationshipContext = searchParams?.get("ctx") || "";

  const compatCheckKey = buildCompatibilityCheckKey({
    mode: "precise",
    birth_date_1: toBirthDateParam(date1),
    birth_date_2: toBirthDateParam(date2),
    relationship_context: relationshipContext || undefined,
  });

  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<CompatibilityBirthdatesResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [shareCopied, setShareCopied] = useState(false);

  useEffect(() => {
    if (!date1 || !date2) {
      setError("Не указаны даты рождения.");
      setLoading(false);
      return;
    }

    if (!isAuthenticated && !canGuestAccessCompatibility(compatCheckKey)) {
      setLoading(false);
      return;
    }

    const loadCompatibility = async () => {
      try {
        const d1 = toBirthDateParam(date1);
        const d2 = toBirthDateParam(date2);
        if (!d1 || !d2) {
          throw new Error("Некорректные даты.");
        }

        const response = await postJson<CompatibilityDynamicsApiResponse>("/compatibility/dynamics", {
          mode: "precise",
          birth_date_1: d1,
          birth_date_2: d2,
          relationship_context: relationshipContext || undefined,
          generation: COMPATIBILITY_GENERATION_TEMPLATE,
          include_personalized: isAuthenticated,
          locale: getLocale(),
          name_1: label1,
          name_2: label2,
        });

        const paid = Boolean(response?.is_paid);
        const detailParagraphs = Array.isArray(response?.full_paragraphs)
          ? response.full_paragraphs.filter(Boolean)
          : Array.isArray(response?.free_paragraphs)
            ? response.free_paragraphs.filter(Boolean)
            : [];

        setResult({
          date1,
          date2,
          label1,
          label2,
          location1,
          location2,
          relationship_context: relationshipContext || undefined,
          score: response?.score ?? 0,
          summary: response?.summary || "Совместимость рассчитана.",
          quick_reading: response?.quick_reading || null,
          product_surface: response.product_surface,
          detail_paragraphs: detailParagraphs,
          is_paid: paid,
          funnel_artifact: response.funnel_artifact ?? null,
          personalized: response.personalized ?? null,
          name_numbers_pair: response.name_numbers_pair ?? null,
        });

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
  }, [date1, date2, label1, label2, location1, location2, relationshipContext, isAuthenticated, compatCheckKey]);

  const handleShare = async () => {
    const url = window.location.href;
    if (navigator.share) {
      try {
        await navigator.share({
          title: "Совместимость",
          text: "Результат",
          url,
        });
      } catch {
        return;
      }
      return;
    }
    await navigator.clipboard.writeText(url);
    setShareCopied(true);
    window.setTimeout(() => setShareCopied(false), 1600);
  };

  if (loading) {
    return (
      <ProductPageScreen
        testId="compat-birthdates-result-page"
        title="Совместимость по датам"
        loading
        loadingLabel="Загрузка…"
      />
    );
  }

  if (!isAuthenticated && !canGuestAccessCompatibility(compatCheckKey)) {
    return (
      <ProductPageScreen
        testId="compat-birthdates-result-page"
        title="Совместимость по датам"
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
        title="Совместимость по датам"
        hideHeader
        mainWide
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
        <section className="tf-shell" style={{ paddingTop: "2rem", paddingBottom: "3rem" }}>
          <div className="compat-desktop-shell compat-desktop-stack">
            <div className="compat-analyze-topbar">
              <Link href="/compatibility/birthdates" className="compat-analyze-back">
                ← К форме
              </Link>
              <Link href="/compatibility/analyze" className="compat-analyze-back">
                Единый экран
              </Link>
            </div>
            <div className="compat-desktop-card">
              <h1 className="orbit-display-sm" style={{ margin: 0 }}>
                Не удалось загрузить
              </h1>
              <p className="orbit-body compat-desktop-muted" style={{ margin: "0.65rem 0 0" }}>
                {error || "Проверь даты и попробуй снова."}
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", marginTop: "1rem" }}>
                <Link href="/compatibility/birthdates" className="orbit-button orbit-button-primary" style={{ textDecoration: "none" }}>
                  К форме
                </Link>
                <Link href="/compatibility" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none" }}>
                  По профилям
                </Link>
              </div>
            </div>
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
          <div
            aria-hidden="true"
            style={{
              position: "absolute",
              inset: 0,
              background:
                "radial-gradient(circle at top left, rgba(246, 233, 206, 0.44), transparent 32%), radial-gradient(circle at bottom right, rgba(221, 234, 219, 0.3), transparent 28%)",
              pointerEvents: "none",
            }}
          />

          <div className="compat-analyze-topbar" style={{ position: "relative", zIndex: 1 }}>
            <Link href="/compatibility/birthdates" className="compat-analyze-back">
              ← К форме
            </Link>
            <div style={{ display: "flex", gap: "0.65rem", flexWrap: "wrap", alignItems: "center" }}>
              <Link href="/compatibility/analyze" className="compat-analyze-back">
                Единый экран
              </Link>
              <Link href="/compatibility/signs" className="compat-analyze-back">
                Быстро по знакам
              </Link>
              <Link
                href="/tarot?from=compatibility"
                className="compat-analyze-back"
                onClick={() =>
                  stashGuidanceCompatibilityPrefill(
                    buildGuidancePrefillFromCompatibilityDynamics({
                      pair_display: `${result.label1} × ${result.label2}`,
                      from_sign_name: result.label1,
                      to_sign_name: result.label2,
                      relationship_context: result.relationship_context,
                      score: result.score,
                      product_surface: { score_tagline: result.product_surface.score_tagline },
                      funnel_artifact: result.funnel_artifact,
                      personalized: result.personalized,
                    })
                  )
                }
              >
                Guidance
              </Link>
              <button
                type="button"
                onClick={handleShare}
                className="compat-analyze-back"
                style={{ border: "none", background: "transparent", cursor: "pointer", padding: 0, font: "inherit" }}
              >
                {shareCopied ? "Скопировано" : "Поделиться"}
              </button>
            </div>
          </div>

          <div className="compat-desktop-card" style={{ position: "relative", zIndex: 1 }}>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Данные пары
            </p>
            <h2 className="orbit-heading-2" style={{ margin: "0.35rem 0 0" }}>
              {result.label1} × {result.label2}
            </h2>
            <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "var(--orbit-color-muted)" }}>
              {formatDate(result.date1)} и {formatDate(result.date2)}
            </p>
            {result.location1 || result.location2 ? (
              <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "var(--orbit-color-muted)" }}>
                {result.location1 ? `${result.label1}: ${result.location1}` : ""}
                {result.location1 && result.location2 ? " • " : ""}
                {result.location2 ? `${result.label2}: ${result.location2}` : ""}
              </p>
            ) : null}
            <p className="orbit-body-xs" style={{ margin: "0.55rem 0 0", color: "#64748b", lineHeight: 1.55 }}>
              Расчёт через даты на сервере: солнечные знаки + воронка «средний уровень» (выше, чем только знаки). Полный натал, дома и глубокий слой — в профилях с местом и временем рождения.
            </p>
          </div>

          <div style={{ position: "relative", zIndex: 1 }}>
            {result.name_numbers_pair?.claim_lines?.[0] ? (
              <p
                className="orbit-body-xs"
                style={{ margin: "0 0 0.85rem", color: "#64748b", lineHeight: 1.55 }}
                data-testid="compat-name-numbers-claim"
              >
                {result.name_numbers_pair.claim_lines[0]}
              </p>
            ) : null}
            <CompatibilityDynamicsSurface
              pairDisplay={`${result.label1} × ${result.label2}`}
              youColumnLabel={result.label1}
              partnerColumnLabel={result.label2}
              score={result.score}
              readingLead={quickReading?.headline || null}
              productSurface={result.product_surface}
              extraParagraphs={result.detail_paragraphs}
              paragraphsDetailTitle="Ещё текст про пару"
              showParagraphsUpsell={!result.is_paid}
              omitIntroHero
            />
          </div>

          {result.funnel_artifact ? (
            <div style={{ position: "relative", zIndex: 1 }}>
              <CompatibilityFunnelSection artifact={result.funnel_artifact} omitTopMargin />
            </div>
          ) : null}

          <div className="compat-desktop-card" style={{ position: "relative", zIndex: 1 }}>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Короткая сводка по знакам Солнца
            </p>
            <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.7 }}>
              {result.summary}
            </p>
          </div>
        </div>
      </section>
    </ProductPageScreen>
  );
}

export default function CompatibilityBirthdatesResultPage() {
  return (
    <Suspense
      fallback={
        <ProductPageScreen
          testId="compat-birthdates-result-page"
          title="Совместимость по датам"
          loading
          loadingLabel="Загрузка…"
        />
      }
    >
      <CompatibilityBirthdatesResultContent />
    </Suspense>
  );
}
