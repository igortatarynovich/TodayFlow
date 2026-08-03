import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TodayCompositionSurface } from "@/components/today/composition/TodayCompositionSurface";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";
import type { TodayContractV1 } from "@/lib/todayContract";
import {
  dayContinuityStorageKey,
  type DayContinuityRecord,
} from "@/lib/todayDayContinuity";

jest.mock("@/hooks/useMeaningRuntime", () => ({
  useMeaningRuntime: () => ({ trackMeaningEvent: jest.fn() }),
}));

jest.mock("@/lib/api", () => ({
  getJson: jest.fn().mockRejectedValue(new Error("no auth")),
  postJson: jest.fn(),
  getStoredAccessToken: jest.fn(() => null),
}));

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
    const zoneIds = within(surface)
      .getAllByTestId(/^today-zone-/)
      .map((el) => el.getAttribute("data-testid"));

    expect(zoneIds.indexOf("today-zone-memory")).toBeLessThan(zoneIds.indexOf("today-zone-greeting"));
  });

  it("hides memory stub when yesterday was not closed", () => {
    render(<TodayCompositionSurface {...baseProps} variant="default" />);
    expect(screen.queryByTestId("today-entity-memory-stub")).not.toBeInTheDocument();
    expect(screen.queryByText(/Здесь появится связь/i)).not.toBeInTheDocument();
  });

  it("renders day story greeting and foundation before ritual", () => {
    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    expect(screen.getByTestId("today-zone-greeting")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-hero")).toBeInTheDocument();
    expect(screen.getByTestId("today-entity-daily-theme")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-ritual-gates")).toBeInTheDocument();
    expect(screen.getByTestId("today-ritual-tarot-gate")).toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-why-story")).not.toBeInTheDocument();
    // PR-3: no strengthen invent without practice_recommendation
    expect(screen.queryByTestId("today-zone-strengthen")).not.toBeInTheDocument();
    // Number/card are ritual layer — not in hero before pick
    expect(screen.getByTestId("today-zone-hero").textContent).not.toMatch(/число дня/i);
  });

  it("keeps day hero when embedded in web dashboard without leaking number before ritual", () => {
    render(<TodayCompositionSurface {...baseProps} variant="default" embeddedInWebDashboard />);

    expect(screen.queryByTestId("today-zone-greeting")).not.toBeInTheDocument();
    expect(screen.getByTestId("today-zone-hero")).toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-pulse")).not.toBeInTheDocument();
    expect(screen.getByTestId("today-zone-ritual-gates")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-glance-act")).toBeInTheDocument();
    expect(screen.getByTestId("today-screen-flow")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-hero").textContent).not.toMatch(/число дня\s*[—-]?\s*4/i);
  });

  it("ScreenFlow Glance-first hosts steps with verdict on glance", () => {
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
    expect(screen.getByTestId("today-zone-glance-act")).toBeInTheDocument();
    // Glance hero is day overview — not four-sphere VerdictStrip (2026-08-01).
    expect(screen.queryByTestId("today-slot-verdict-strip")).not.toBeInTheDocument();
    expect(screen.getByTestId("today-slot-glance-nearest")).toBeInTheDocument();
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

  it("opens tarot pick overlay from ritual gate without inventing strengthen", async () => {
    const user = userEvent.setup();
    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    expect(screen.queryByTestId("today-ritual-tarot-pick")).not.toBeInTheDocument();
    await user.click(screen.getByTestId("today-ritual-tarot-gate"));
    expect(screen.getByTestId("today-ritual-tarot-overlay")).toBeInTheDocument();
    expect(screen.getByTestId("today-ritual-tarot-pick")).toBeInTheDocument();
    expect(screen.getByText(RITUAL_COPY.experiencePickCardEyebrow)).toBeInTheDocument();
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
    // Personal acts live on a later ScreenFlow step — still in DOM
    expect(screen.getByTestId("today-entity-synthesis")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-ritual-gates")).toBeInTheDocument();
    // Plot owns conflict narrative — not a duplicate short_name in the hero chrome
    expect(screen.getByTestId("today-zone-plot-narrative")).toBeInTheDocument();
    expect(screen.getByTestId("today-plot-why").textContent).toMatch(/Луна в Козероге/i);
    const hero = screen.getByTestId("today-zone-hero").textContent || "";
    expect(hero).not.toMatch(/Ломать работающее или беречь ровный ритм/);
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

    expect(screen.getByTestId("today-zone-symbol-impacts")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-tarot-impact")).toHaveTextContent(/Сила/);
    expect(screen.getByTestId("today-zone-number-impact")).toHaveTextContent(/4|Число/);
    expect(screen.getByTestId("today-zone-tarot-impact").textContent).toMatch(/открыт/i);
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

    expect(screen.queryByTestId("today-zone-ritual-gates")).not.toBeInTheDocument();
    expect(screen.getByTestId("today-zone-reading")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-move")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-bridges-wrap")).toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-personal")).not.toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-strengthen")).not.toBeInTheDocument();
    expect(screen.queryByTestId("today-soft-why")).not.toBeInTheDocument();
    expect(screen.getByTestId("today-entity-synthesis")).toBeInTheDocument();
    expect(screen.queryByText("Энергия дня")).not.toBeInTheDocument();
  });

  it("shows strengthen and soft why when day_story supplies recommendation and claims", () => {
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

    expect(screen.getByTestId("today-zone-strengthen")).toBeInTheDocument();
    expect(screen.getByTestId("today-tool-practice")).toBeInTheDocument();
    expect(screen.getByTestId("today-soft-why")).toHaveTextContent(/ясной линии/i);
  });

  it("opens promise form when ritual complete", async () => {
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
    // Phase 2b: promise lives on Move — ActNav uses ScreenFlow step ids
    const moveNav =
      screen.queryByRole("button", { name: /Действие/i }) ||
      screen.queryByTestId("today-act-nav-4") ||
      screen.queryByTestId("today-act-nav-3");
    if (moveNav) await user.click(moveNav);
    await user.click(screen.getByTestId("today-zone-promise-open"));
    expect(screen.getByTestId("today-entity-daily-goal")).toBeInTheDocument();
  });

  it("shows morning dialogue when mood missing", () => {
    render(<TodayCompositionSurface {...baseProps} variant="default" />);
    expect(screen.getByTestId("today-zone-dialogue-morning")).toBeInTheDocument();
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
    expect(screen.getByTestId("today-zone-ritual-gates")).toBeInTheDocument();
    expect(screen.getByTestId("today-ritual-tarot-gate")).toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-growth")).not.toBeInTheDocument();
    (resolveTodayDayPhase as jest.Mock).mockReturnValue("morning");
  });
});
