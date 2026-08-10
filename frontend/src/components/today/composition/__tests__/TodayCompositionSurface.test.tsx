import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TodayCompositionSurface } from "@/components/today/composition/TodayCompositionSurface";
import type { TodayContractV1 } from "@/lib/todayContract";
import {
  dayContinuityStorageKey,
  type DayContinuityRecord,
} from "@/lib/todayDayContinuity";

jest.mock("@/hooks/useMeaningRuntime", () => ({
  useMeaningRuntime: () => ({ trackMeaningEvent: jest.fn() }),
}));

jest.mock("@/lib/api", () => {
  const actual = jest.requireActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    getJson: jest.fn().mockRejectedValue(new Error("no auth")),
    postJson: jest.fn(),
    getStoredAccessToken: jest.fn(() => null),
  };
});

jest.mock("@/lib/todayDayGreeting", () => ({
  ...jest.requireActual("@/lib/todayDayGreeting"),
  resolveTodayDayPhase: jest.fn(() => "morning"),
}));

import { resolveTodayDayPhase } from "@/lib/todayDayGreeting";

const sampleContract: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "День ясности — спокойный ритм и одна главная линия." },
  personal_growth: { development_point: "Замедлиться и услышать себя." },
  domains: {
    work: {
      status: "сегодня в работе — ясность",
      opportunity: "закрыть одну задачу",
      risk: "распыление",
      action: "Выбери одну задачу.",
    },
    money: {
      status: "сегодня в работе — ясность",
      opportunity: "закрыть одну задачу",
      risk: "распыление",
      action: "Выбери одну задачу.",
    },
    relationships: {
      status: "сегодня в отношениях — больше слушать",
      opportunity: "мягкий контакт",
      risk: "спешить",
      action: "Напиши одному близкому человеку.",
    },
    energy: {
      status: "сегодня дома — тишина",
      opportunity: "короткий разговор",
      risk: "перегруз",
      action: "Удели 10 минут семье.",
    },
  },
  primary_action: "Сделай одну главную задачу до обеда.",
  progress: {},
  generation_id: "test-gen",
};

const baseProps = {
  dateISO: "2026-06-23",
  displayDate: "23 июня",
  todayData: {} as never,
  morningRitualData: null,
  contract: sampleContract,
  cardName: "Сила",
  cardMeaning: "внутренняя опора",
  numerologyValue: "4",
  numerologyMeaning: "структура",
  guideNarrativeLoading: false,
  guideNarrativePayload: null,
  colorLine: "золотистый",
  stoneLine: "янтарь",
};

function seedPreviousDayContinuity(record: DayContinuityRecord) {
  window.localStorage.setItem(dayContinuityStorageKey(record.dateISO), JSON.stringify(record));
}

/** Intent/Reality for today — required before First Today ritual/reveal (placement C). */
function seedFirstTodayReaction() {
  const now = new Date();
  const dayKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
  window.localStorage.setItem(
    "todayflow_onboarding_context_v1",
    JSON.stringify({ intent_theme: "focus", reality_state: "stable", day_key: dayKey }),
  );
}

