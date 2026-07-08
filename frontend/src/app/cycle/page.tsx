"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { DsBody, DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { useAuth } from "@/lib/useAuth";
import { getJson, postJson } from "@/lib/api";
import { useToast } from "@/components/ToastProvider";
import { rhythmTierLabelForScore } from "@/components/today/todayRitualCopy";

type CycleEntry = {
  id: number;
  date: string;
  cycle_day: number | null;
  period_intensity: string | null;
  ovulation: boolean;
  fertile_window: boolean;
  symptoms: Record<string, unknown> | null;
};

type CycleInsights = {
  from_date: string;
  to_date: string;
  tracked_days: number;
  average_cycle_day: number | null;
  period_intensity_distribution: Record<string, number>;
  ovulation_days: number;
  fertile_window_days: number;
  top_symptoms: Array<{ label: string; count: number }>;
  recommendations: string[];
};

type FusionResponse = {
  scores: {
    energy: number;
    emotional_balance: number;
    focus: number;
  };
  encouragement: string;
};

type PracticeResponse = {
  id: string;
  title: string;
  description: string;
  category: string;
  practice_type?: string;
  cycle_type?: string;
  duration_minutes?: number;
  tags?: string[];
};

type DailyScenario = {
  mode: "recovery" | "balance" | "peak";
  title: string;
  subtitle: string;
  actions: string[];
};

