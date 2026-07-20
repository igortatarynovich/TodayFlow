"use client";

import Link from "next/link";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { useState, useEffect } from "react";
import { getJson, postJson } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";

type NumerologyDailyInsight = {
  date: string;
  selection_status?: string;
  number: {
    title: string;
    value: number;
    reduced_value: number;
    is_master: boolean;
    summary: string;
  } | null;
};

type NumerologyExplanation = {
  number: {
    value: number | null;
    reduced_value: number;
    title: string;
    summary: string;
  };
  explanation: {
    meaning?: string;
    what_to_do?: string;
    what_to_avoid?: string;
  };
  date: string;
};

export default function NumerologyDayNumberPage() {
  const { isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<NumerologyDailyInsight | null>(null);
  const [explain, setExplain] = useState<NumerologyExplanation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    const loadDayNumber = async () => {
      try {
        setLoading(true);
        setError(null);
        // GET is gated (not_selected) — no number identity before reveal.
        const daily = await getJson<NumerologyDailyInsight>("/numerology/daily");
        setData(daily);
        setExplain(null);
      } catch (err) {
        console.error("Failed to load day number", err);
        setError("Не удалось загрузить число дня");
      } finally {
        setLoading(false);
      }
    };

    loadDayNumber();
  }, [isAuthenticated]);

  const handleReveal = async () => {
    try {
      const daily = await postJson<NumerologyDailyInsight>("/numerology/daily/reveal", {});
      setData(daily);
      setRevealed(true);
      if (isAuthenticated) {
        const detailed = await getJson<NumerologyExplanation>("/numerology/daily/explain").catch(() => null);
        setExplain(detailed);
      }
    } catch (err) {
      console.error("Failed to reveal day number", err);
      setError("Не удалось открыть число дня");
    }
  };

  if (loading) {
    return (
      <ProductPageScreen testId="numerology-day-number-page" title="Число дня" loading loadingLabel="Загрузка…" />
    );
  }

  if (error || !data) {
    return (
      <ProductPageScreen
        testId="numerology-day-number-page"
        title="Число дня"
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
        <section className={pl.panel}>
          <h2 className="orbit-display-sm">{error || "Ошибка загрузки"}</h2>
          <Link href="/numerology/life-path" className={pl.textLink}>
            Вернуться к нумерологии
          </Link>
        </section>
      </ProductPageScreen>
    );
  }

  const dayNumber = data.number?.value || data.number?.reduced_value;

  return (
    <ProductPageScreen
      testId="numerology-day-number-page"
      title="Число дня"
      subtitle={new Date(data.date).toLocaleDateString("ru-RU", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      })}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
        <div style={{ maxWidth: "760px", margin: "0 auto", padding: "0 var(--orbit-space-xl)" }}>
          <div className="orbit-card" style={{ padding: "var(--orbit-space-xl)", background: "#FAF9F7", textAlign: "center" }}>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.1em" }}>
              Ритуал дня
            </p>
            <div style={{ marginTop: "var(--orbit-space-md)", display: "grid", gap: "var(--orbit-space-md)", placeItems: "center" }}>
              {revealed ? (
                <div
                  style={{
                    width: "min(100%, 280px)",
                    aspectRatio: "1 / 1",
                    borderRadius: "32px",
                    background: "radial-gradient(circle at top, rgba(214,184,129,0.22), transparent 42%), linear-gradient(180deg, rgba(255,251,245,0.98), rgba(255,255,255,0.98))",
                    border: "1px solid rgba(195,154,92,0.22)",
                    display: "grid",
                    placeItems: "center",
                    boxShadow: "0 18px 40px rgba(15, 23, 42, 0.08)",
                    transition: "transform 320ms ease, opacity 320ms ease",
                  }}
                >
                  <div style={{ fontSize: "5rem", fontWeight: 600, color: "#0f172a", lineHeight: 1 }}>
                    {dayNumber}
                    {data.number?.is_master && <span style={{ fontSize: "2rem", verticalAlign: "super" }}>★</span>}
                  </div>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => void handleReveal()}
                  style={{
                    width: "min(100%, 280px)",
                    aspectRatio: "1 / 1",
                    borderRadius: "32px",
                    border: "1px solid rgba(195,154,92,0.28)",
                    background: "linear-gradient(180deg, rgba(124,90,51,0.96), rgba(76,53,31,0.98))",
                    color: "#fff7ed",
                    boxShadow: "0 18px 40px rgba(95, 67, 35, 0.16)",
                    cursor: "pointer",
                    display: "grid",
                    placeItems: "center",
                    padding: "1.2rem",
                    textAlign: "center",
                  }}
                >
                  <div style={{ display: "grid", gap: "0.6rem" }}>
                    <p className="orbit-body-xs" style={{ margin: 0, color: "rgba(255,247,237,0.78)", textTransform: "uppercase", letterSpacing: "0.12em" }}>
                      Число дня
                    </p>
                    <div style={{ fontSize: "2.4rem", lineHeight: 1 }}>✦</div>
                    <p className="orbit-body-sm" style={{ margin: 0, lineHeight: 1.7, color: "#fff7ed" }}>
                      Открой число, когда будешь готов увидеть основной ритм сегодняшнего дня.
                    </p>
                  </div>
                </button>
              )}

              <p className="orbit-body" style={{ fontSize: "1.125rem", lineHeight: 1.7, color: "#334155", marginBottom: 0 }}>
                {revealed ? (data.number?.title || "Ритм дня") : "Сегодняшний ритм ещё не открыт"}
              </p>
              <p className="orbit-body-sm" style={{ color: "#64748b", lineHeight: 1.6, maxWidth: "32rem", margin: 0 }}>
                {revealed
                  ? data.number?.summary || ""
                  : "Сначала открой число дня, потом считай, что оно усиливает и чего сегодня лучше не перегружать."}
              </p>
            </div>
          </div>
        </div>

      {!revealed ? (
        <section style={{ paddingTop: "var(--orbit-space-xl)", paddingBottom: "var(--orbit-space-2xl)", background: "#ffffff" }}>
          <div style={{ maxWidth: "760px", margin: "0 auto", padding: "0 var(--orbit-space-xl)" }}>
            <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)", background: "#fffaf3", border: "1px solid rgba(195,154,92,0.18)" }}>
              <p className="orbit-body-sm" style={{ margin: 0, color: "#6f573a", lineHeight: 1.7 }}>
                Число дня лучше читать как короткий ежедневный ритуал: открыть символ, почувствовать темп и только потом переходить к трактовке и действиям.
              </p>
            </div>
          </div>
        </section>
      ) : null}

      {revealed && explain && (
        <section style={{ paddingTop: "var(--orbit-space-2xl)", paddingBottom: "var(--orbit-space-4xl)", background: "#FAF9F7" }}>
          <div style={{ maxWidth: "760px", margin: "0 auto", padding: "0 var(--orbit-space-xl)", display: "grid", gap: "var(--orbit-space-md)" }}>
            {explain.explanation.meaning && (
              <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)", background: "#fff" }}>
                <h2 className="orbit-heading-2" style={{ marginBottom: "var(--orbit-space-sm)" }}>Смысл для тебя</h2>
                <p className="orbit-body-sm" style={{ margin: 0, lineHeight: 1.6, color: "#334155" }}>{explain.explanation.meaning}</p>
              </div>
            )}
            <div style={{ display: "grid", gap: "var(--orbit-space-md)", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))" }}>
              <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)", background: "#f0fdf4", border: "1px solid #86efac" }}>
                <h3 className="orbit-heading-3" style={{ marginBottom: "var(--orbit-space-sm)", color: "#166534" }}>Что делать</h3>
                <p className="orbit-body-sm" style={{ margin: 0, lineHeight: 1.6, color: "#334155" }}>
                  {explain.explanation.what_to_do || "Поддерживай основной фокус дня короткими действиями."}
                </p>
              </div>
              <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)", background: "#fef2f2", border: "1px solid #fca5a5" }}>
                <h3 className="orbit-heading-3" style={{ marginBottom: "var(--orbit-space-sm)", color: "#991b1b" }}>Чего избегать</h3>
                <p className="orbit-body-sm" style={{ margin: 0, lineHeight: 1.6, color: "#334155" }}>
                  {explain.explanation.what_to_avoid || "Не распыляйся на второстепенные задачи."}
                </p>
              </div>
            </div>
          </div>
        </section>
      )}

      <section style={{ paddingTop: "var(--orbit-space-xl)", paddingBottom: "var(--orbit-space-4xl)", textAlign: "center", background: "#FAF9F7" }}>
        <div style={{ maxWidth: "760px", margin: "0 auto", padding: "0 var(--orbit-space-xl)", display: "flex", gap: "var(--orbit-space-sm)", justifyContent: "center", flexWrap: "wrap" }}>
          <Link href="/profile?focus=numerology" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none" }}>
            Числа внутри профиля
          </Link>
          <Link href="/today?slot=morning" className="orbit-button orbit-button-primary" style={{ textDecoration: "none" }}>
            Применить в Today
          </Link>
        </div>
      </section>
    </ProductPageScreen>
  );
}
