/**
 * X14 executable audit — live completeness / placement of existing slots.
 * Canon: TODAY_DISPLAY_INVENTORY_V1 T1.continuity · T3.tracker
 * This file proves defects. It does not close the gate.
 */
import { render, screen, within } from "@testing-library/react";
import { emitTodayDisplayFrame } from "@/lib/displayGrammar/emitTodayDisplayFrame";
import { scanDisplayGrammar } from "@/lib/displayGrammar/scanDisplayGrammar";
import type { TodayContractV1 } from "@/lib/todayContract";
import { buildTodayProgressRows } from "@/lib/todayGrowthTrackers";
import { loadYesterdayEveningClose } from "@/lib/todayEveningGratitude";
import { TodayDayTasksBlock } from "@/components/today/composition/TodayDayTasksBlock";
import { TodayMyDayPane } from "@/components/today/composition/TodayMyDayPane";
import { getJson } from "@/lib/api";

jest.mock("@/lib/api", () => {
  const actual = jest.requireActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    getJson: jest.fn(),
  };
});

const getJsonMock = getJson as jest.MockedFunction<typeof getJson>;

const persistContract: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "День просит не спешить." },
  personal_growth: { development_point: "Один шаг." },
  domains: {
    work: { status: "s", opportunity: "o", risk: "r", action: "a" },
    money: { status: "s", opportunity: "o", risk: "r", action: "a" },
    relationships: { status: "s", opportunity: "o", risk: "r", action: "a" },
    energy: { status: "s", opportunity: "o", risk: "r", action: "a" },
  },
  primary_action: "Одно дело до полудня",
  progress: {},
  generation_id: "x14-audit",
  personal_day: { natal_overlay: { focus_axis: "work", activations: [{ id: "a1" }] } },
  day_story: {
    contract_version: "day_story_v1",
    day_personal: { summary_ru: "Одно обещание без шума." },
    do: ["Назови одно обещание"],
  },
  today_progress: {
    rows: [
      {
        id: "habit:1",
        kind: "habit",
        kind_label: "Привычка",
        name: "Стакан воды",
        streak_days: 3,
        days_bool: [false, false, false, false, false, false, true],
      },
    ],
  },
};

describe("X14 T1.continuity audit", () => {
  it("grammar emits T1.continuity only when a caller passes continuityBody", () => {
    const filled = emitTodayDisplayFrame({
      contract: persistContract,
      capability: "light",
      continuityBody: "Вчера ты отметил(а) благодарность: за спокойный момент.",
    });
    expect(filled.atoms?.some((a) => a.slot_id === "T1.continuity")).toBe(true);
    expect(scanDisplayGrammar(filled)).toEqual([]);

    const withoutCaller = emitTodayDisplayFrame({
      contract: persistContract,
      capability: "light",
    });
    expect(withoutCaller.atoms?.some((a) => a.slot_id === "T1.continuity")).toBe(false);
  });

  it("GET failure with no local record omits silently instead of transport chrome", async () => {
    window.localStorage.clear();
    getJsonMock.mockRejectedValue(new TypeError("Failed to fetch"));
    const snap = await loadYesterdayEveningClose("2026-09-22", { authenticated: true });
    expect(getJsonMock).toHaveBeenCalledWith("/day-connection/2026-09-21");
    expect(snap).toBeNull();
  });
});

describe("X14 T3.tracker audit", () => {
  it("grammar does not emit T3.tracker even when today_progress habit rows exist", () => {
    const frame = emitTodayDisplayFrame({
      contract: persistContract,
      capability: "light",
    });
    expect(frame.atoms?.some((a) => a.slot_id === "T3.tracker")).toBe(false);
    expect(frame.today_lock?.emptyTasksChrome).toBe(false);
  });

  it("progress rows mix ascetic and practice into the tracker host", () => {
    const rows = buildTodayProgressRows({
      todayISO: "2026-09-22",
      habit: { id: 1, name: "Стакан воды" },
      habitStreakDays: 3,
      habitCompletedDates: ["2026-09-22"],
      ascetic: { id: 2, title: "Без сахара" },
      asceticStreakDays: 1,
      asceticCompletedDates: ["2026-09-22"],
      practiceName: "Дыхание 4-7-8",
      practiceStreakDays: 2,
      practiceCompletedDates: ["2026-09-21", "2026-09-22"],
    });
    expect(rows.map((r) => r.kind)).toEqual(["habit", "ascetic", "practice"]);
  });

  it("MY DAY extraCards host paints mixed daily rows, then drops them on unavailable", () => {
    const rows = buildTodayProgressRows({
      todayISO: "2026-09-22",
      habit: { id: 1, name: "Стакан воды" },
      habitStreakDays: 3,
      habitCompletedDates: ["2026-09-22"],
      ascetic: { id: 2, title: "Без сахара" },
      asceticStreakDays: 1,
      asceticCompletedDates: ["2026-09-22"],
      practiceName: "Дыхание 4-7-8",
      practiceStreakDays: 2,
      practiceCompletedDates: ["2026-09-22"],
    });

    const { unmount } = render(
      <TodayMyDayPane
        headline="Тезис"
        extraCards={<TodayDayTasksBlock todayTasks={[]} progressRows={rows} />}
      />,
    );
    const host = screen.getByTestId("today-day-tasks-daily");
    expect(within(host).getByTestId("today-zone-progress")).toBeInTheDocument();
    expect(within(host).getByTestId("today-progress-row-habit")).toBeInTheDocument();
    expect(within(host).getByTestId("today-progress-row-ascetic")).toBeInTheDocument();
    expect(within(host).getByTestId("today-progress-row-practice")).toBeInTheDocument();
    unmount();

    render(
      <TodayMyDayPane
        meaningUnavailable
        extraCards={<TodayDayTasksBlock todayTasks={[]} progressRows={rows} />}
      />,
    );
    expect(screen.queryByTestId("today-zone-progress")).not.toBeInTheDocument();
    expect(screen.queryByTestId("today-day-tasks")).not.toBeInTheDocument();
  });
});
