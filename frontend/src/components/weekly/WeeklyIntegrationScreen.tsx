"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import { getJson, postJson } from "@/lib/api";
import { useToast } from "@/components/ToastProvider";
import { formatWeeklyRhythmStoryLine } from "@/components/today/flowPracticesMainTabChrome";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";

type WeeklyIntegration = {
  week_start: string;
  week_end: string;
  integration_text: string;
  data_points: {
    completion_rate?: number;
    signals_days?: number;
    signals_completion_rate?: number;
    ritual_feedback_yes_days?: number;
    ritual_feedback_no_days?: number;
    unclear_decision_days?: number;
    dominant_question_focus?: string | null;
    where_held?: string;
    where_released?: string | null;
    [key: string]: unknown;
  };
  created_at: string;
};

function getWeekStart(date: Date): string {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  const monday = new Date(d.setDate(diff));
  return monday.toISOString().split('T')[0];
}

export default function WeeklyIntegrationScreen() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const toast = useToast();
  const [loading, setLoading] = useState(true);
  const [integration, setIntegration] = useState<WeeklyIntegration | null>(null);
  const [selectedWeek, setSelectedWeek] = useState(getWeekStart(new Date()));
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) return;
    const loadIntegration = async () => {
      try {
        setLoading(true);
        const data = await getJson<WeeklyIntegration | null>(`/tracking/weekly/${selectedWeek}`);
        setIntegration(data ?? null);
      } catch (err: unknown) {
        const e = err as { status?: number };
        if (e?.status === 404) {
          setIntegration(null);
        } else {
          console.error("Error loading integration:", err);
        }
      } finally {
        setLoading(false);
      }
    };
    loadIntegration();
  }, [isAuthenticated, selectedWeek]);

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      const newIntegration = await postJson<WeeklyIntegration>("/tracking/weekly/generate", { week_start: selectedWeek });
      setIntegration(newIntegration);
    } catch (err: any) {
      console.error("Error generating integration:", err);
      const message = err?.message || err?.detail || "Ошибка при генерации недельной интеграции";
      toast.error(message);
    } finally {
      setGenerating(false);
    }
  };

  const getWeekEnd = (weekStart: string): string => {
    const start = new Date(weekStart);
    const end = new Date(start);
    end.setDate(end.getDate() + 6);
    return end.toISOString().split('T')[0];
  };

  const describeFocus = (value?: string | null) => {
    if (!value) return "не выделен";
    const text = value.toLowerCase();
    if (text.includes("деньг")) return "деньги";
    if (text.includes("отнош")) return "отношения";
    if (text.includes("работ")) return "работа";
    if (text.includes("состоя") || text.includes("энерг")) return "состояние";
    return value;
  };

  if (authLoading || loading) {
    return (
      <ProductPageScreen
        testId="weekly-integration-page"
        title="Недельная интеграция"
        loading
        loadingLabel="Загрузка…"
        railTitle="Неделя"
        railHint="Короткий итог: что повторялось и куда держать фокус."
      />
    );
  }

  if (!isAuthenticated) {
    return (
      <ProductPageScreen
        testId="weekly-integration-page"
        title="Недельная интеграция"
        subtitle="Короткий итог недели: что повторялось и на чём лучше держать фокус дальше."
        railTitle="Доступ"
        railHint="Сначала собери свой Today — потом итоги недели сохранятся в аккаунте."
      >
        <div style={{ display: "grid", gap: "0.85rem", justifyItems: "start" }}>
          <Link href="/onboarding/welcome?fresh=1" className="orbit-button orbit-button-primary">
            Создать мой Today
          </Link>
          <Link href="/auth?mode=login&redirect=/weekly/integration" className="orbit-body-sm" style={{ color: "#78716c", textDecoration: "underline" }}>
            Уже есть аккаунт? Войти
          </Link>
        </div>
      </ProductPageScreen>
    );
  }

  return (
    <ProductPageScreen
      testId="weekly-integration-page"
      title="Недельная интеграция"
      subtitle="Короткий итог недели: что повторялось и на чём лучше держать фокус дальше."
      railTitle="Неделя"
      railHint="Собери итог после 2–3 отмеченных дней — ритм станет яснее."
      contentClassName={pl.content}
    >
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1.25rem" }}>
          <Link href="/weekly" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none" }}>
            ← Вернуться к недельному фокусу
          </Link>
        </div>

        <div style={{ marginBottom: "2rem", display: "flex", gap: "1rem", alignItems: "flex-end" }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Неделя (начало недели)</label>
            <input
              type="date"
              value={selectedWeek}
              onChange={(e) => setSelectedWeek(e.target.value)}
              style={{ padding: "0.75rem", fontSize: "1rem", border: "1px solid #ddd", borderRadius: "4px", width: "100%", maxWidth: "300px" }}
            />
            <p style={{ fontSize: "0.9rem", color: "#666", marginTop: "0.5rem" }}>
              {new Date(selectedWeek).toLocaleDateString('ru-RU')} — {new Date(getWeekEnd(selectedWeek)).toLocaleDateString('ru-RU')}
            </p>
          </div>
          <button
            onClick={handleGenerate}
            disabled={generating}
            style={{ padding: "0.75rem 2rem", fontSize: "1rem", background: "#667eea", color: "white", border: "none", borderRadius: "4px", cursor: generating ? "not-allowed" : "pointer", opacity: generating ? 0.6 : 1 }}
          >
            {generating ? "Собираем неделю…" : "Собрать итог недели"}
          </button>
        </div>

        {!integration ? (
          <div style={{ background: "#f9f9f9", padding: "3rem", borderRadius: "8px", textAlign: "center", color: "#666" }}>
            <p>Итога за эту неделю ещё нет.</p>
            <p style={{ marginTop: "0.5rem", fontSize: "0.9rem" }}>
              Отметь хотя бы 2–3 дня и собери короткий итог — что держало ритм.
            </p>
          </div>
        ) : (
          <div style={{ background: "#fff", padding: "3rem", borderRadius: "12px", border: "2px solid #667eea", boxShadow: "0 4px 12px rgba(102, 126, 234, 0.1)" }}>
            <div style={{ marginBottom: "1.5rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h2 style={{ fontSize: "1.5rem", margin: 0 }}>
                Неделя {new Date(integration.week_start).toLocaleDateString('ru-RU')} — {new Date(getWeekEnd(integration.week_start)).toLocaleDateString('ru-RU')}
              </h2>
              <span style={{ fontSize: "0.9rem", color: "#999" }}>{new Date(integration.created_at).toLocaleDateString('ru-RU')}</span>
            </div>
            <p style={{ fontSize: "1.2rem", lineHeight: "1.8", color: "#333", whiteSpace: "pre-line" }}>{integration.integration_text}</p>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.85rem", marginTop: "2rem" }}>
              <div style={{ padding: "1rem", borderRadius: "12px", background: "#f7f3eb", border: "1px solid rgba(191,151,95,0.22)" }}>
                <p style={{ margin: 0, fontSize: "0.78rem", color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.06em" }}>Ритм недели</p>
                <p style={{ margin: "0.35rem 0 0", fontSize: "1.05rem", fontWeight: 600, lineHeight: 1.45, color: "#6d4f29" }}>
                  {formatWeeklyRhythmStoryLine("ru", integration.data_points.completion_rate || 0)}
                </p>
                <p style={{ margin: "0.25rem 0 0", fontSize: "0.85rem", color: "#8a7760" }}>
                  {integration.data_points.signals_days || 0} дней с отметками на картах
                </p>
              </div>
              <div style={{ padding: "1rem", borderRadius: "12px", background: "#f7f3eb", border: "1px solid rgba(191,151,95,0.22)" }}>
                <p style={{ margin: 0, fontSize: "0.78rem", color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.06em" }}>Сигналы дня</p>
                <p style={{ margin: "0.35rem 0 0", fontSize: "1.45rem", fontWeight: 700, color: "#6d4f29" }}>
                  {integration.data_points.signals_days || 0}/7
                </p>
                <p style={{ margin: "0.25rem 0 0", fontSize: "0.85rem", color: "#8a7760" }}>дней с живым откликом</p>
              </div>
              <div style={{ padding: "1rem", borderRadius: "12px", background: "#f7f3eb", border: "1px solid rgba(191,151,95,0.22)" }}>
                <p style={{ margin: 0, fontSize: "0.78rem", color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.06em" }}>Собранность</p>
                <p style={{ margin: "0.35rem 0 0", fontSize: "1.45rem", fontWeight: 700, color: "#6d4f29" }}>
                  {integration.data_points.ritual_feedback_yes_days || 0}
                </p>
                <p style={{ margin: "0.25rem 0 0", fontSize: "0.85rem", color: "#8a7760" }}>дней собраны до конца</p>
              </div>
              <div style={{ padding: "1rem", borderRadius: "12px", background: "#f7f3eb", border: "1px solid rgba(191,151,95,0.22)" }}>
                <p style={{ margin: 0, fontSize: "0.78rem", color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.06em" }}>Неясность</p>
                <p style={{ margin: "0.35rem 0 0", fontSize: "1.45rem", fontWeight: 700, color: "#6d4f29" }}>
                  {integration.data_points.unclear_decision_days || 0}
                </p>
                <p style={{ margin: "0.25rem 0 0", fontSize: "0.85rem", color: "#8a7760" }}>дней с unresolved выбором</p>
              </div>
            </div>

            <div style={{ marginTop: "1rem", padding: "1rem 1.1rem", borderRadius: "12px", background: "#fbf8f2", border: "1px solid rgba(191,151,95,0.18)" }}>
              <p style={{ margin: 0, fontSize: "0.82rem", color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                Что неделя пыталась показать
              </p>
              <p style={{ margin: "0.45rem 0 0", fontSize: "0.98rem", color: "#5f4323", lineHeight: 1.6 }}>
                Главный повторяющийся фокус: <strong>{describeFocus(integration.data_points.dominant_question_focus as string | null | undefined)}</strong>.
                {typeof integration.data_points.ritual_feedback_no_days === "number" && integration.data_points.ritual_feedback_no_days > 0
                  ? ` Несобранных дней: ${integration.data_points.ritual_feedback_no_days}.`
                  : " Срывов по закрытию дня почти не было."}
              </p>
            </div>
          </div>
        )}
    </ProductPageScreen>
  );
}
