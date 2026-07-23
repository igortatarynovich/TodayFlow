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
    relationships: {
      status: "сегодня в отношениях — больше слушать",
      opportunity: "мягкий контакт",
      risk: "спешить",
      action: "Напиши одному близкому человеку.",
    },
    money_work: {
      status: "сегодня в работе — ясность",
      opportunity: "закрыть одну задачу",
      risk: "распыление",
      action: "Выбери одну задачу.",
    },
    family: {
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

    expect(zoneIds.indexOf("today-zone-continuity")).toBeLessThan(zoneIds.indexOf("today-zone-greeting"));
  });

  it("renders day story greeting and foundation before ritual", () => {
    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    expect(screen.getByTestId("today-zone-greeting")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-pulse")).toBeInTheDocument();
    expect(screen.getByText("Энергия дня")).toBeInTheDocument();
    expect(screen.getByTestId("today-entity-daily-theme")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-glance")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-sky-influences")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-sphere-focus")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-color-guide")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-ritual-gates")).toBeInTheDocument();
    expect(screen.getByTestId("today-ritual-tarot-gate")).toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-why-story")).not.toBeInTheDocument();
    // PR-3: no strengthen invent without practice_recommendation
    expect(screen.queryByTestId("today-zone-strengthen")).not.toBeInTheDocument();
  });

  it("hides continuity on firstToday variant", () => {
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
    expect(screen.getByTestId("today-zone-personal")).toBeInTheDocument();
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

    await user.click(screen.getByTestId("today-zone-promise-open"));
    expect(screen.getByTestId("today-entity-daily-goal")).toBeInTheDocument();
  });

  it("shows morning dialogue when mood missing", () => {
    render(<TodayCompositionSurface {...baseProps} variant="default" />);
    expect(screen.getByTestId("today-zone-dialogue-morning")).toBeInTheDocument();
    expect(screen.getByText("Как ты входишь в этот день?")).toBeInTheDocument();
  });

  it("hides dashboard panels on firstToday conversation path", () => {
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
