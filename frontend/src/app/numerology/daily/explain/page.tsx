"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { useAuth } from "@/lib/useAuth";
import { getJson } from "@/lib/api";
import Link from "next/link";

type NumerologyExplanation = {
  number: {
    value: number | null;
    reduced_value: number;
    title: string;
    summary: string;
  };
  explanation: {
    meaning: string;
    what_to_do: string;
    what_to_avoid: string;
    possible_events: string;
    how_day_looks: string;
    why_this_number: string;
  };
  date: string;
};

function NumerologyDailyExplainContent() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const searchParams = useSearchParams();
  const date = searchParams?.get("date");
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<NumerologyExplanation | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    const loadExplanation = async () => {
      try {
        setLoading(true);
        setError(null);
        const url = date ? `/numerology/daily/explain?date=${date}` : "/numerology/daily/explain";
        const response = await getJson<NumerologyExplanation>(url);
        setData(response);
      } catch (err: any) {
        console.error("Failed to load numerology explanation", err);
        setError(err?.message || "Не удалось загрузить объяснение");
      } finally {
        setLoading(false);
      }
    };

    loadExplanation();
  }, [isAuthenticated, date]);

  if (authLoading || loading) {
    return (
      <ProductPageScreen testId="numerology-daily-explain-page" title="Объяснение числа дня" loading loadingLabel="Загрузка…" />
    );
  }

  if (!isAuthenticated) {
    return (
      <ProductPageScreen
        testId="numerology-daily-explain-page"
        title="Объяснение числа дня"
        guest={{ message: "Войдите, чтобы увидеть объяснение", ctaHref: "/auth", ctaLabel: "Войти" }}
      />
    );
  }

  if (error || !data) {
    return (
      <ProductPageScreen testId="numerology-daily-explain-page" title="Объяснение числа дня" contentClassName={`${pl.content} ${pl.legacyHost}`}>
        <section className={pl.panel} style={{ textAlign: "center" }}>
          <h1 className="orbit-display-sm">{error || "Ошибка загрузки"}</h1>
          <Link href="/numerology/day-number" className={pl.textLink}>
            Вернуться к числу дня
          </Link>
        </section>
      </ProductPageScreen>
    );
  }

  return (
    <ProductPageScreen
      testId="numerology-daily-explain-page"
      title="Объяснение числа дня"
      hideHeader
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <section style={{ paddingTop: "var(--orbit-space-2xl)", paddingBottom: "var(--orbit-space-2xl)", textAlign: "center" }}>
        <div style={{
          maxWidth: "800px",
          margin: "0 auto",
          padding: "0 var(--orbit-space-xl)"
        }}>
          <Link href="/numerology/day-number" className="orbit-body-sm" style={{
            color: "var(--orbit-color-primary)",
            textDecoration: "none",
            display: "inline-block",
            marginBottom: "var(--orbit-space-lg)"
          }}>
            ← К числу дня
          </Link>
          <h1 className="orbit-display" style={{
            fontSize: "clamp(2rem, 4vw, 3rem)",
            lineHeight: 1.2,
            marginBottom: "var(--orbit-space-md)",
            color: "#0f172a",
            fontWeight: 500
          }}>
            Объяснение числа дня {data.number.value || data.number.reduced_value}
          </h1>
          <p className="orbit-body-sm" style={{
            color: "#64748b"
          }}>
            {new Date(data.date).toLocaleDateString('ru-RU', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </p>
        </div>
      </section>

      {/* Explanation */}
      <section style={{
        paddingTop: "var(--orbit-space-2xl)",
        paddingBottom: "var(--orbit-space-4xl)",
        background: "#ffffff"
      }}>
        <div style={{
          maxWidth: "800px",
          margin: "0 auto",
          padding: "0 var(--orbit-space-xl)"
        }}>
          {/* Meaning */}
          {data.explanation.meaning && (
            <div className="orbit-card" style={{
              padding: "var(--orbit-space-xl)",
              marginBottom: "var(--orbit-space-lg)",
              background: "#FAF9F7"
            }}>
              <h2 className="orbit-heading-2" style={{
                marginBottom: "var(--orbit-space-md)",
                color: "#0f172a"
              }}>
                Что это значит
              </h2>
              <p className="orbit-body" style={{
                lineHeight: 1.7,
                color: "#334155"
              }}>
                {data.explanation.meaning}
              </p>
            </div>
          )}

          {/* What to do */}
          {data.explanation.what_to_do && (
            <div className="orbit-card" style={{
              padding: "var(--orbit-space-xl)",
              marginBottom: "var(--orbit-space-lg)",
              background: "#f0fdf4",
              border: "1px solid #86efac"
            }}>
              <h2 className="orbit-heading-2" style={{
                marginBottom: "var(--orbit-space-md)",
                color: "#166534"
              }}>
                Что делать
              </h2>
              <p className="orbit-body" style={{
                lineHeight: 1.7,
                color: "#334155"
              }}>
                {data.explanation.what_to_do}
              </p>
            </div>
          )}

          {/* What to avoid */}
          {data.explanation.what_to_avoid && (
            <div className="orbit-card" style={{
              padding: "var(--orbit-space-xl)",
              marginBottom: "var(--orbit-space-lg)",
              background: "#fef2f2",
              border: "1px solid #fca5a5"
            }}>
              <h2 className="orbit-heading-2" style={{
                marginBottom: "var(--orbit-space-md)",
                color: "#991b1b"
              }}>
                Чего избегать
              </h2>
              <p className="orbit-body" style={{
                lineHeight: 1.7,
                color: "#334155"
              }}>
                {data.explanation.what_to_avoid}
              </p>
            </div>
          )}

          {/* Possible events */}
          {data.explanation.possible_events && (
            <div className="orbit-card" style={{
              padding: "var(--orbit-space-xl)",
              marginBottom: "var(--orbit-space-lg)",
              background: "#fefce8",
              border: "1px solid #fde047"
            }}>
              <h2 className="orbit-heading-2" style={{
                marginBottom: "var(--orbit-space-md)",
                color: "#854d0e"
              }}>
                Возможные события
              </h2>
              <p className="orbit-body" style={{
                lineHeight: 1.7,
                color: "#334155"
              }}>
                {data.explanation.possible_events}
              </p>
            </div>
          )}

          {/* How day looks */}
          {data.explanation.how_day_looks && (
            <div className="orbit-card" style={{
              padding: "var(--orbit-space-xl)",
              marginBottom: "var(--orbit-space-lg)",
              background: "#f0f9ff",
              border: "1px solid #7dd3fc"
            }}>
              <h2 className="orbit-heading-2" style={{
                marginBottom: "var(--orbit-space-md)",
                color: "#0c4a6e"
              }}>
                Как выглядит день
              </h2>
              <p className="orbit-body" style={{
                lineHeight: 1.7,
                color: "#334155"
              }}>
                {data.explanation.how_day_looks}
              </p>
            </div>
          )}

          {/* Why this number */}
          {data.explanation.why_this_number && (
            <div className="orbit-card" style={{
              padding: "var(--orbit-space-xl)",
              marginBottom: "var(--orbit-space-lg)",
              background: "#faf5ff",
              border: "1px solid #c4b5fd"
            }}>
              <h2 className="orbit-heading-2" style={{
                marginBottom: "var(--orbit-space-md)",
                color: "#6b21a8"
              }}>
                Почему это число важно
              </h2>
              <p className="orbit-body" style={{
                lineHeight: 1.7,
                color: "#334155"
              }}>
                {data.explanation.why_this_number}
              </p>
            </div>
          )}
        </div>
      </section>
    </ProductPageScreen>
  );
}

export default function NumerologyDailyExplainPage() {
  return (
    <Suspense fallback={
      <ProductPageScreen testId="numerology-daily-explain-page" title="Объяснение числа дня" loading loadingLabel="Загрузка…" />
    }>
      <NumerologyDailyExplainContent />
    </Suspense>
  );
}
