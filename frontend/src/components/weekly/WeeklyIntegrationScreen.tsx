"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/useAuth";
import { getJson, postJson } from "@/lib/api";
import { useToast } from "@/components/ToastProvider";
import { formatWeeklyRhythmStoryLine } from "@/components/today/flowPracticesMainTabChrome";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import { DsBody, DsButton, DsCard, DsCaption, DsTitle } from "@/design-system";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import w from "./weeklyIntegration.module.css";

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
  return monday.toISOString().split("T")[0];
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
      const newIntegration = await postJson<WeeklyIntegration>("/tracking/weekly/generate", {
        week_start: selectedWeek,
      });
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
    return end.toISOString().split("T")[0];
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
      />
    );
  }

  if (!isAuthenticated) {
    return (
      <ProductPageScreen
        testId="weekly-integration-page"
        title="Недельная интеграция"
        subtitle="Короткий итог недели: что повторялось и на чём лучше держать фокус дальше."
      >
        <div className={w.authStack}>
          <DsButton variant="primary" href="/onboarding/welcome?fresh=1">
            Создать мой Today
          </DsButton>
          <DsButton variant="ghost" href="/auth?mode=login&redirect=/weekly/integration">
            Уже есть аккаунт? Войти
          </DsButton>
        </div>
      </ProductPageScreen>
    );
  }

  return (
    <ProductPageScreen
      testId="weekly-integration-page"
      title="Недельная интеграция"
      subtitle="Короткий итог недели: что повторялось и на чём лучше держать фокус дальше."
      contentClassName={pl.content}
    >
      <div className={w.toolbar}>
        <DsButton variant="secondary" href="/weekly">
          ← Вернуться к недельному фокусу
        </DsButton>
      </div>

      <div className={w.controls}>
        <div className={w.field}>
          <label className={w.fieldLabel} htmlFor="weekly-integration-week">
            Неделя (начало недели)
          </label>
          <input
            id="weekly-integration-week"
            className={w.dateInput}
            type="date"
            value={selectedWeek}
            onChange={(e) => setSelectedWeek(e.target.value)}
          />
          <p className={w.rangeHint}>
            {new Date(selectedWeek).toLocaleDateString("ru-RU")} —{" "}
            {new Date(getWeekEnd(selectedWeek)).toLocaleDateString("ru-RU")}
          </p>
        </div>
        <DsButton variant="primary" onClick={handleGenerate} disabled={generating}>
          {generating ? "Собираем неделю…" : "Собрать итог недели"}
        </DsButton>
      </div>

      {!integration ? (
        <DsCard variant="outline" className={w.emptyShell}>
          <DsBody muted>Итога за эту неделю ещё нет.</DsBody>
          <DsCaption muted>Отметь хотя бы 2–3 дня и собери короткий итог — что держало ритм.</DsCaption>
        </DsCard>
      ) : (
        <DsCard variant="elevated" className={w.resultShell}>
          <div className={w.resultHead}>
            <DsTitle as="h2">
              Неделя {new Date(integration.week_start).toLocaleDateString("ru-RU")} —{" "}
              {new Date(getWeekEnd(integration.week_start)).toLocaleDateString("ru-RU")}
            </DsTitle>
            <DsCaption muted>{new Date(integration.created_at).toLocaleDateString("ru-RU")}</DsCaption>
          </div>
          <DsBody className={w.story}>{integration.integration_text}</DsBody>

          <div className={w.statGrid}>
            <div className={w.statTile}>
              <p className={w.statLabel}>Ритм недели</p>
              <p className={w.statValueSm}>
                {formatWeeklyRhythmStoryLine("ru", integration.data_points.completion_rate || 0)}
              </p>
              <p className={w.statHint}>
                {integration.data_points.signals_days || 0} дней с отметками на картах
              </p>
            </div>
            <div className={w.statTile}>
              <p className={w.statLabel}>Сигналы дня</p>
              <p className={w.statValue}>{integration.data_points.signals_days || 0}/7</p>
              <p className={w.statHint}>дней с живым откликом</p>
            </div>
            <div className={w.statTile}>
              <p className={w.statLabel}>Собранность</p>
              <p className={w.statValue}>{integration.data_points.ritual_feedback_yes_days || 0}</p>
              <p className={w.statHint}>дней собраны до конца</p>
            </div>
            <div className={w.statTile}>
              <p className={w.statLabel}>Неясность</p>
              <p className={w.statValue}>{integration.data_points.unclear_decision_days || 0}</p>
              <p className={w.statHint}>дней с unresolved выбором</p>
            </div>
          </div>

          <div className={w.focusPanel}>
            <p className={w.focusLabel}>Что неделя пыталась показать</p>
            <p className={w.focusBody}>
              Главный повторяющийся фокус:{" "}
              <strong>
                {describeFocus(integration.data_points.dominant_question_focus as string | null | undefined)}
              </strong>
              .
              {typeof integration.data_points.ritual_feedback_no_days === "number" &&
              integration.data_points.ritual_feedback_no_days > 0
                ? ` Несобранных дней: ${integration.data_points.ritual_feedback_no_days}.`
                : " Срывов по закрытию дня почти не было."}
            </p>
          </div>
        </DsCard>
      )}
    </ProductPageScreen>
  );
}
