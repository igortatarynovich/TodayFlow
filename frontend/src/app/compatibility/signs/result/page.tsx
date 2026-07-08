"use client";

import Link from "next/link";
import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getJson } from "@/lib/api";
import { buildGuidancePrefillFromCompatibilityDynamics, stashGuidanceCompatibilityPrefill } from "@/lib/guidanceCompatibilityPrefill";
import { getLocale } from "@/lib/i18n";
import { useAuth } from "@/lib/useAuth";
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

type SignCompatibilityPayload = {
  from_sign: string;
  to_sign: string;
  from_sign_name: string;
  to_sign_name: string;
  from_gender?: string | null;
  to_gender?: string | null;
  score: number;
  summary: string;
  quick_reading?: {
    headline?: string;
    strongest?: string;
    friction?: string;
    next_step?: string;
    strengths?: string[];
    cautions?: string[];
  } | null;
  free_paragraphs: string[];
  full_paragraphs: string[];
  is_paid: boolean;
  content_id: string;
  relationship_context?: string | null;
  product_surface: SignCompatProductSurface;
  personalized?: {
    profile_ready?: boolean;
    headline?: string;
    hint?: string;
    focus?: string;
    do_focus?: string;
    avoid_focus?: string;
  } | null;
  funnel_artifact?: CompatibilityFunnelArtifact | null;
};

