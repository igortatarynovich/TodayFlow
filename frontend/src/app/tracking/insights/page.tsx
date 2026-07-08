"use client";

import { useState, useEffect, useMemo } from "react";
import { useAuth } from "@/lib/useAuth";
import { DsButton } from "@/design-system";
import { getJson, postJson } from "@/lib/api";
import { useToast } from "@/components/ToastProvider";
import { getLocale } from "@/lib/i18n";
import {
  flowTrackerChromeBundle,
  type FlowTrackerChromeBundle,
} from "@/components/today/flowPracticesMainTabChrome";
import { ProductAuxWebScreen } from "@/components/product-ui/ProductAuxWebScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";

type AutoInsight = {
  id: string;
  date: string;
  type: string;
  insight_text: string;
  data_points: Record<string, unknown>;
  confidence?: "low" | "medium" | "high";
  created_at: string;
};

function tpl(s: string, vars: Record<string, string | number>): string {
  return s.replace(/\{\{(\w+)\}\}/g, (_, k) => String(vars[k] ?? ""));
}

function autoInsightTypeLabel(fc: FlowTrackerChromeBundle, type: string): string {
  const m: Record<string, string> = {
    streak: fc.trackingInsightTypeStreak,
    pattern: fc.trackingInsightTypePattern,
    shift: fc.trackingInsightTypeShift,
    correlation: fc.trackingInsightTypeCorrelation,
    weekend_pattern: fc.trackingInsightTypeWeekendPattern,
    signal_closure: fc.trackingInsightTypeSignalClosure,
    signal_clarity: fc.trackingInsightTypeSignalClarity,
    signal_focus: fc.trackingInsightTypeSignalFocus,
  };
  return m[type] ?? type;
}

function insightCardClass(confidence: "low" | "medium" | "high"): string {
  if (confidence === "high") return `${pl.insightCard} ${pl.insightCardHigh}`;
  if (confidence === "low") return `${pl.insightCard} ${pl.insightCardLow}`;
  return `${pl.insightCard} ${pl.insightCardMedium}`;
}

