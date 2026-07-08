"use client";

import { useMemo } from "react";
import { TodayRitualFlow } from "@/components/today/TodayRitualFlow";
import type { FusionResponse, MorningRitualData, TodayCycleData } from "@/components/today/todayPageUtils";
import type { MeaningRingsResponse } from "@/lib/types";
import {
  buildRitualAvoidSignals,
  buildRitualPossibleSignals,
  buildRitualSupportSignals,
  guidanceSummaryForRitual,
} from "@/components/today/todayRitualSignals";

/** Локальное превью UI ритуала «Сегодня». Не для продакшена: в production возвращаем пустую заглушку. */
export default function TodayRitualPreviewPage() {
  const isDev = process.env.NODE_ENV !== "production";

  const todayData = useMemo((): TodayCycleData => {
    return {
      date: "2026-04-25",
      morning: {
        daily_horoscope: {
          spine: {
            day_axis: "День про один честный шаг без суеты",
            best_mode: "Мягкий темп и один защищённый фокус",
            main_risk: "Решать всё параллельно и ждать, что «само рассосётся»",
            first_move: "До обеда выбрать одну главную задачу и назвать её вслух",
            do_not_enter: "Споры на пустом желудке и в чатах без паузы",
          },
          scenarios: [
            {
              slug: "love",
              title: "Любовь и близость",
              focus: "Сегодня важен честный контакт, а не «правильная» версия разговора.",
              summary:
                "Можно получить ясность в одном спокойном разговоре — без требования ответа мгновенно. Не стоит ждать, что вас прочитают между строк: одна простая фраза лучше длинной речи.",
            },
            {
              slug: "career",
              title: "Работа",
              focus: "Один рабочий вектор лучше пяти недожатых задач.",
              summary:
                "День располагает закрыть один содержательный блок. Если улететь в переписку и митинги, к вечеру будет чувство «ничего не сдвинулось».",
            },
            {
              slug: "money",
              title: "Деньги",
              focus: "Отличить срочность от реальной нужды.",
              summary:
                "Импульсивная трата может казаться быстрым решением. На необязательные покупки полезна пауза до вечера.",
            },
          ],
        },
        numerology_number: { value: 7, reduced_value: 7, title: "Число внутренней ясности" },
        numerology_explanation: { summary: "Пауза перед словом даёт больше силы, чем спешка." },
        daily_forecast_summary: { summary: "Хороший день, чтобы назвать главное одним предложением." },
        daily_recommendations: {
          what_to_do: "Один защищённый слот без переключений",
          what_to_avoid: "Договариваться о новом, пока не выдохнулись",
        },
        decision_engine: {
          hero: { energy_score: 63, energy_label: "Ровный темп", risk: "Распыление внимания", focus: ["ритм", "ясность"] },
        },
        tarot_card: { name: "Умеренность" },
      },
      morning_completed: false,
      day_connection: {
        id: 0,
        date: "2026-04-25",
        morning_intention: null,
        morning_focus: "Один фокус до вечера",
        evening_reflection: null,
        evening_observations: null,
        connection_thread: null,
        morning_completed: false,
        day_completed: false,
        evening_completed: false,
      },
      day_trackers: [],
      day_journal_entries: [],
      day_completed: false,
      evening: null,
      evening_completed: false,
      morning_available: true,
      day_available: true,
      evening_available: true,
    };
  }, []);

  const morningRitualData = useMemo((): MorningRitualData => {
    return {
      date: "2026-04-25",
      tarot_card: { name: "Умеренность" },
      tarot_explanation: { meaning: "Баланс и честный темп важнее форса.", summary: "Соединить противоположности без крайностей." },
      numerology_number: { value: 7, title: "Число внутренней ясности" },
    };
  }, []);

  const fusion = useMemo((): FusionResponse => {
    return {
      scores: { energy: 63, emotional_balance: 58, focus: 61 },
      recommendations: ["Вода до обеда", "10 минут движения"],
      encouragement: "Малый шаг сегодня — уже опора.",
      activity_context: {
        guide_meaning_completions_today: {
          habit_completed: 1,
          practice_completed: 0,
          focus_completed: 2,
          affirmation_done: 0,
          ascetic_step_done: 0,
        },
      },
      day_history: {
        contract_version: "day_history_v0",
        yesterday: {
          date: "2026-04-24",
          fusion_scores: { energy: 55, emotional_balance: 60, focus: 52 },
          day_flow: { morning_completed: true, day_completed: false, evening_completed: false },
        },
        fusion_score_delta_vs_yesterday: { energy: 8, emotional_balance: -2, focus: 9 },
        fusion_score_delta_trustworthy: true,
        yesterday_fusion_has_flow_markers: true,
        trailing_7d_flow_days: 7,
        trailing_7d_summary_trustworthy: true,
        trailing_7d_summary: {
          energy: { avg: 51.7, min: 42, max: 61, days: 7 },
          emotional_balance: { avg: 48.2, min: 40, max: 55, days: 7 },
          focus: { avg: 54.9, min: 48, max: 62, days: 7 },
        },
      },
    };
  }, []);

  const meaningRings = useMemo((): MeaningRingsResponse => {
    return {
      window_days: 28,
      generated_at: new Date().toISOString(),
      rings: [
        { ring: "Love", score: 71, trend_7d: 2, confidence: "medium", top_contributors: ["дневник", "утренний чек-ин"] },
        { ring: "Purpose", score: 64, trend_7d: 0, confidence: "medium", top_contributors: ["цели недели"] },
        { ring: "Wealth", score: 59, trend_7d: -1, confidence: "low", top_contributors: ["трекер трат"] },
        { ring: "Energy", score: 68, trend_7d: 3, confidence: "medium", top_contributors: ["сон", "движение"] },
      ],
    };
  }, []);

  const ritualSignals = useMemo(() => {
    const firstAction = "Закрой один блок работы без чата";
    const best = String(todayData.morning?.daily_horoscope?.spine?.best_mode || "").trim();
    return {
      possible: buildRitualPossibleSignals(todayData.morning),
      avoid: buildRitualAvoidSignals(todayData.morning),
      support: buildRitualSupportSignals(
        best,
        guidanceSummaryForRitual({ morning: todayData.morning, actionPlanFirstLine: firstAction }),
      ),
    };
  }, [todayData]);

  const dayLayerPreview = useMemo(
    (): Record<string, unknown> => ({
      nudge_message: "Малый шаг сегодня — уже опора.",
      personal_insight_title: "Точка сборки",
      personal_insight_body:
        "Опирайся на утренний стержень дня: не ускоряйся без нужды и доводи одну линию.",
      personal_insight_chips: ["Один шаг", "Фиксация"],
      life_now_weekly: "Если есть недельный фокус — отметь по нему один шаг.",
      question_of_day_prompt: "Что сейчас ближе к тому, как ты набираешь силы — тишина или контакт?",
    }),
    [],
  );

  if (!isDev) {
    return (
      <main className="orbit-page" style={{ padding: "2rem", fontFamily: "system-ui" }}>
        <p>Превью доступно только в режиме разработки.</p>
      </main>
    );
  }

  return (
    <main
      className="orbit-page todayflow-serene todayflow-shell today-web-page"
      style={{
        background:
          "radial-gradient(1200px 460px at 8% -8%, rgba(234, 211, 163, 0.24), transparent 60%), radial-gradient(900px 420px at 95% -10%, rgba(225, 201, 160, 0.2), transparent 60%), #f7f2ea",
        minHeight: "100dvh",
      }}
    >
      <div
        className="todayflow-shell__container todayflow-main-container"
        style={{
          paddingTop: "1rem",
          paddingBottom: `max(3rem, env(safe-area-inset-bottom, 0px))`,
        }}
      >
        <p className="orbit-body-xs" style={{ margin: "0 0 0.75rem", color: "#7a623d" }}>
          Превью для дизайна:{" "}
          <strong>/dev/today-ritual-preview</strong> — мок-данные, без API.
        </p>
        <TodayRitualFlow
          firstName="Вика"
          profileGender="female"
          displayDate="пятница, 25 апреля"
          todayData={todayData}
          morningRitualData={morningRitualData}
          fusion={fusion}
          meaningRings={meaningRings}
          energyScore={63}
          dayLabel="Мягкий темп и один защищённый фокус"
          subtitle="До обеда выбери одну главную задачу — так проще не распылиться к вечеру."
          cardName="Умеренность"
          cardMeaning="Баланс и честный темп важнее форса."
          numerologyValue="7"
          numerologyMeaning="Пауза перед словом даёт больше силы, чем спешка."
          numerologyLucky={{ time: "14:00–16:00", color: "Лазурь", stone: "Лунный камень" }}
          cardNumberBridge="«Умеренность» и число 7 просят одного: внутренняя честность раньше внешнего «надо»."
          summaryTitle="День про один честный шаг без суеты"
          possible={ritualSignals.possible}
          avoid={ritualSignals.avoid}
          support={ritualSignals.support}
          whyMoon={null}
          whyLunar={null}
          actionItems={[
            { text: "Закрой один блок работы без чата", ring: "фокус" },
            { text: "Одна честная фраза близкому", ring: "близость" },
          ]}
          weeklyGoals={[]}
          onOpenHabit={() => undefined}
          onTrackMood={() => undefined}
          guideNarrativeLoading={false}
          guideNarrativePayload={null}
          spheresNarrativePayload={null}
          dayLayerNarrativePayload={dayLayerPreview}
          dayLayerNarrativeLoading={false}
          eveningPayload={null}
          eveningNarrativeLoading={false}
          eveningCustomPhrase=""
          eveningMarkedDone={false}
          eveningObservations={{ noticed: "", hardest: "", easier_than_expected: "" }}
          eveningReflectionInput=""
          eveningSaving={false}
          onEveningCustomPhraseChange={() => undefined}
          onEveningMarkedDoneChange={() => undefined}
          onEveningObservationChange={() => undefined}
          onEveningReflectionChange={() => undefined}
          onSaveEvening={() => undefined}
          onRefreshToday={() => undefined}
          onEveningPhaseSaved={() => undefined}
        />
      </div>
    </main>
  );
}
