"use client";

import Link from "next/link";
import { useCallback, useState } from "react";
import { logActiveJTBDAction } from "@/lib/jtbdFeedback";
import {
  getHoroscopeScenarioMeta,
  getHoroscopeScenarioRoute,
  sanitizePersonalDayHref,
  type TodayCycleData,
} from "@/components/today/todayPageUtils";
import { narrativeString, narrativeStringArray } from "@/lib/todayNarrativeApi";
import { fetchTodayNarrativeCached } from "@/lib/todayNarrativeCache";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";

function slugToDeepenTopic(slug: string): "love" | "money" | "career" | "family" | "full_day" {
  if (slug === "love" || slug === "money" || slug === "career" || slug === "family") return slug;
  return "full_day";
}

export function TodayLifeSpheresSection({
  todayData,
  spheresNarrative = null,
  guideGenerationId = null,
}: {
  todayData: TodayCycleData;
  spheresNarrative?: Record<string, unknown> | null;
  guideGenerationId?: number | null;
}) {
  const dh = todayData.morning?.daily_horoscope;

  const [deepenBySlug, setDeepenBySlug] = useState<Record<string, string>>({});
  const [deepenLoadingSlug, setDeepenLoadingSlug] = useState<string | null>(null);
  const [expandedSlug, setExpandedSlug] = useState<string | null>(null);

  const tiesRaw = spheresNarrative?.scenario_tie_ins;
  const tieIns =
    tiesRaw && typeof tiesRaw === "object" && !Array.isArray(tiesRaw)
      ? (tiesRaw as Record<string, unknown>)
      : {};

  const fetchDeepen = useCallback(
    async (slug: string) => {
      const topic = slugToDeepenTopic(slug);
      setDeepenLoadingSlug(slug);
      try {
        const r = await fetchTodayNarrativeCached({
          target_date: todayData.date,
          surface: "deepen",
          deepen_topic: topic,
          parent_generation_id: guideGenerationId ?? undefined,
        });
        const body = narrativeString(r.payload?.body);
        const title = narrativeString(r.payload?.title);
        const bullets = narrativeStringArray(r.payload?.bullets, []);
        const closing = narrativeString(r.payload?.closing_line);
        const chunks: string[] = [];
        if (title) chunks.push(title);
        if (body) chunks.push(body);
        if (bullets.length) chunks.push(bullets.map((b) => `• ${b}`).join("\n"));
        if (closing) chunks.push(closing);
        const text = chunks.join("\n\n").trim() || RITUAL_COPY.lifeSpheresDeepenFallbackBody;
        setDeepenBySlug((prev) => ({ ...prev, [slug]: text }));
      } catch {
        setDeepenBySlug((prev) => ({
          ...prev,
          [slug]: RITUAL_COPY.lifeSpheresDeepenLoadError,
        }));
      } finally {
        setDeepenLoadingSlug(null);
      }
    },
    [todayData.date, guideGenerationId],
  );

  if (!dh) {
    return (
      <section style={{ marginBottom: "var(--orbit-space-xl)" }}>
        <div className="orbit-card todayflow-panel" style={{ padding: "1rem", borderRadius: "18px" }}>
          <p className="orbit-body-sm" style={{ margin: 0, color: "#6a5132", lineHeight: 1.6 }}>
            {RITUAL_COPY.lifeSpheresMorningRefreshHint}
          </p>
        </div>
      </section>
    );
  }

  return (
    <section id="life-spheres-section" style={{ marginBottom: "var(--orbit-space-xl)" }}>
      <style jsx>{`
        .today-sphere-item {
          transition: transform 180ms ease, box-shadow 220ms ease, border-color 220ms ease, background 220ms ease;
        }
        @media (hover: hover) and (pointer: fine) {
          .today-sphere-item:hover {
            transform: translateY(-1px);
          }
        }
      `}</style>
      <div
        style={{
          padding: "var(--orbit-space-lg)",
          borderRadius: "22px",
          border: "1px solid rgba(200, 154, 92, 0.3)",
          background: "linear-gradient(165deg, rgba(255,255,255,0.97) 0%, rgba(255,244,228,0.96) 100%)",
          boxShadow: "0 16px 34px rgba(110, 80, 38, 0.1)",
        }}
      >
        <div style={{ marginBottom: "0.85rem" }}>
          <h2 className="orbit-heading-3" style={{ margin: 0, fontSize: "1.1rem", color: "#5e4222" }}>
            {RITUAL_COPY.lifeSpheresHubTitle}
          </h2>
          <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#7a6242", lineHeight: 1.55 }}>
            {RITUAL_COPY.lifeSpheresHubLead}
          </p>
        </div>

        {Array.isArray(dh.scenarios) && dh.scenarios.length > 0 ? (
          <div>
            <div style={{ display: "grid", gap: "0.6rem" }}>
              {dh.scenarios.map((scenario: Record<string, unknown>, index: number) => {
                const slug = String(scenario?.slug || "");
                const meta = getHoroscopeScenarioMeta(slug);
                const route = getHoroscopeScenarioRoute(slug);
                const tieLine = narrativeString(tieIns[slug]);
                const deepenText = deepenBySlug[slug];
                const isOpen = expandedSlug === slug;
                return (
                  <div
                    className="today-sphere-item"
                    key={String(scenario?.slug || scenario?.title || index)}
                    style={{
                      borderRadius: "16px",
                      background: isOpen
                        ? "linear-gradient(160deg, rgba(255,255,255,0.98) 0%, rgba(255,248,236,0.96) 100%)"
                        : "rgba(255,255,255,0.86)",
                      border: `1px solid ${isOpen ? `${meta.accent}66` : `${meta.accent}30`}`,
                      overflow: "hidden",
                      boxShadow: isOpen ? "0 10px 24px rgba(105, 76, 38, 0.1)" : "none",
                    }}
                  >
                    <button
                      type="button"
                      onClick={() => setExpandedSlug((prev) => (prev === slug ? null : slug))}
                      style={{
                        width: "100%",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        gap: "0.6rem",
                        padding: "0.85rem 0.9rem",
                        border: "none",
                        background: "transparent",
                        cursor: "pointer",
                      }}
                    >
                      <div style={{ minWidth: 0, textAlign: "left" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.45rem" }}>
                          <span style={{ color: meta.accent, fontSize: "1rem", fontWeight: 700 }}>{meta.icon}</span>
                          <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#1f2937" }}>
                            {String(scenario?.title || RITUAL_COPY.lifeSpheresScenarioTitleFallback)}
                          </p>
                        </div>
                        <p className="orbit-body-xs" style={{ margin: "0.25rem 0 0", color: meta.accent }}>
                          {String(scenario?.focus || RITUAL_COPY.lifeSpheresFocusLineFallback)}
                        </p>
                      </div>
                      <span className="orbit-body-xs" style={{ color: "#7a6242", fontWeight: 700 }}>
                        {isOpen ? RITUAL_COPY.todayUiCollapseCta : RITUAL_COPY.todayUiOpenCta}
                      </span>
                    </button>

                    {isOpen ? (
                      <div style={{ padding: "0 0.9rem 0.9rem", borderTop: "1px solid rgba(201,168,115,0.18)" }}>
                        <p className="orbit-body-sm" style={{ margin: "0.55rem 0 0", color: "#6a5132", lineHeight: 1.65 }}>
                          {String(scenario?.summary || "")}
                        </p>
                        {tieLine ? (
                          <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#5e4222", lineHeight: 1.55, fontStyle: "italic" }}>
                            {tieLine}
                          </p>
                        ) : null}
                        {deepenText ? (
                          <p className="orbit-body-xs" style={{ margin: "0.5rem 0 0", color: "#4b5563", lineHeight: 1.65, whiteSpace: "pre-wrap" }}>
                            {deepenText}
                          </p>
                        ) : null}
                        <div style={{ marginTop: "0.55rem", display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
                          <button
                            type="button"
                            className="orbit-button orbit-button-secondary orbit-button-sm"
                            style={{ borderColor: `${meta.accent}44` }}
                            disabled={deepenLoadingSlug === slug}
                            onClick={() => void fetchDeepen(slug)}
                          >
                            {deepenLoadingSlug === slug
                              ? RITUAL_COPY.lifeSpheresDeepenLoading
                              : deepenText
                                ? RITUAL_COPY.lifeSpheresDeepenRefreshWhyCta
                                : RITUAL_COPY.lifeSpheresDeepenWhyCta}
                          </button>
                          <Link
                            href={sanitizePersonalDayHref(route.href)}
                            onClick={() => {
                              void logActiveJTBDAction("daily_horoscope_scenario_opened", {
                                scenario_slug: slug || "general",
                                source_surface: "today_life_spheres",
                                target_href: route.href,
                              }).catch(() => {});
                            }}
                            className="orbit-button orbit-button-primary orbit-button-sm"
                            style={{ textDecoration: "none" }}
                          >
                            {RITUAL_COPY.lifeSpheresScenarioActionCta}
                          </Link>
                        </div>
                      </div>
                    ) : null}
                    {slug === "love" && isOpen ? (
                      <p className="orbit-body-xs" style={{ margin: "0 0.9rem 0.8rem", color: "#7a6242", lineHeight: 1.55 }}>
                        {RITUAL_COPY.lifeSpheresLoveDeepCompatibilityHint}
                      </p>
                    ) : null}
                  </div>
                );
              })}
            </div>
          </div>
        ) : null}
      </div>
    </section>
  );
}
