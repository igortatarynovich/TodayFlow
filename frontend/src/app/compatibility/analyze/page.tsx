"use client";

import Link from "next/link";
import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { buildGuidancePrefillFromCompatibilityDynamics } from "@/lib/guidanceCompatibilityPrefill";
import { buildExplorationFromDynamics } from "@/lib/buildCompatibilityExplorationModel";
import { CompatibilityExplorationResult } from "@/components/compatibility/CompatibilityExplorationResult";
import type { CompatibilityFunnelArtifact } from "@/components/compatibility/CompatibilityFunnelSection";
import type { SignCompatProductSurface } from "@/components/compatibility/CompatibilityDynamicsSurface";
import { getScenarioSkin, resolveScenarioId } from "@/lib/compatibilityScenarioSkins";
import { postJson } from "@/lib/api";
import { COMPATIBILITY_GENERATION_LIVE } from "@/lib/compatibilityDynamicsMode";
import {
  lifecycleStatusLabel,
  parseGenerationLifecycle,
  type GenerationLifecycle,
} from "@/lib/generationLifecycle";
import { pollCompatibilityJob, retryCompatibilityJob } from "@/lib/pollGenerationJob";
import { stripCompatibilityDisplayGarbage } from "@/lib/compatibilityCopySanitize";
import {
  buildCompatibilityDeepOpenEvent,
  buildCompatibilityScenarioSwitchEvent,
  type CompatibilityLearningMeta,
} from "@/lib/compatibilityEcho";
import {
  fetchCompatibilityEncyclopedia,
  findEncyclopediaSelection,
  type CompatibilityEncyclopediaResponse,
} from "@/lib/compatibilityEncyclopediaApi";
import { resolveClientLocale } from "@/lib/i18n";
import {
  RELATIONSHIP_CONTEXT_OPTIONS,
  type RelationshipContextId,
} from "@/lib/compatibilityRelationshipContext";
import { ZODIAC_OPTIONS } from "@/lib/zodiacOptions";
import { useAuth } from "@/lib/useAuth";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import {
  buildCompatibilityCheckKey,
  canGuestAccessCompatibility,
  guestCompatibilityRemaining,
  isGuestCompatibilityLimitReached,
  tryConsumeGuestCompatibility,
} from "@/lib/guestAccessStore";
import { GuestAccessLimitGate } from "@/components/guest/GuestAccessLimitGate";
import { GUEST_ACCESS_COPY } from "@/components/guest/guestAccessCopy";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";

type DynamicsResponse = {
  from_sign: string;
  to_sign: string;
  from_sign_name: string;
  to_sign_name: string;
  score: number;
  product_surface: SignCompatProductSurface;
  generation_source?: string | null;
  pair_dynamics?: Record<string, unknown> | null;
  personalized?: {
    headline?: string;
    hint?: string;
    do_focus?: string;
    avoid_focus?: string;
  } | null;
  relationship_context?: string | null;
  funnel_artifact?: CompatibilityFunnelArtifact | null;
  attachment_reference?: Record<string, unknown> | null;
  access_disclosure?: {
    tier?: string;
    locked_layers?: string[];
    upsell?: {
      title?: string;
      body?: string;
      cta_register?: string;
      cta_subscribe?: string;
    } | null;
    guidance?: {
      yes_no?: { answer?: string; framing?: string };
      do?: string[];
      dont?: string[];
      how?: string[];
    } | null;
  } | null;
  generation_lifecycle?: GenerationLifecycle | null;
};

export default function CompatibilityAnalyzePage() {
  return (
    <Suspense
      fallback={
        <ProductPageScreen
          testId="compat-analyze-page"
          title="Разбор совместимости"
          loading
          loadingLabel="Загрузка…"
        />
      }
    >
      <CompatibilityAnalyzeContent />
    </Suspense>
  );
}

