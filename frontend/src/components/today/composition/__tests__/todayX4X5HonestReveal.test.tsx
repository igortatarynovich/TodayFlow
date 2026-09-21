/**
 * X4/X5 — locked 4-surface T2 path. Card gate then number gate (A→B).
 * Overlay gesture stays theater; this file audits painted chrome, not mechanic.
 * Canon: TODAY_PRODUCT_FLOW_V1 X4/X5 · TODAY_DISPLAY_INVENTORY_V1 T2-gate.*
 */

import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TodayCompositionSurface } from "@/components/today/composition/TodayCompositionSurface";
import type { TodayContractV1 } from "@/lib/todayContract";

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
  generation_id: "x4-x5-reveal",
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

function seedCardOpen() {
  window.localStorage.setItem(
    "todayflow.day_engagement.v1.2026-06-23",
    JSON.stringify({
      tarotPickedName: "Сила",
      tarotPickedId: 8,
      numberConfirmed: false,
      dayGoal: null,
      practiceStarted: false,
      affirmationRead: false,
      todayOpened: true,
    }),
  );
}

describe("X4/X5 locked T2 honest reveal", () => {
  beforeEach(() => {
    window.localStorage.clear();
    authState.isAuthenticated = false;
  });

  it("X4: locked card gate does not paint a pick of a prebaked card", () => {
    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    const gate = within(screen.getByTestId("today-frame-rituals")).getByTestId("today-ritual-tarot-gate");
    const text = (gate.textContent || "").toLowerCase();
    expect(text).toMatch(/открой|открыть|вытяни|сними/);
    expect(text).not.toMatch(/выбери ту/);
    expect(text).not.toMatch(/к которой тянет/);
    expect(text).not.toMatch(/выбрать карту/);
    expect(screen.queryByTestId("today-frame-number")).not.toBeInTheDocument();
  });

  it("X4 overlay keeps a reveal verb, not a real pick", async () => {
    const user = userEvent.setup();
    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    await user.click(screen.getByTestId("today-ritual-tarot-gate"));
    const overlay = await screen.findByTestId("today-ritual-tarot-overlay");
    expect(overlay).toHaveAttribute("aria-label", expect.stringMatching(/вытащим|открой|открыть/i));
    expect(within(overlay).getByTestId("ritual-tarot-deck-commit")).toHaveTextContent(/^Открыть карту$/);
    expect((overlay.textContent || "").toLowerCase()).not.toMatch(/выбери ту|к которой тянет|выбрать карту/);
  });

  it("X5: locked number gate after card does not paint a personal calendar number", async () => {
    seedCardOpen();
    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    expect(screen.getByTestId("today-ritual-card-kept")).toBeInTheDocument();
    const gate = within(screen.getByTestId("today-frame-number")).getByTestId("today-ritual-number-gate");
    const text = (gate.textContent || "").toLowerCase();
    expect(text).not.toMatch(/сво[её] число/);
    expect(text).not.toMatch(/тво[её] число/);
    expect(text).not.toMatch(/выбрать число/);
    expect(text).toMatch(/число/);
  });

  it("X5 overlay ring stays a calendar-day reveal, not a personal pick", async () => {
    const user = userEvent.setup();
    seedCardOpen();
    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    await user.click(screen.getByTestId("today-ritual-number-gate"));
    const overlay = await screen.findByTestId("today-ritual-number-overlay");
    expect(overlay).toHaveAttribute("aria-label", expect.stringMatching(/число дня/i));
    expect((overlay.getAttribute("aria-label") || "").toLowerCase()).not.toMatch(/сво[её]|тво[её]/);
    const ringButtons = within(overlay).getAllByRole("button", { name: "Открыть число дня" });
    expect(ringButtons.length).toBeGreaterThan(0);
  });
});