export default function CyclePage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const toast = useToast();
  const [loading, setLoading] = useState(true);
  const [entries, setEntries] = useState<CycleEntry[]>([]);
  const [insights, setInsights] = useState<CycleInsights | null>(null);
  const [fusion, setFusion] = useState<FusionResponse | null>(null);
  const [recommendedPractices, setRecommendedPractices] = useState<PracticeResponse[]>([]);
  const [submitting, setSubmitting] = useState(false);

  const [cycleDay, setCycleDay] = useState("");
  const [periodIntensity, setPeriodIntensity] = useState("none");
  const [ovulation, setOvulation] = useState(false);
  const [fertileWindow, setFertileWindow] = useState(false);
  const [symptomsInput, setSymptomsInput] = useState("");

  const today = useMemo(() => new Date().toISOString().split("T")[0], []);
  const todayEntry = entries[0] || null;
  const dailyScenario = useMemo(() => buildDailyScenario(todayEntry, fusion), [todayEntry, fusion]);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [entryData, insightsData, fusionData] = await Promise.all([
        getJson<CycleEntry[]>(`/calendar/cycle?from_date=${shiftDate(today, -30)}&to_date=${today}`),
        getJson<CycleInsights>(`/calendar/cycle/insights?from_date=${shiftDate(today, -30)}&to_date=${today}`),
        getJson<FusionResponse>(`/tracking/fusion/${today}`).catch(() => null),
      ]);
      const allPractices = await getJson<PracticeResponse[]>("/practices/").catch(() => []);
      setEntries(entryData);
      setInsights(insightsData);
      setFusion(fusionData);
      setRecommendedPractices(selectCyclePractices(entryData, insightsData, fusionData, allPractices));
    } finally {
      setLoading(false);
    }
  }, [today]);

  useEffect(() => {
    if (!isAuthenticated) return;
    loadData();
  }, [isAuthenticated, loadData]);

  useEffect(() => {
    if (!todayEntry) return;
    setCycleDay(todayEntry.cycle_day ? String(todayEntry.cycle_day) : "");
    setPeriodIntensity(todayEntry.period_intensity || "none");
    setOvulation(!!todayEntry.ovulation);
    setFertileWindow(!!todayEntry.fertile_window);
    setSymptomsInput(formatSymptoms(todayEntry.symptoms));
  }, [todayEntry]);

  const submitTodayEntry = async () => {
    setSubmitting(true);
    try {
      const symptoms = parseSymptoms(symptomsInput);
      await postJson("/calendar/cycle", {
        date: today,
        cycle_day: cycleDay ? Number(cycleDay) : null,
        period_intensity: periodIntensity === "none" ? null : periodIntensity,
        ovulation,
        fertile_window: fertileWindow,
        symptoms,
      });
      await loadData();
    } catch (error: any) {
      toast.error(error?.message || "Не удалось сохранить данные цикла");
    } finally {
      setSubmitting(false);
    }
  };

  if (authLoading || loading) {
    return (
      <ProductPageScreen testId="cycle-page" title="Личный цикл" loading loadingLabel="Загрузка…" />
    );
  }

  if (!isAuthenticated) {
    return (
      <ProductPageScreen
        testId="cycle-page"
        title="Личный ритм цикла"
        guest={{
          message:
            "Войди, чтобы видеть цикл как спокойный персональный слой: фиксация, сценарий дня и рекомендации без перегруженной аналитики.",
          ctaHref: "/auth?redirect=/cycle",
          ctaLabel: "Войти",
        }}
      />
    );
  }

  return (
    <ProductPageScreen
      testId="cycle-page"
      eyebrow="Cycle Layer"
      title="Личный цикл как понятный дневной ориентир"
      subtitle="Здесь цикл не превращается в перегруженную аналитику. Ты видишь текущее состояние, фиксируешь день и сразу понимаешь, какой ритм для тебя сегодня бережнее и эффективнее."
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <div style={{ display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
        <DsButton href="/today" size="sm">
          К Today
        </DsButton>
        <DsButton href="/calendar" variant="secondary" size="sm">
          К календарю
        </DsButton>
        <DsButton href="/practices" variant="secondary" size="sm">
          Практики
        </DsButton>
      </div>

      <section className={pl.panel}>
        <p className={v2.eyebrow}>Текущий срез</p>
        {fusion ? (
          <>
            <DsBody className={`${pl.bodyMtXs} ${pl.scoreValue}`}>
              Энергия — {rhythmTierLabelForScore(fusion.scores.energy)}
              <br />
              Баланс — {rhythmTierLabelForScore(fusion.scores.emotional_balance)}
              <br />
              Фокус — {rhythmTierLabelForScore(fusion.scores.focus)}
            </DsBody>
            <DsBody size="sm" className={pl.bodyMtXs}>
              Если интересно: энергия {fusion.scores.energy}/100, баланс {fusion.scores.emotional_balance}/100, фокус{" "}
              {fusion.scores.focus}/100
            </DsBody>
            <DsBody size="sm" className={pl.bodyMtSm}>
              {fusion.encouragement}
            </DsBody>
          </>
        ) : (
          <DsBody size="sm" className={pl.bodyMtSm}>
            Когда появятся данные дня, здесь будет виден живой срез состояния.
          </DsBody>
        )}
      </section>

      <section className={pl.grid2}>
        <div className={pl.panel}>
          <h2 className={v2.sectionTitle}>Зафиксировать сегодняшний день</h2>
          <div className={pl.formStack} style={{ marginTop: "0.75rem" }}>
              <input
                value={cycleDay}
                onChange={(e) => setCycleDay(e.target.value)}
                placeholder="День цикла"
                className="orbit-input"
              />
              <select value={periodIntensity} onChange={(e) => setPeriodIntensity(e.target.value)} className="orbit-input">
                <option value="none">Интенсивность не отмечена</option>
                <option value="light">Легкая</option>
                <option value="medium">Средняя</option>
                <option value="heavy">Сильная</option>
              </select>
              <input
                value={symptomsInput}
                onChange={(e) => setSymptomsInput(e.target.value)}
                placeholder="Симптомы через запятую"
                className="orbit-input"
              />
              <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "center" }}>
                <label className="orbit-body-sm" style={{ color: "#334155" }}>
                  <input type="checkbox" checked={ovulation} onChange={(e) => setOvulation(e.target.checked)} /> Овуляция
                </label>
                <label className="orbit-body-sm" style={{ color: "#334155" }}>
                  <input type="checkbox" checked={fertileWindow} onChange={(e) => setFertileWindow(e.target.checked)} /> Фертильное окно
                </label>
              </div>
              <div style={{ display: "flex", gap: "0.55rem", flexWrap: "wrap" }}>
                <DsButton onClick={submitTodayEntry} disabled={submitting}>
                  {submitting ? "Сохранение..." : "Сохранить сегодня"}
                </DsButton>
              </div>
            </div>
          </div>

          <div className={pl.panel}>
            <h2 className={v2.sectionTitle}>Сценарий дня</h2>
            <div
              style={{
                border: "1px solid #ece4d8",
                borderRadius: "16px",
                padding: "0.9rem 1rem",
                background:
                  dailyScenario.mode === "peak"
                    ? "linear-gradient(135deg, #f1fbff 0%, #f8fcff 100%)"
                    : dailyScenario.mode === "balance"
                      ? "linear-gradient(135deg, #fffdf8 0%, #fbf7ef 100%)"
                      : "linear-gradient(135deg, #fff8ef 0%, #fffdf8 100%)",
              }}
            >
              <div className="orbit-body" style={{ color: "#352515", fontWeight: 700 }}>
                {dailyScenario.title}
              </div>
              <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#465567", lineHeight: 1.7 }}>
                {dailyScenario.subtitle}
              </p>
              <ul style={{ margin: "0.7rem 0 0 1rem", color: "#334155" }}>
                {dailyScenario.actions.map((action) => (
                  <li key={action} className="orbit-body-sm" style={{ marginBottom: "0.35rem", lineHeight: 1.6 }}>
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        <section className={pl.grid2}>
          <div className={pl.panel}>
            <h2 className={v2.sectionTitle}>Сводка за 30 дней</h2>
            {insights ? (
              <>
                <div style={{ display: "grid", gap: "0.65rem", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))" }}>
                  <SummaryCard title="Дней с трекингом" value={String(insights.tracked_days)} />
                  <SummaryCard title="Средний день" value={insights.average_cycle_day?.toString() || "—"} />
                  <SummaryCard title="Овуляция" value={String(insights.ovulation_days)} />
                  <SummaryCard title="Фертильные дни" value={String(insights.fertile_window_days)} />
                </div>
                <div style={{ marginTop: "0.8rem" }}>
                  <p className="orbit-body-sm" style={{ margin: 0, color: "#465567", lineHeight: 1.7 }}>
                    Интенсивность: легкая {insights.period_intensity_distribution.light || 0}, средняя {insights.period_intensity_distribution.medium || 0}, сильная {insights.period_intensity_distribution.heavy || 0}.
                  </p>
                </div>
                <div style={{ marginTop: "0.8rem" }}>
                  <p className="orbit-body-sm" style={{ margin: 0, color: "#352515", fontWeight: 700 }}>
                    Частые симптомы
                  </p>
                  <div style={{ display: "flex", gap: "0.45rem", flexWrap: "wrap", marginTop: "0.5rem" }}>
                    {insights.top_symptoms.length > 0 ? (
                      insights.top_symptoms.map((item) => (
                        <span
                          key={item.label}
                          className="orbit-body-xs"
                          style={{
                            padding: "0.2rem 0.55rem",
                            borderRadius: "999px",
                            background: "#fff8ee",
                            border: "1px solid #eadfcf",
                            color: "#7c6241",
                          }}
                        >
                          {item.label} ({item.count})
                        </span>
                      ))
                    ) : (
                      <span className="orbit-body-xs" style={{ color: "#64748b" }}>
                        Пока без данных
                      </span>
                    )}
                  </div>
                </div>
              </>
            ) : (
              <p className="orbit-body-sm" style={{ margin: 0, color: "#64748b" }}>
                Недостаточно данных для сводки.
              </p>
            )}
          </div>

          <div className={pl.panel}>
            <h2 className={v2.sectionTitle}>Практики под твой ритм</h2>
            {recommendedPractices.length ? (
              <div style={{ display: "grid", gap: "0.65rem" }}>
                {recommendedPractices.map((practice) => (
                  <article
                    key={practice.id}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      gap: "0.8rem",
                      alignItems: "flex-start",
                      border: "1px solid #ece4d8",
                      background: "#fffdf9",
                      borderRadius: "16px",
                      padding: "0.8rem 0.9rem",
                    }}
                  >
                    <div>
                      <div className="orbit-body" style={{ fontWeight: 700, color: "#352515" }}>
                        {practice.title}
                      </div>
                      <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#334155", lineHeight: 1.6 }}>
                        {practice.description}
                      </p>
                      <div className="orbit-body-xs" style={{ marginTop: "0.35rem", color: "#64748b" }}>
                        {practice.duration_minutes ? `${practice.duration_minutes} мин` : "короткая практика"} • {practice.category}
                      </div>
                    </div>
                    <DsButton href={`/practices/${practice.id}`} variant="secondary" size="sm">
                      Открыть
                    </DsButton>
                  </article>
                ))}
              </div>
            ) : (
              <p className="orbit-body-sm" style={{ margin: 0, color: "#64748b" }}>
                Подходящие практики не найдены. Открой общий каталог практик.
              </p>
            )}
          </div>
        </section>

        <section className={pl.panel}>
          <h2 className={v2.sectionTitle}>Последние отмеченные дни</h2>
          <div style={{ display: "grid", gap: "0.55rem" }}>
            {entries.length ? (
              entries.slice(0, 8).map((entry) => (
                <div
                  key={entry.id}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
                    gap: "0.5rem",
                    border: "1px solid #ece4d8",
                    background: "#fffdf9",
                    borderRadius: "16px",
                    padding: "0.8rem 0.9rem",
                    color: "#334155",
                  }}
                >
                  <span className="orbit-body-sm" style={{ fontWeight: 700 }}>{entry.date}</span>
                  <span className="orbit-body-sm">день цикла: {entry.cycle_day ?? "—"}</span>
                  <span className="orbit-body-sm">интенсивность: {entry.period_intensity ?? "нет"}</span>
                  <span className="orbit-body-sm">{entry.ovulation ? "овуляция" : "обычный день"}</span>
                </div>
              ))
            ) : (
              <p className="orbit-body-sm" style={{ margin: 0, color: "#64748b" }}>
                Записей пока нет.
              </p>
            )}
          </div>
        </section>
    </ProductPageScreen>
  );
}