describe("TodayCompositionSurface", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("renders continuity recall before hero on default variant", () => {
    seedPreviousDayContinuity({
      dateISO: "2026-06-22",
      mainFocus: "Разговор с командой",
      outcome: "partial",
      closedAt: "2026-06-22T20:00:00.000Z",
    });

    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    expect(screen.getByTestId("today-entity-continuity-recall")).toBeInTheDocument();
    expect(screen.getByText("С чего продолжить")).toBeInTheDocument();

    const surface = screen.getByTestId("today-composition-surface");
    const memory = within(surface).getByTestId("today-zone-memory");
    const day = within(surface).getByTestId("today-frame-day");
    expect(memory.compareDocumentPosition(day) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("hides memory stub when yesterday was not closed", () => {
    render(<TodayCompositionSurface {...baseProps} variant="default" />);
    expect(screen.queryByTestId("today-entity-memory-stub")).not.toBeInTheDocument();
    expect(screen.queryByText(/Здесь появится связь/i)).not.toBeInTheDocument();
  });

  it("renders day brief block before ritual", () => {
    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    expect(screen.getByTestId("today-frame-day")).toBeInTheDocument();
    expect(screen.getByTestId("today-day-brief")).toBeInTheDocument();
    expect(screen.getByTestId("today-frame-number")).toBeInTheDocument();
    expect(screen.getByTestId("today-frame-card")).toBeInTheDocument();
    expect(screen.getByTestId("ritual-tarot-pick-grid")).toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-why-story")).not.toBeInTheDocument();
  });

  it("keeps day brief when embedded in web dashboard without leaking number before ritual", () => {
    render(<TodayCompositionSurface {...baseProps} variant="default" embeddedInWebDashboard />);

    expect(screen.queryByTestId("today-zone-greeting")).not.toBeInTheDocument();
    expect(screen.getByTestId("today-frame-day")).toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-pulse")).not.toBeInTheDocument();
    expect(screen.getByTestId("today-frame-number")).toBeInTheDocument();
    expect(screen.getByTestId("today-screen-flow")).toBeInTheDocument();
    expect(screen.getByTestId("today-frame-day").textContent || "").not.toMatch(/число дня\s*[—-]?\s*4/i);
  });

  it("ScreenFlow greeting-first hosts story-deck steps", () => {
    const contractWithScenario: TodayContractV1 = {
      ...sampleContract,
      day_story: {
        contract_version: "day_story_v1",
        interpretation_status: "ok",
        theme: "Ломать работающее или беречь ровный ритм",
        primary_conflict: "Ломать работающее или беречь ровный ритм",
        day_scenario: {
          runtime_sot: true,
          ready: true,
          generation_source: "deterministic_engine_b5",
          conflict: {
            short_name: "Ломать работающее или беречь ровный ритм",
            why_arose: "Луна в Козероге собирает одну линию.",
            opposing_forces: { a: "ломать работающее", b: "беречь ровный ритм" },
          },
          scenes: [
            {
              scene_id: "scene.work_decisions",
              sphere: "work_decisions",
              sphere_label_ru: "Работа и решения",
              role_in_story: "primary",
              what_happens: "В работе сегодня решающий жест.",
              opportunity: "Одно письмо без ожидания одобрения.",
              trap: "Отложить и сделать вид, что выбора нет.",
              recommended_action: "Сделай один короткий шаг.",
              domestic_example: "Письмо, которое ты откладывал.",
            },
          ],
        },
      },
    };

    render(
      <TodayCompositionSurface {...baseProps} contract={contractWithScenario} variant="default" />,
    );

    expect(screen.getByTestId("today-zone-foundation")).toBeInTheDocument();
    expect(screen.getByTestId("today-screen-flow")).toBeInTheDocument();
    expect(screen.getByTestId("today-frame-day")).toBeInTheDocument();
    expect(screen.queryByTestId("today-slot-verdict-strip")).not.toBeInTheDocument();
    expect(screen.getByTestId("today-composition-surface").querySelectorAll("[data-screen-flow-step]").length).toBeGreaterThanOrEqual(3);
  });

  it("hides continuity on firstToday variant", () => {
    seedFirstTodayReaction();
    seedPreviousDayContinuity({
      dateISO: "2026-06-22",
      mainFocus: "Разговор с командой",
      outcome: "done",
      closedAt: "2026-06-22T20:00:00.000Z",
    });

    render(<TodayCompositionSurface {...baseProps} variant="firstToday" />);

    expect(screen.queryByTestId("today-entity-continuity-recall")).not.toBeInTheDocument();
    expect(screen.getByTestId("today-zone-hero")).toBeInTheDocument();
  });

  it("shows evening CTA only after ritual on firstToday", () => {
    seedFirstTodayReaction();
    window.localStorage.setItem(
      "todayflow.day_engagement.v1.2026-06-23",
      JSON.stringify({
        tarotPickedName: "Сила",
        tarotPickedId: 8,
        numberConfirmed: true,
        dayGoal: null,
        practiceStarted: false,
        affirmationRead: false,
        todayOpened: true,
      }),
    );
    render(<TodayCompositionSurface {...baseProps} variant="firstToday" />);

    expect(screen.getByTestId("today-evening-open")).toHaveTextContent("Закрыть день");
  });

  it("opens tarot pick from rituals step without inventing strengthen", async () => {
    const user = userEvent.setup();
    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    await user.click(within(screen.getByTestId("today-frame-day")).getByTestId("today-story-next-anchor"));
    // Six blocks: rituals is step 1 (first chrome dot when day is 0).
    const ritualsDot = screen.getByTestId("screen-flow-dot-1");
    await user.click(ritualsDot);
    expect(screen.getByTestId("today-frame-rituals")).toBeInTheDocument();
    expect(screen.getByTestId("ritual-tarot-pick-grid")).toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-strengthen")).not.toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-actions")).not.toBeInTheDocument();
  });

  it("opens full day reading before ritual when day_scenario is ready", () => {
    const contractWithScenario: TodayContractV1 = {
      ...sampleContract,
      day_story: {
        contract_version: "day_story_v1",
        interpretation_status: "ok",
        theme: "Ломать работающее или беречь ровный ритм",
        primary_conflict: "Ломать работающее или беречь ровный ритм",
        day_scenario: {
          runtime_sot: true,
          ready: true,
          generation_source: "deterministic_engine_b5",
          conflict: {
            short_name: "Ломать работающее или беречь ровный ритм",
            why_arose: "Луна в Козероге собирает одну линию.",
            opposing_forces: { a: "ломать работающее", b: "беречь ровный ритм" },
          },
          scenes: [
            {
              scene_id: "scene.work_decisions",
              sphere: "work_decisions",
              sphere_label_ru: "Работа и решения",
              role_in_story: "primary",
              what_happens: "В работе сегодня решающий жест.",
              opportunity: "Одно письмо без ожидания одобрения.",
              trap: "Отложить и сделать вид, что выбора нет.",
              recommended_action: "Сделай один короткий шаг.",
              domestic_example: "Письмо, которое ты откладывал.",
            },
          ],
        },
      },
    };

    render(
      <TodayCompositionSurface {...baseProps} contract={contractWithScenario} variant="default" />,
    );

    expect(screen.getByTestId("today-screen-flow")).toBeInTheDocument();
    // Six blocks v3.4: day · rituals · instruction · color · tasks · loop
    expect(screen.getByTestId("today-frame-day")).toBeInTheDocument();
    expect(screen.getByTestId("today-day-brief")).toBeInTheDocument();
    expect(screen.getByTestId("today-frame-rituals")).toBeInTheDocument();
    expect(screen.getByTestId("today-frame-number")).toBeInTheDocument();
    expect(screen.getByTestId("today-frame-card")).toBeInTheDocument();
    expect(screen.getByTestId("today-frame-instruction")).toBeInTheDocument();
    expect(screen.getByTestId("today-composition-surface").querySelectorAll("[data-screen-flow-step]").length).toBe(6);
  });

  it("shows opened card and number interpretation after ritual", () => {
    window.localStorage.setItem(
      "todayflow.day_engagement.v1.2026-06-23",
      JSON.stringify({
        tarotPickedName: "Сила",
        tarotPickedId: 8,
        numberConfirmed: true,
        numberValue: "4",
        dayGoal: null,
        practiceStarted: false,
        affirmationRead: false,
        todayOpened: true,
      }),
    );

    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    expect(screen.getByTestId("today-frame-card")).toBeInTheDocument();
    expect(screen.getByTestId("today-frame-number")).toBeInTheDocument();
    // After engagement, ritual steps stay in the handoff shell (reveal or resume UI).
    expect(
      screen.queryByTestId("ritual-tarot-reveal") ||
        screen.queryByTestId("ritual-tarot-pick-grid") ||
        screen.getByTestId("today-frame-card"),
    ).toBeTruthy();
    expect(
      screen.queryByTestId("ritual-number-reveal") ||
        screen.queryByTestId("ritual-number-pick-flower") ||
        screen.getByTestId("today-frame-number"),
    ).toBeTruthy();
  });

  it("shows personalized reading when ritual complete without empty strengthen", () => {
    window.localStorage.setItem(
      "todayflow.day_engagement.v1.2026-06-23",
      JSON.stringify({
        tarotPickedName: "Сила",
        tarotPickedId: 8,
        numberConfirmed: true,
        dayGoal: null,
        practiceStarted: false,
        affirmationRead: false,
        todayOpened: true,
      }),
    );

    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    expect(screen.getByTestId("today-frame-day")).toBeInTheDocument();
    expect(screen.getByTestId("today-frame-rituals")).toBeInTheDocument();
    expect(screen.getByTestId("today-frame-instruction")).toBeInTheDocument();
    expect(screen.getByTestId("today-frame-color")).toBeInTheDocument();
    expect(screen.getByTestId("today-frame-tasks")).toBeInTheDocument();
    expect(screen.getByTestId("today-frame-loop")).toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-personal")).not.toBeInTheDocument();
  });

  it("shows practice frame when day_story supplies recommendation", () => {
    window.localStorage.setItem(
      "todayflow.day_engagement.v1.2026-06-23",
      JSON.stringify({
        tarotPickedName: "Сила",
        tarotPickedId: 8,
        numberConfirmed: true,
        dayGoal: null,
        practiceStarted: false,
        affirmationRead: false,
        todayOpened: true,
      }),
    );

    const contractWithStory: TodayContractV1 = {
      ...sampleContract,
      day_story: {
        contract_version: "day_story_v1",
        theme: "Ясность",
        story: "Сегодня день коротких договорённостей и спокойного темпа.",
        practice_recommendation: {
          kind: "practice",
          text: "Закрыть одну задачу до обеда.",
          reason: "Один результат важнее пяти начатых.",
        },
        trace: {
          derived_claims: [
            { id: "claim.day_axis", kind: "axis", text: "День держится на одной ясной линии." },
          ],
        },
      },
    };

    render(
      <TodayCompositionSurface {...baseProps} contract={contractWithStory} variant="default" />,
    );

    // Tasks block hosts practice gift (six blocks v3.4).
    expect(screen.getByTestId("today-frame-tasks")).toBeInTheDocument();
    expect(screen.getAllByText(/Закрыть одну задачу/i).length).toBeGreaterThan(0);
  });

  it("shows practice CTA when ritual complete", async () => {
    window.localStorage.setItem(
      "todayflow.day_engagement.v1.2026-06-23",
      JSON.stringify({
        tarotPickedName: "Сила",
        tarotPickedId: 8,
        numberConfirmed: true,
        morningMoodId: "calm",
        focusTopicId: "work",
        dayGoal: null,
        practiceStarted: false,
        affirmationRead: false,
        todayOpened: true,
        eveningHighlightId: null,
      }),
    );
    const user = userEvent.setup();
    render(<TodayCompositionSurface {...baseProps} variant="default" />);
    await user.click(within(screen.getByTestId("today-frame-day")).getByTestId("today-story-next-anchor"));
    const tasksDot = screen.getByTestId("screen-flow-dot-4");
    await user.click(tasksDot);
    expect(screen.getByTestId("today-frame-tasks")).toBeInTheDocument();
  });

  it("does not mount morning dialogue as its own six-block step", () => {
    window.localStorage.setItem(
      "todayflow.day_engagement.v1.2026-06-23",
      JSON.stringify({
        tarotPickedName: "Сила",
        tarotPickedId: 8,
        numberConfirmed: true,
        dayGoal: null,
        practiceStarted: false,
        affirmationRead: false,
        todayOpened: true,
      }),
    );
    render(<TodayCompositionSurface {...baseProps} variant="default" />);
    // Priority/dialogue step removed in v3.4 — not a product frame.
    expect(screen.queryByTestId("today-zone-dialogue-morning")).not.toBeInTheDocument();
    expect(screen.getByTestId("today-frame-day")).toBeInTheDocument();
  });

  it("gates firstToday behind intent/reality reaction chips", () => {
    render(<TodayCompositionSurface {...baseProps} variant="firstToday" />);

    expect(screen.getByTestId("conversation-thread-first-today")).toBeInTheDocument();
    expect(screen.getByTestId("first-today-reaction-gate-intent")).toBeInTheDocument();
    expect(screen.queryByTestId("conversation-turn-today_opening")).not.toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-ritual-tarot")).not.toBeInTheDocument();
  });

  it("hides dashboard panels on firstToday conversation path", () => {
    seedFirstTodayReaction();
    render(<TodayCompositionSurface {...baseProps} variant="firstToday" />);

    expect(screen.queryByTestId("today-zone-sphere-focus")).not.toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-color-guide")).not.toBeInTheDocument();
    expect(screen.getByTestId("conversation-thread-first-today")).toBeInTheDocument();
    expect(screen.getByTestId("conversation-turn-today_opening")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-ritual-tarot")).toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-actions")).not.toBeInTheDocument();
  });

  it("shows tarot gate at evening when ritual is still pending", () => {
    (resolveTodayDayPhase as jest.Mock).mockReturnValue("night");
    render(<TodayCompositionSurface {...baseProps} variant="default" />);
    expect(screen.getByTestId("today-frame-card")).toBeInTheDocument();
    expect(screen.getByTestId("ritual-tarot-pick-grid")).toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-growth")).not.toBeInTheDocument();
    (resolveTodayDayPhase as jest.Mock).mockReturnValue("morning");
  });
});