function ResultContent() {
  const params = useSearchParams();
  const { isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SignCompatibilityPayload | null>(null);

  const fromSign = params?.get("from") || "";
  const toSign = params?.get("to") || "";
  const fromGender = params?.get("from_gender") || "unknown";
  const toGender = params?.get("to_gender") || "unknown";
  const relationshipContext = params?.get("ctx") || "";

  const compatCheckKey = buildCompatibilityCheckKey({
    mode: "signs",
    from: fromSign,
    to: toSign,
    relationship_context: relationshipContext || undefined,
  });

  useEffect(() => {
    if (!fromSign || !toSign) {
      setError("Не удалось определить пару знаков.");
      setLoading(false);
      return;
    }

    if (!isAuthenticated && !canGuestAccessCompatibility(compatCheckKey)) {
      setLoading(false);
      return;
    }

    setLoading(true);
    const ctxQ = relationshipContext ? `&relationship_context=${encodeURIComponent(relationshipContext)}` : "";
    const localeQ = `&locale=${encodeURIComponent(getLocale())}`;
    getJson<SignCompatibilityPayload>(
      `/compatibility/signs?from=${encodeURIComponent(fromSign)}&to=${encodeURIComponent(toSign)}&from_gender=${encodeURIComponent(fromGender)}&to_gender=${encodeURIComponent(toGender)}&include_personalized=true${ctxQ}${localeQ}`,
    )
      .then((data) => {
        setResult(data);
        if (!isAuthenticated) {
          tryConsumeGuestCompatibility(compatCheckKey);
        }
      })
      .catch((err: { message?: string }) => setError(err?.message || "Не удалось загрузить совместимость"))
      .finally(() => setLoading(false));
  }, [fromSign, toSign, fromGender, toGender, relationshipContext, isAuthenticated, compatCheckKey]);

  const paragraphs = useMemo(() => {
    if (!result) return [];
    return (result.is_paid ? result.full_paragraphs : result.free_paragraphs).filter(Boolean);
  }, [result]);

  if (loading) {
    return (
      <ProductPageScreen
        testId="compat-signs-result-page"
        title="Совместимость по знакам"
        loading
        loadingLabel="Загрузка…"
      />
    );
  }

  if (!isAuthenticated && !canGuestAccessCompatibility(compatCheckKey)) {
    return (
      <ProductPageScreen
        testId="compat-signs-result-page"
        title="Совместимость по знакам"
        hideHeader
        mainWide
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
        <section className="tf-shell" style={{ paddingTop: "2rem", paddingBottom: "4.5rem" }}>
          <GuestAccessLimitGate
            title={GUEST_ACCESS_COPY.compatLimitTitle}
            body={GUEST_ACCESS_COPY.compatLimitBody}
            secondaryHref="/compatibility/signs"
            secondaryLabel="← К знакам"
            testId="guest-compat-signs-result-limit"
          />
        </section>
      </ProductPageScreen>
    );
  }

  if (error || !result) {
    return (
      <ProductPageScreen
        testId="compat-signs-result-page"
        title="Совместимость по знакам"
        hideHeader
        mainWide
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
        <section className="tf-shell" style={{ paddingTop: "2rem", paddingBottom: "3rem" }}>
          <div className="compat-desktop-shell compat-desktop-stack">
            <div className="compat-analyze-topbar">
              <Link href="/compatibility/signs" className="compat-analyze-back">
                ← К знакам
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
                {error || "Выбери пару знаков снова."}
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", marginTop: "1rem" }}>
                <Link href="/compatibility/signs" className="orbit-button orbit-button-primary" style={{ textDecoration: "none" }}>
                  К знакам
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
  const generalStrongestText =
    quickReading?.strongest ||
    quickReading?.strengths?.[0] ||
    "Прямой разговор важнее догадок.";
  const generalFrictionText =
    quickReading?.friction ||
    quickReading?.cautions?.[0] ||
    "Риск — ждать совпадения без настройки ритма и границ.";
  const personalStrongestText = result.personalized?.do_focus || generalStrongestText;
  const personalFrictionText = result.personalized?.avoid_focus || generalFrictionText;

  const personalizedCard =
    isAuthenticated && result.personalized ? (
      <div className="compat-personalized-inline">
        <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", fontWeight: 700 }}>
          С учётом профиля
        </p>
        <h2 className="orbit-heading-2" style={{ margin: "0.45rem 0 0" }}>
          {result.personalized.headline || "Как твой ритм влияет на пару"}
        </h2>
        {result.personalized.hint ? (
          <p className="orbit-body-sm compat-desktop-muted" style={{ margin: "0.65rem 0 0" }}>
            {result.personalized.hint}
          </p>
        ) : null}
        <div
          style={{
            marginTop: "0.9rem",
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "0.75rem",
          }}
        >
          <div className="compat-callout-go">
            <p className="orbit-body-xs" style={{ margin: 0, color: "#166534", fontWeight: 700 }}>
              Опора
            </p>
            <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#14532d", lineHeight: 1.55 }}>
              {personalStrongestText}
            </p>
          </div>
          <div className="compat-callout-warn">
            <p className="orbit-body-xs" style={{ margin: 0, color: "#92400e", fontWeight: 700 }}>
              Риск
            </p>
            <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#78350f", lineHeight: 1.55 }}>
              {personalFrictionText}
            </p>
          </div>
        </div>
      </div>
    ) : undefined;

  return (
    <ProductPageScreen
      testId="compat-signs-result-page"
      title={`${result.from_sign_name} × ${result.to_sign_name}`}
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
            <Link href="/compatibility/signs" className="compat-analyze-back">
              ← Назад к вводу
            </Link>
            <div style={{ display: "flex", gap: "0.65rem", flexWrap: "wrap", alignItems: "center" }}>
              <Link href="/compatibility/analyze" className="compat-analyze-back">
                Единый экран
              </Link>
              <Link href="/compatibility/birthdates" className="compat-analyze-back">
                Точнее по датам
              </Link>
              <Link
                href="/tarot?from=compatibility"
                className="compat-analyze-back"
                onClick={() =>
                  stashGuidanceCompatibilityPrefill(
                    buildGuidancePrefillFromCompatibilityDynamics({
                      from_sign_name: result.from_sign_name,
                      to_sign_name: result.to_sign_name,
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
              <Link href="/compatibility" className="compat-analyze-back">
                По профилям
              </Link>
            </div>
          </div>

          <div style={{ position: "relative", zIndex: 1 }}>
            <CompatibilityDynamicsSurface
              pairDisplay={`${result.from_sign_name} × ${result.to_sign_name}`}
              youColumnLabel="твой знак в паре"
              partnerColumnLabel="знак партнёра"
              score={result.score}
              readingLead={quickReading?.headline || null}
              productSurface={result.product_surface}
              personalizedCard={personalizedCard}
              extraParagraphs={paragraphs}
              paragraphsDetailTitle="Ещё текст про пару"
              showParagraphsUpsell={!result.is_paid}
            />
          </div>

          {result.funnel_artifact ? (
            <div style={{ position: "relative", zIndex: 1 }}>
              <CompatibilityFunnelSection artifact={result.funnel_artifact} omitTopMargin />
            </div>
          ) : null}

          <div className="compat-desktop-card" style={{ position: "relative", zIndex: 1 }}>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Короткая сводка знаков
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

export default function CompatibilitySignsResultPage() {
  return (
    <Suspense
      fallback={
        <ProductPageScreen
          testId="compat-signs-result-page"
          title="Совместимость по знакам"
          loading
          loadingLabel="Загрузка…"
        />
      }
    >
      <ResultContent />
    </Suspense>
  );
}