function selectCyclePractices(
  entries: CycleEntry[],
  insights: CycleInsights | null,
  fusion: FusionResponse | null,
  practices: PracticeResponse[],
): PracticeResponse[] {
  if (!practices.length) return [];

  const latest = entries[0] || null;
  const lowEnergy = !!fusion && fusion.scores.energy < 45;
  const lowBalance = !!fusion && fusion.scores.emotional_balance < 45;
  const heavy = latest?.period_intensity === "heavy";
  const medium = latest?.period_intensity === "medium";
  const ovulation = !!latest?.ovulation;
  const fertile = !!latest?.fertile_window;

  const scored = practices.map((practice) => {
    const haystack = `${practice.title} ${practice.description} ${practice.category} ${(practice.tags || []).join(" ")} ${practice.practice_type || ""} ${practice.cycle_type || ""}`.toLowerCase();
    let score = 0;

    if (practice.cycle_type === "lunar" || practice.practice_type === "cycle_based") score += 2;
    if (lowEnergy && hasAny(haystack, ["дых", "медитац", "мягк", "восстанов", "relax", "осознан"])) score += 3;
    if (lowBalance && hasAny(haystack, ["рефлекс", "дневник", "эмо", "баланс", "calm", "ground"])) score += 2;
    if ((heavy || medium) && hasAny(haystack, ["мягк", "дых", "stretch", "йога", "восстанов"])) score += 3;
    if (ovulation && hasAny(haystack, ["фокус", "актив", "энерг", "действ"])) score += 2;
    if (fertile && hasAny(haystack, ["коммуника", "твор", "открыт", "связ"])) score += 2;
    if (insights && insights.tracked_days < 5 && hasAny(haystack, ["awareness", "check", "micro", "коротк"])) score += 2;
    if ((practice.duration_minutes || 0) > 20 && (lowEnergy || heavy)) score -= 2;

    return { practice, score };
  });

  return scored
    .sort((a, b) => b.score - a.score || (a.practice.duration_minutes || 0) - (b.practice.duration_minutes || 0))
    .map((item) => item.practice)
    .slice(0, 3);
}