export default function InsightsPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const toast = useToast();
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState<AutoInsight[]>([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split("T")[0]);
  const [generating, setGenerating] = useState(false);

  const locale = getLocale() === "ru" ? "ru" : "en";
  const fc = useMemo(() => flowTrackerChromeBundle(locale), [locale]);
  const dateLocaleTag = locale === "ru" ? "ru-RU" : "en-US";

  useEffect(() => {
    if (!isAuthenticated) return;
    const loadInsights = async () => {
      try {
        setLoading(true);
        const data = await getJson<AutoInsight[]>(`/tracking/insights?date=${selectedDate}`);
        setInsights(data);
      } catch (err) {
        console.error("Error loading insights:", err);
      } finally {
        setLoading(false);
      }
    };
    loadInsights();
  }, [isAuthenticated, selectedDate]);

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      await postJson<AutoInsight>("/tracking/insights/generate", { date: selectedDate });
      const data = await getJson<AutoInsight[]>(`/tracking/insights?date=${selectedDate}`);
      setInsights(data);
    } catch (err: unknown) {
      console.error("Error generating insight:", err);
      const e = err as { message?: string; detail?: string };
      const message = e?.message || e?.detail || fc.insightsGenerateErrorFallback;
      toast.error(message);
    } finally {
      setGenerating(false);
    }
  };

  if (authLoading || loading) {
    return (
      <ProductAuxWebScreen title={fc.trackingInsightsPageTitle} loading loadingLabel={fc.trackingInsightsPageLead} />
    );
  }

  if (!isAuthenticated) {
    return (
      <ProductAuxWebScreen
        title={fc.trackingInsightsPageTitle}
        guest={{
          message: fc.trackingInsightsLoginPrompt,
          ctaHref: "/auth?redirect=/tracking/insights",
          ctaLabel: locale === "ru" ? "Войти" : "Sign in",
        }}
      />
    );
  }

  return (
    <ProductAuxWebScreen
      testId="tracking-insights-page"
      title={fc.trackingInsightsPageTitle}
      subtitle={fc.trackingInsightsPageLead}
      railTitle={locale === "ru" ? "Автоинсайты" : "Auto insights"}
      railHint={
        locale === "ru"
          ? "Паттерны из дневника, ритуалов и трекеров — с уровнем уверенности."
          : "Patterns from diary, rituals, and trackers — with confidence level."
      }
    >
      <div className={pl.fieldRow}>
        <div style={{ flex: "1 1 12rem", maxWidth: "20rem" }}>
          <label className={pl.fieldLabel} htmlFor="insights-date">
            {fc.trackingFormDateLabel}
          </label>
          <input
            id="insights-date"
            type="date"
            className={pl.fieldInput}
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
          />
        </div>
        <DsButton onClick={handleGenerate} disabled={generating}>
          {generating ? fc.insightsGeneratingShort : fc.generateInsight}
        </DsButton>
      </div>

      {insights.length === 0 ? (
        <div className={pl.emptyState}>
          <p>{fc.trackingInsightsEmptyTitle}</p>
          <p className={pl.hubCardDesc} style={{ marginTop: "0.5rem" }}>
            {fc.trackingInsightsEmptyHint}
          </p>
        </div>
      ) : (
        <div className={pl.insightList}>
          {insights.map((insight) => {
            const confidence = insight.confidence || "medium";
            const confidenceLabels = {
              low: fc.trackingInsightConfidenceLow,
              medium: fc.trackingInsightConfidenceMedium,
              high: fc.trackingInsightConfidenceHigh,
            };

            return (
              <article key={insight.id} className={insightCardClass(confidence)}>
                <div className={pl.insightMeta}>
                  <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
                    <span className={pl.insightType}>{autoInsightTypeLabel(fc, insight.type)}</span>
                    <span className={`${v2.chip} ${pl.insightType}`}>{confidenceLabels[confidence]}</span>
                  </div>
                  <span className={pl.hubCardDesc}>
                    {new Date(insight.date).toLocaleDateString(dateLocaleTag)}
                  </span>
                </div>
                <p className={pl.insightBody}>{insight.insight_text}</p>

                {insight.type === "correlation" && insight.data_points ? (
                  <div className={pl.insightData}>
                    <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
                      {typeof insight.data_points.avg_mood === "number" ? (
                        <div>
                          <strong>{fc.trackingInsightDataAvgMood}</strong> {String(insight.data_points.avg_mood)}/5
                        </div>
                      ) : null}
                      {typeof insight.data_points.data_points_count === "number" ? (
                        <div>
                          <strong>{fc.trackingInsightDataEntries}</strong>{" "}
                          {String(insight.data_points.data_points_count)}
                        </div>
                      ) : null}
                    </div>
                  </div>
                ) : null}

                {insight.type === "weekend_pattern" && insight.data_points ? (
                  <div className={pl.insightData}>
                    <div>
                      <strong>{fc.trackingInsightDataWeekendEntries}</strong>{" "}
                      {typeof insight.data_points.weekend_percentage === "number"
                        ? `${insight.data_points.weekend_percentage}%`
                        : ""}{" "}
                      (
                      {tpl(fc.trackingInsightDataTotalCountSuffix, {
                        n:
                          typeof insight.data_points.total_entries === "number"
                            ? insight.data_points.total_entries
                            : 0,
                      })}
                      )
                    </div>
                  </div>
                ) : null}

                {(insight.type === "signal_closure" ||
                  insight.type === "signal_clarity" ||
                  insight.type === "signal_focus") &&
                insight.data_points ? (
                  <div className={pl.insightData}>
                    <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
                      {typeof insight.data_points.days_reviewed === "number" ? (
                        <div>
                          <strong>{fc.trackingInsightDataDaysReviewed}</strong>{" "}
                          {String(insight.data_points.days_reviewed)}
                        </div>
                      ) : null}
                      {typeof insight.data_points.ritual_feedback_yes_days === "number" ? (
                        <div>
                          <strong>{fc.trackingInsightDataGatheredDays}</strong>{" "}
                          {String(insight.data_points.ritual_feedback_yes_days)}
                        </div>
                      ) : null}
                      {typeof insight.data_points.ritual_feedback_no_days === "number" ? (
                        <div>
                          <strong>{fc.trackingInsightDataUngatheredDays}</strong>{" "}
                          {String(insight.data_points.ritual_feedback_no_days)}
                        </div>
                      ) : null}
                      {typeof insight.data_points.unclear_decision_days === "number" ? (
                        <div>
                          <strong>{fc.trackingInsightDataUnclearDecisions}</strong>{" "}
                          {String(insight.data_points.unclear_decision_days)}
                        </div>
                      ) : null}
                      {typeof insight.data_points.clear_decision_days === "number" ? (
                        <div>
                          <strong>{fc.trackingInsightDataClearDecisions}</strong>{" "}
                          {String(insight.data_points.clear_decision_days)}
                        </div>
                      ) : null}
                      {typeof insight.data_points.dominant_focus === "string" ? (
                        <div>
                          <strong>{fc.trackingInsightDataDominantFocus}</strong>{" "}
                          {String(insight.data_points.dominant_focus)}
                        </div>
                      ) : null}
                      {typeof insight.data_points.dominant_focus_count === "number" ? (
                        <div>
                          <strong>{fc.trackingInsightDataRepeatCount}</strong>{" "}
                          {String(insight.data_points.dominant_focus_count)}
                        </div>
                      ) : null}
                    </div>
                  </div>
                ) : null}
              </article>
            );
          })}
        </div>
      )}
    </ProductAuxWebScreen>
  );
}