function CompatibilityAnalyzeContent() {
  const searchParams = useSearchParams();
  const topicId = searchParams.get("topic")?.trim() || null;
  const readingId = searchParams.get("reading")?.trim() || null;
  const seriesId = searchParams.get("series")?.trim() || null;
  const { isAuthenticated } = useAuth();
  const { trackMeaningEvent } = useMeaningRuntime();
  const topicSelectTracked = useRef(false);
  const [catalog, setCatalog] = useState<CompatibilityEncyclopediaResponse | null>(null);
  const [entryMode, setEntryMode] = useState<"quick" | "precise">("quick");
  const [signFrom, setSignFrom] = useState("");
  const [signTo, setSignTo] = useState("");
  const [name1, setName1] = useState("");
  const [name2, setName2] = useState("");
  const [birth1, setBirth1] = useState("");
  const [birth2, setBirth2] = useState("");
  const [relationshipContext, setRelationshipContext] = useState<RelationshipContextId | "">("");

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DynamicsResponse | null>(null);
  const [lifecycle, setLifecycle] = useState<GenerationLifecycle | null>(null);
  const enrichAbortRef = useRef<AbortController | null>(null);
  const [limitBlocked, setLimitBlocked] = useState(false);
  const deepOpenTracked = useRef(false);

  useEffect(() => {
    const locale = resolveClientLocale();
    void fetchCompatibilityEncyclopedia(locale).then(setCatalog);
  }, []);

  const selectionPreview = useMemo(
    () => (catalog ? findEncyclopediaSelection(catalog, { topic: topicId, reading: readingId, series: seriesId }) : null),
    [catalog, topicId, readingId, seriesId],
  );

  useEffect(() => {
    if (!selectionPreview || topicSelectTracked.current) return;
    topicSelectTracked.current = true;
    trackMeaningEvent({
      event_type: "compatibility_topic_select",
      event_source: "compatibility",
      idempotency_key: `compatibility_topic_select:analyze:${topicId ?? readingId ?? seriesId ?? "unknown"}:${new Date().toISOString().slice(0, 10)}`,
      payload: {
        selection_kind: topicId ? "category" : readingId ? "reading" : seriesId ? "series" : "unknown",
        selection_id: topicId ?? readingId ?? seriesId ?? null,
        topic_id: topicId,
        reading_id: readingId,
        series_id: seriesId,
        surface: "analyze",
      },
    });
  }, [readingId, selectionPreview, seriesId, topicId, trackMeaningEvent]);

  const canQuickSubmit = Boolean(signFrom && signTo);
  const canPreciseSubmit = Boolean(birth1 && birth2);
  const compatRemaining = guestCompatibilityRemaining();

  const buildCompatCheckKey = useCallback(
    (mode: "quick" | "precise") =>
      mode === "quick"
        ? buildCompatibilityCheckKey({
            mode: "quick",
            from_sign: signFrom,
            to_sign: signTo,
            relationship_context: relationshipContext || undefined,
          })
        : buildCompatibilityCheckKey({
            mode: "precise",
            birth_date_1: birth1,
            birth_date_2: birth2,
            relationship_context: relationshipContext || undefined,
          }),
    [birth1, birth2, relationshipContext, signFrom, signTo],
  );

  const pairTitle = result ? `${result.from_sign_name} × ${result.to_sign_name}` : "";

  const guidancePrefill = useMemo(
    () =>
      result
        ? buildGuidancePrefillFromCompatibilityDynamics({
            from_sign_name: result.from_sign_name,
            to_sign_name: result.to_sign_name,
            relationship_context: result.relationship_context,
            score: result.score,
            product_surface: { score_tagline: result.product_surface.score_tagline },
            funnel_artifact: result.funnel_artifact,
            personalized: result.personalized,
          })
        : null,
    [result]
  );

  const explorationModel = useMemo(
    () =>
      result
        ? buildExplorationFromDynamics({
            topicId,
            seriesId,
            readingId,
            pairTitle,
            score: result.score,
            productSurface: result.product_surface,
          })
        : null,
    [result, topicId, seriesId, readingId, pairTitle],
  );

  const scenarioSkin = useMemo(
    () => getScenarioSkin(resolveScenarioId({ topic: topicId, series: seriesId, reading: readingId })),
    [topicId, seriesId, readingId],
  );

  const buildPayload = useCallback(
    (mode: "quick" | "precise") => {
      const base: Record<string, unknown> = {
        generation: COMPATIBILITY_GENERATION_LIVE,
        include_personalized: isAuthenticated,
        relationship_context: relationshipContext || undefined,
        locale: resolveClientLocale(),
        topic_id: topicId || undefined,
        reading_id: readingId || undefined,
        series_id: seriesId || undefined,
      };
      if (mode === "quick") {
        return {
          ...base,
          mode: "quick",
          from_sign: signFrom,
          to_sign: signTo,
          name_1: name1.trim() || undefined,
          name_2: name2.trim() || undefined,
        };
      }
      return {
        ...base,
        mode: "precise",
        birth_date_1: birth1,
        birth_date_2: birth2,
        name_1: name1.trim() || undefined,
        name_2: name2.trim() || undefined,
      };
    },
    [birth1, birth2, isAuthenticated, name1, name2, relationshipContext, signFrom, signTo, topicId, readingId, seriesId]
  );

  const learningMeta = useMemo<CompatibilityLearningMeta>(
    () => ({
      surface: "analyze_dynamics",
      scenarioId: scenarioSkin.id,
      formatId: seriesId ?? topicId ?? readingId,
      toneMode: scenarioSkin.toneMode,
      fromSign: result?.from_sign ?? null,
      toSign: result?.to_sign ?? null,
      score: result?.score ?? null,
    }),
    [readingId, result, scenarioSkin.id, scenarioSkin.toneMode, seriesId, topicId],
  );

  const handleScenarioSwitch = useCallback(
    (toScenarioId: string, href: string) => {
      trackMeaningEvent(buildCompatibilityScenarioSwitchEvent(learningMeta, toScenarioId, href));
    },
    [learningMeta, trackMeaningEvent],
  );

  const handleDeepOpen = useCallback(() => {
    if (deepOpenTracked.current) return;
    deepOpenTracked.current = true;
    trackMeaningEvent(buildCompatibilityDeepOpenEvent(learningMeta));
  }, [learningMeta, trackMeaningEvent]);

  const runDynamics = useCallback(
    async (mode: "quick" | "precise") => {
      setBusy(true);
      setError(null);
      enrichAbortRef.current?.abort();
      enrichAbortRef.current = new AbortController();
      const signal = enrichAbortRef.current.signal;
      try {
        const data = await postJson<DynamicsResponse>("/compatibility/dynamics", buildPayload(mode));
        setResult(data);
        const lc = parseGenerationLifecycle(data.generation_lifecycle) ?? {
          status: "baseline_ready" as const,
          source: data.generation_source || "template",
          is_fully_personal: false,
        };
        setLifecycle(lc);
        if (!isAuthenticated) {
          tryConsumeGuestCompatibility(buildCompatCheckKey(mode));
        }
        trackMeaningEvent({
          event_type: "compatibility_view",
          event_source: "compatibility",
          idempotency_key: `compatibility_view:analyze:${data.from_sign}:${data.to_sign}:${topicId ?? readingId ?? seriesId ?? "none"}:${new Date().toISOString().slice(0, 10)}`,
          payload: {
            surface: "analyze_dynamics",
            mode,
            topic_id: topicId,
            reading_id: readingId,
            series_id: seriesId,
            format_id: seriesId ?? topicId ?? readingId,
            tone_mode: scenarioSkin.toneMode,
            from_sign: data.from_sign,
            to_sign: data.to_sign,
            score: data.score,
            lifecycle: lc.status,
          },
        });
        // First paint done — enrich in background without blocking UI.
        setBusy(false);
        if (
          isAuthenticated &&
          lc.status === "enrichment_pending" &&
          typeof lc.job_id === "number"
        ) {
          void pollCompatibilityJob(lc.job_id, { signal }).then((polled) => {
            if (!polled || signal.aborted) return;
            setLifecycle(polled.lifecycle);
            if (polled.lifecycle.status === "enriched" && polled.product_surface) {
              setResult((prev) =>
                prev
                  ? {
                      ...prev,
                      product_surface: polled.product_surface as DynamicsResponse["product_surface"],
                      generation_source: polled.generation_source ?? "llm",
                      score: typeof polled.score === "number" ? polled.score : prev.score,
                      access_disclosure:
                        (polled.access_disclosure as DynamicsResponse["access_disclosure"]) ??
                        prev.access_disclosure,
                      generation_lifecycle: polled.lifecycle,
                    }
                  : prev,
              );
            }
          });
        }
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : "Не удалось загрузить разбор.";
        setError(msg);
        setBusy(false);
      }
    },
    [buildCompatCheckKey, buildPayload, isAuthenticated, readingId, scenarioSkin.toneMode, seriesId, topicId, trackMeaningEvent]
  );

  const resetDeepOpenTracking = useCallback(() => {
    deepOpenTracked.current = false;
  }, []);

  const submitQuick = async () => {
    if (!canQuickSubmit) return;
    if (
      !isAuthenticated &&
      isGuestCompatibilityLimitReached() &&
      !canGuestAccessCompatibility(buildCompatCheckKey("quick"))
    ) {
      setLimitBlocked(true);
      return;
    }
    resetDeepOpenTracking();
    setEntryMode("quick");
    await runDynamics("quick");
  };

  const submitPrecise = async () => {
    if (!canPreciseSubmit) return;
    if (
      !isAuthenticated &&
      isGuestCompatibilityLimitReached() &&
      !canGuestAccessCompatibility(buildCompatCheckKey("precise"))
    ) {
      setLimitBlocked(true);
      return;
    }
    resetDeepOpenTracking();
    setEntryMode("precise");
    await runDynamics("precise");
  };

  const personalizedSlot = useMemo(() => {
    if (!result?.personalized?.headline) return null;
    const p = result.personalized;
    return (
      <div>
        <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", fontWeight: 700 }}>
          Через твой профиль
        </p>
        <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.65 }}>
          {p.headline}
        </p>
        {p.do_focus ? (
          <p className="orbit-body-xs" style={{ margin: "0.55rem 0 0", color: "#166534", lineHeight: 1.55 }}>
            Усилить: {p.do_focus}
          </p>
        ) : null}
        {p.avoid_focus ? (
          <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#9a3412", lineHeight: 1.55 }}>
            Осторожнее с: {p.avoid_focus}
          </p>
        ) : null}
      </div>
    );
  }, [result]);

  return (
    <ProductPageScreen
      testId="compat-analyze-page"
      title="Разбор совместимости"
      hideHeader
      mainWide
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      {limitBlocked ? (
        <section className="tf-shell" style={{ paddingTop: "1.75rem", paddingBottom: "3rem" }}>
          <GuestAccessLimitGate
            title={GUEST_ACCESS_COPY.compatLimitTitle}
            body={GUEST_ACCESS_COPY.compatLimitBody}
            secondaryHref="/compatibility"
            secondaryLabel="← К совместимости"
            testId="guest-compat-analyze-limit"
          />
        </section>
      ) : (
      <section className="tf-shell" style={{ paddingTop: "1.75rem", paddingBottom: "3rem" }}>
        <div className="compat-desktop-shell compat-desktop-stack">
          <div className="compat-analyze-topbar">
            <Link href="/compatibility" className="compat-analyze-back">
              ← К исследованию
            </Link>
          </div>

          <div
            className="compat-desktop-card compat-desktop-col-12"
            style={{
              marginBottom: "0.5rem",
              background: "linear-gradient(180deg, rgba(255,251,245,0.98), rgba(255,255,255,0.96))",
              border: "1px solid rgba(201,168,115,0.35)",
            }}
          >
            <p className="orbit-body-xs" style={{ margin: 0, color: "#8f6b3a", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em" }}>
              {scenarioSkin.emoji} {scenarioSkin.poster}
            </p>
            <h2 className="orbit-heading-2" style={{ margin: "0.45rem 0 0", fontSize: "clamp(1.2rem, 2.5vw, 1.45rem)" }}>
              {scenarioSkin.posterSubtitle}
            </h2>
            {selectionPreview?.introBlocks.map((block, idx) => {
              const text = stripCompatibilityDisplayGarbage(block.text);
              return text ? (
                <p key={`${block.kind}-${idx}`} className="orbit-body-sm" style={{ margin: "0.55rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                  {text}
                </p>
              ) : null;
            })}
          </div>

          <div id="compat-entry" className="compat-desktop-card compat-desktop-col-12" style={{ scrollMarginTop: "96px" }}>
            <div>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Режим расчёта
              </p>
              <h1 className="orbit-display" style={{ margin: "0.35rem 0 0", fontSize: "clamp(1.35rem, 2.8vw, 1.85rem)" }}>
                {entryMode === "quick" ? "Быстрый разбор · ~30 секунд" : "Точный разбор · по данным"}
              </h1>
              {!isAuthenticated && compatRemaining < 4 ? (
                <p className="orbit-body-sm" style={{ margin: "0.65rem 0 0", color: "var(--orbit-color-muted, #6b6560)" }}>
                  {GUEST_ACCESS_COPY.remainingCompat(compatRemaining)}
                </p>
              ) : null}
            </div>

            <div className="compat-desktop-entry-tabs" style={{ marginTop: "1rem" }}>
              <button
                type="button"
                className="orbit-button orbit-button-secondary orbit-button-sm"
                onClick={() => setEntryMode("quick")}
                style={{
                  borderColor: entryMode === "quick" ? "rgba(167, 123, 55, 0.88)" : undefined,
                  background: entryMode === "quick" ? "rgba(242, 220, 181, 0.35)" : undefined,
                }}
              >
                🎲 По знакам
              </button>
              <button
                type="button"
                className="orbit-button orbit-button-secondary orbit-button-sm"
                onClick={() => setEntryMode("precise")}
                style={{
                  borderColor: entryMode === "precise" ? "rgba(167, 123, 55, 0.88)" : undefined,
                  background: entryMode === "precise" ? "rgba(242, 220, 181, 0.35)" : undefined,
                }}
              >
                ❤️ По профилям / датам
              </button>
            </div>

            <div className="compat-desktop-grid-12" style={{ marginTop: "1rem" }}>
              <div className="compat-desktop-col-6">
                <p className="orbit-body-sm" style={{ margin: "0 0 0.65rem", fontWeight: 700, color: "#5f4323" }}>
                  Выбор знаков
                </p>
                <div style={{ display: "grid", gap: "0.65rem" }}>
                  <label className="orbit-body-xs" style={{ display: "grid", gap: "0.35rem", color: "#64748b" }}>
                    Твой знак
                    <select
                      className="orbit-input"
                      value={signFrom}
                      onChange={(e) => setSignFrom(e.target.value)}
                      disabled={entryMode !== "quick"}
                    >
                      <option value="">—</option>
                      {ZODIAC_OPTIONS.map((z) => (
                        <option key={z.id} value={z.id}>
                          {z.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="orbit-body-xs" style={{ display: "grid", gap: "0.35rem", color: "#64748b" }}>
                    Знак партнёра
                    <select
                      className="orbit-input"
                      value={signTo}
                      onChange={(e) => setSignTo(e.target.value)}
                      disabled={entryMode !== "quick"}
                    >
                      <option value="">—</option>
                      {ZODIAC_OPTIONS.map((z) => (
                        <option key={z.id} value={z.id}>
                          {z.name}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
                <button
                  type="button"
                  className="orbit-button orbit-button-primary orbit-button-sm"
                  style={{ marginTop: "0.85rem" }}
                  disabled={entryMode !== "quick" || !canQuickSubmit || busy}
                  onClick={() => void submitQuick()}
                >
                  {busy && entryMode === "quick" ? "Считаем…" : "Посмотреть совместимость"}
                </button>
              </div>

              <div className="compat-desktop-col-6">
                <p className="orbit-body-sm" style={{ margin: "0 0 0.65rem", fontWeight: 700, color: "#5f4323" }}>
                  Ввод данных
                </p>
                <div style={{ display: "grid", gap: "0.65rem" }}>
                  <label className="orbit-body-xs" style={{ display: "grid", gap: "0.35rem", color: "#64748b" }}>
                    Имя (ты) — опционально
                    <input className="orbit-input" value={name1} onChange={(e) => setName1(e.target.value)} placeholder="Например, Аня" />
                  </label>
                  <label className="orbit-body-xs" style={{ display: "grid", gap: "0.35rem", color: "#64748b" }}>
                    Имя партнёра — опционально
                    <input className="orbit-input" value={name2} onChange={(e) => setName2(e.target.value)} placeholder="Например, Макс" />
                  </label>
                  <label className="orbit-body-xs" style={{ display: "grid", gap: "0.35rem", color: "#64748b" }}>
                    Твоя дата рождения
                    <input
                      className="orbit-input"
                      type="date"
                      value={birth1}
                      onChange={(e) => setBirth1(e.target.value)}
                      disabled={entryMode !== "precise"}
                    />
                  </label>
                  <label className="orbit-body-xs" style={{ display: "grid", gap: "0.35rem", color: "#64748b" }}>
                    Дата рождения партнёра
                    <input
                      className="orbit-input"
                      type="date"
                      value={birth2}
                      onChange={(e) => setBirth2(e.target.value)}
                      disabled={entryMode !== "precise"}
                    />
                  </label>
                </div>
                <button
                  type="button"
                  className="orbit-button orbit-button-primary orbit-button-sm"
                  style={{ marginTop: "0.85rem" }}
                  disabled={entryMode !== "precise" || !canPreciseSubmit || busy}
                  onClick={() => void submitPrecise()}
                >
                  {busy && entryMode === "precise" ? "Считаем…" : "Точный разбор"}
                </button>
              </div>

              <div className="compat-desktop-col-12" style={{ marginTop: "0.5rem" }}>
                <p className="orbit-body-sm" style={{ margin: "0 0 0.55rem", fontWeight: 700, color: "#5f4323" }}>
                  Что сейчас между вами?
                </p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem" }}>
                  <button
                    type="button"
                    className="orbit-button orbit-button-secondary orbit-button-sm"
                    onClick={() => setRelationshipContext("")}
                    style={{
                      borderColor: relationshipContext === "" ? "rgba(167, 123, 55, 0.88)" : undefined,
                      background: relationshipContext === "" ? "rgba(242, 220, 181, 0.32)" : undefined,
                    }}
                  >
                    не указывать
                  </button>
                  {RELATIONSHIP_CONTEXT_OPTIONS.map((opt) => {
                    const active = relationshipContext === opt.id;
                    return (
                      <button
                        key={opt.id}
                        type="button"
                        className="orbit-button orbit-button-secondary orbit-button-sm"
                        onClick={() => setRelationshipContext(opt.id)}
                        style={{
                          borderColor: active ? "rgba(167, 123, 55, 0.88)" : undefined,
                          background: active ? "rgba(242, 220, 181, 0.32)" : undefined,
                          fontSize: "0.78rem",
                        }}
                      >
                        {opt.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {error ? (
              <p className="orbit-body-sm" style={{ margin: "1rem 0 0", color: "#b91c1c" }}>
                {error}
              </p>
            ) : null}
            {lifecycle ? (
              <p
                className="orbit-body-sm"
                data-testid="compat-lifecycle-status"
                style={{ margin: "0.75rem 0 0", color: "#5e4222" }}
              >
                {lifecycleStatusLabel(lifecycle.status)}
                {lifecycle.status === "enrichment_failed" && typeof lifecycle.job_id === "number" ? (
                  <>
                    {" "}
                    <button
                      type="button"
                      className="orbit-button orbit-button-ghost"
                      onClick={() => {
                        const id = lifecycle.job_id;
                        if (typeof id !== "number") return;
                        void retryCompatibilityJob(id).then((next) => {
                          if (!next) return;
                          setLifecycle(next);
                          if (next.status === "enrichment_pending") {
                            void pollCompatibilityJob(id).then((polled) => {
                              if (!polled) return;
                              setLifecycle(polled.lifecycle);
                              if (polled.lifecycle.status === "enriched" && polled.product_surface) {
                                setResult((prev) =>
                                  prev
                                    ? {
                                        ...prev,
                                        product_surface:
                                          polled.product_surface as DynamicsResponse["product_surface"],
                                        generation_source: polled.generation_source ?? "llm",
                                        generation_lifecycle: polled.lifecycle,
                                      }
                                    : prev,
                                );
                              }
                            });
                          }
                        });
                      }}
                    >
                      Повторить
                    </button>
                  </>
                ) : null}
              </p>
            ) : null}
          </div>

          {result && explorationModel ? (
            <CompatibilityExplorationResult
              model={explorationModel}
              personalizedSlot={personalizedSlot}
              funnelArtifact={result.funnel_artifact ?? null}
              accessDisclosure={result.access_disclosure ?? null}
              guidancePrefill={guidancePrefill}
              onScenarioSwitch={handleScenarioSwitch}
              onDeepOpen={handleDeepOpen}
            />
          ) : (
            <p className="orbit-body-sm compat-desktop-muted" style={{ margin: 0 }}>
              Выбери знаки или даты и контекст — разбор появится здесь.
            </p>
          )}
        </div>
      </section>
      )}
    </ProductPageScreen>
  );
}
