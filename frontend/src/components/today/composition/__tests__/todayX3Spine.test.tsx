/**
 * X3 — Theme → Focus → Step readable spine on the locked 4-surface.
 * Does not encode X4 reveal or X5 number identity.
 * Canon: TODAY_PRODUCT_FLOW_V1 · TODAY_DISPLAY_INVENTORY_V1
 */

import { render, screen, within } from "@testing-library/react";
import { TodayCompositionSurface } from "@/components/today/composition/TodayCompositionSurface";
import type { TodayContractV1 } from "@/lib/todayContract";
import { DAY_MODE_LABELS_RU } from "@/lib/dayAtmosphere";
import { SHARED_DAY_HUMAN_LINES } from "@/lib/todayK01HumanLine";

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

const authState = {
  isAuthenticated: false,
  isLoading: false,
  profile: null,
  refresh: jest.fn(),
  networkDegraded: false,
  warningMessage: null,
  lastValidatedAt: null,
  lastSnapshotSavedAt: null,
};

jest.mock("@/lib/useAuth", () => ({
  useAuth: () => authState,
}));

jest.mock("@/lib/time-of-day", () => ({
  ...jest.requireActual("@/lib/time-of-day"),
  getTimeOfDayByHour: jest.fn(() => "evening"),
}));

const sampleContract: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "День ясности — спокойный ритм и одна главная линия." },
  personal_growth: { development_point: "Замедлиться и услышать себя." },
  domains: {
    work: { status: "s", opportunity: "o", risk: "r", action: "a" },
    money: { status: "s", opportunity: "o", risk: "r", action: "a" },
    relationships: { status: "s", opportunity: "o", risk: "r", action: "a" },
    energy: { status: "s", opportunity: "o", risk: "r", action: "a" },
  },
  primary_action: "Сделай одну главную задачу до обеда.",
  progress: {},
  generation_id: "x3-spine",
  global_day: { primary_energy: "clarity" },
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
};

const personalContract: TodayContractV1 = {
  ...sampleContract,
  personal_day: { natal_overlay: { focus_axis: "work", activations: [{ id: "a1" }] } },
  day_story: {
    contract_version: "day_story_v1",
    interpretation_status: "ok",
    day_personal: {
      summary_ru: "Сегодня тебе важно назвать одну конкретную договорённость.",
    },
    do: ["Скажи одну конкретную просьбу до обеда."],
    day_scenario: {
      conflict: {
        why_personal: "В работе тебе обычно легче держать одну линию, чем разбрасываться.",
      },
    },
  },
};

describe("X3 Theme / Focus / Step spine", () => {
  beforeEach(() => {
    window.localStorage.clear();
    authState.isAuthenticated = false;
  });

  it("opens on TODAY Theme and keeps ritual and evening out of that frame", () => {
    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    const flow = screen.getByTestId("today-screen-flow");
    expect(flow).toHaveAttribute("data-active-index", "0");
    expect(flow.querySelector('[data-screen-flow-step="today"]')).toHaveAttribute(
      "data-step-active",
      "true",
    );

    const today = screen.getByTestId("today-frame-day");
    const hero = within(today).getByTestId("today-day-brief-vibe");
    expect(hero).toHaveTextContent(DAY_MODE_LABELS_RU.clarity);
    expect(hero).toHaveTextContent(SHARED_DAY_HUMAN_LINES.clarity);

    expect(within(today).queryByTestId("today-ritual-tarot-gate")).not.toBeInTheDocument();
    expect(within(today).queryByTestId("today-ritual-number-gate")).not.toBeInTheDocument();
    expect(within(today).queryByTestId("today-evening-gratitude")).not.toBeInTheDocument();
    expect(within(today).queryByTestId("today-my-day")).not.toBeInTheDocument();

    const ritual = screen.getByTestId("today-frame-rituals");
    expect(within(ritual).getByTestId("today-ritual-tarot-gate")).toBeInTheDocument();
    expect(within(ritual).queryByTestId("today-evening-gratitude")).not.toBeInTheDocument();
    expect(within(ritual).queryByTestId("today-day-brief-vibe")).not.toBeInTheDocument();

    expect(screen.queryByTestId("today-frame-my-day")).not.toBeInTheDocument();
    expect(screen.getByTestId("today-evening-gratitude")).toBeInTheDocument();
  });

  it("exposes Personal Focus before Step on MY DAY when capability exists", () => {
    authState.isAuthenticated = true;
    render(
      <TodayCompositionSurface
        {...baseProps}
        contract={personalContract}
        variant="default"
        coreProfile={{ astro: { birth_date: "1990-01-15" } } as never}
      />,
    );

    const myDay = screen.getByTestId("today-frame-my-day");
    const headline = within(myDay).getByTestId("today-my-day-headline");
    const focus = within(myDay).getByTestId("today-handoff-focus");
    const step = within(myDay).getByTestId("today-handoff-focus-prioritize");

    expect(headline).toHaveTextContent("Сегодня тебе важно назвать одну конкретную договорённость.");
    expect(focus).toHaveTextContent("Работа");
    expect(focus).toHaveTextContent("В работе тебе обычно легче держать одну линию");
    expect(step).toHaveTextContent("Скажи одну конкретную просьбу до обеда.");

    expect(headline.compareDocumentPosition(focus) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(focus.compareDocumentPosition(step) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });
});