function hasAny(haystack: string, needles: string[]): boolean {
  return needles.some((needle) => haystack.includes(needle));
}

function buildDailyScenario(entry: CycleEntry | null, fusion: FusionResponse | null): DailyScenario {
  const heavy = entry?.period_intensity === "heavy";
  const medium = entry?.period_intensity === "medium";
  const lowEnergy = !!fusion && fusion.scores.energy < 45;
  const lowBalance = !!fusion && fusion.scores.emotional_balance < 45;

  if (heavy || lowEnergy) {
    return {
      mode: "recovery",
      title: "Режим восстановления",
      subtitle: "Лучше идти через мягкий темп, меньше перегружать нервную систему и снижать обязательный объем.",
      actions: [
        "2 коротких паузы дыхания по 3-5 минут в первой половине дня.",
        "Оставить только 1-2 приоритетные задачи.",
        "Вечером выбрать мягкую расслабляющую практику.",
      ],
    };
  }

  if (medium || lowBalance || entry?.fertile_window) {
    return {
      mode: "balance",
      title: "Режим баланса",
      subtitle: "Ресурс есть, но лучше двигаться через структурный и управляемый темп.",
      actions: [
        "Собрать день в 3 блока: фокус, восстановление, завершение.",
        "Сделать один осознанный чек-ин состояния в середине дня.",
        "Вечером зафиксировать, что дало энергию, а что забрало.",
      ],
    };
  }

  return {
    mode: "peak",
    title: "Режим пика",
    subtitle: "Потенциал дня высокий: можно брать сложные задачи и усиливать видимый результат.",
    actions: [
      "Сначала самая сложная задача в первые 90-120 минут.",
      "Использовать окно высокой энергии для коммуникаций и творчества.",
      "Зафиксировать результат дня в дневнике, чтобы закрепить паттерн.",
    ],
  };
}

function SummaryCard({ title, value }: { title: string; value: string }) {
  return (
    <div style={{ border: "1px solid #ece4d8", borderRadius: "16px", padding: "0.8rem 0.9rem", background: "#fffdf9" }}>
      <div className="orbit-body-xs" style={{ color: "#64748b" }}>{title}</div>
      <div className="orbit-body" style={{ marginTop: "0.2rem", color: "#352515", fontWeight: 700 }}>{value}</div>
    </div>
  );
}

function parseSymptoms(raw: string): Record<string, boolean> | null {
  const list = raw.split(",").map((item) => item.trim()).filter(Boolean);
  if (!list.length) return null;
  const mapped: Record<string, boolean> = {};
  list.forEach((item) => {
    mapped[item] = true;
  });
  return mapped;
}

function formatSymptoms(symptoms: Record<string, unknown> | null | undefined) {
  if (!symptoms) return "";
  return Object.keys(symptoms).join(", ");
}

function shiftDate(isoDate: string, deltaDays: number): string {
  const [y, m, d] = isoDate.split("-").map(Number);
  const date = new Date(y, (m || 1) - 1, d || 1);
  date.setDate(date.getDate() + deltaDays);
  return date.toISOString().split("T")[0];
}
