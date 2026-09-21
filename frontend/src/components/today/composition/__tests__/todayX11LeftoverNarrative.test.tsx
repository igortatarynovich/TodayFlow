/**
 * X11 — locked 4-surface has one Inventory narrative.
 * Glance-as-act, stacked leftover, promise-trap evening, and leftover query surfaces stay off product Today.
 * Canon: TODAY_PRODUCT_FLOW_V1 X11 · FULL_USER_PATH_CANON_V1 §13
 */

import { render, screen } from "@testing-library/react";
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
  generation_id: "x11-leftover",
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

describe("X11 locked leftover narrative", () => {
  beforeEach(() => {
    window.localStorage.clear();
    authState.isAuthenticated = false;
  });

  it("does not mount Glance-as-act or leftover glance zone on the locked 4-surface", () => {
    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    expect(screen.getByTestId("today-zone-foundation")).toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-glance-act")).not.toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-glance")).not.toBeInTheDocument();
  });

  it("paints evening gratitude, not promise-trap drama or a second day story", () => {
    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    expect(screen.getByTestId("today-frame-evening")).toBeInTheDocument();
    expect(screen.getByTestId("today-evening-gratitude")).toBeInTheDocument();
    expect(screen.queryByTestId("evening-promise-picker")).not.toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-promise")).not.toBeInTheDocument();
    expect(screen.queryByTestId("today-composition-evening")).not.toBeInTheDocument();
    expect(screen.queryByTestId("today-composition-closed")).not.toBeInTheDocument();
  });

  it("does not paint leftover pick / personal-number copy on the locked surface", () => {
    render(<TodayCompositionSurface {...baseProps} variant="default" />);

    const text = (screen.getByTestId("today-composition-surface").textContent || "").toLowerCase();
    expect(text).not.toMatch(/выбери ту/);
    expect(text).not.toMatch(/к которой тянет/);
    expect(text).not.toMatch(/сво[её] число/);
    expect(text).not.toMatch(/интуитивно выбери/);
  });
});
