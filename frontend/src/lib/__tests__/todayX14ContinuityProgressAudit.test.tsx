/**
 * X14 close-out — T1.continuity and T3.tracker COMPLETE on the locked 4-surface.
 * Canon: TODAY_DISPLAY_INVENTORY_V1 T1.continuity · T3.tracker
 */
import { render, screen, within } from "@testing-library/react";
import { emitTodayDisplayFrame } from "@/lib/displayGrammar/emitTodayDisplayFrame";
import { scanDisplayGrammar } from "@/lib/displayGrammar/scanDisplayGrammar";
import type { TodayContractV1 } from "@/lib/todayContract";
import { buildTodayProgressRows, habitTrackerRows } from "@/lib/todayGrowthTrackers";
import { loadYesterdayEveningClose } from "@/lib/todayEveningGratitude";
import { TodayDayTasksBlock } from "@/components/today/composition/TodayDayTasksBlock";
import { TodayMyDayPane } from "@/components/today/composition/TodayMyDayPane";
import { TodayProgressTracker } from "@/components/today/composition/TodayProgressTracker";
import { TODAY_NO_CONNECTION_COPY } from "@/lib/todaySlotAvailability";
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
  generation_id: "x14-closeout",
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
      {
        id: "practice",
        kind: "practice",
        kind_label: "Практика",
        name: "Дыхание 4-7-8",
        streak_days: 2,
        days_bool: [false, false, false, false, false, false, true],
      },
    ],
  },
};

describe("X14 T1.continuity close-out", () => {
  it("grammar emits T1.continuity on TODAY and omits when empty", () => {
    const filled = emitTodayDisplayFrame({
      contract: persistContract,
      capability: "light",
      continuityBody: "Вчера ты отметил(а) благодарность: за спокойный момент.",
    });
    const slot = filled.atoms?.find((a) => a.slot_id === "T1.continuity");
    expect(slot?.surface).toBe("today");
    expect(slot?.text_class).toBe("user");
    expect(scanDisplayGrammar(filled)).toEqual([]);

    const withoutCaller = emitTodayDisplayFrame({
      contract: persistContract,
      capability: "light",
    });
    expect(withoutCaller.atoms?.some((a) => a.slot_id === "T1.continuity")).toBe(false);
  });

  it("GET failure with no local record is transport chrome, not empty yesterday", async () => {
    window.localStorage.clear();
    getJsonMock.mockRejectedValue(new TypeError("Failed to fetch"));
    const load = await loadYesterdayEveningClose("2026-09-22", { authenticated: true });
    expect(getJsonMock).toHaveBeenCalledWith("/day-connection/2026-09-21");
    expect(load).toEqual({ snapshot: null, failure: "no_connection" });

    const frame = emitTodayDisplayFrame({
      contract: persistContract,
      capability: "light",
      continuityFailure: load.failure,
    });
    expect(frame.atoms?.some((a) => a.slot_id === "T1.continuity")).toBe(false);
    expect(frame.atoms?.find((a) => a.slot_id === "TF.no_connection")?.text).toBe(TODAY_NO_CONNECTION_COPY);
  });
});

describe("X14 T3.tracker close-out", () => {
  it("grammar emits T3.tracker from habit rows even when MY DAY meaning is unavailable", () => {
    const frame = emitTodayDisplayFrame({
      contract: persistContract,
      capability: "light",
    });
    expect(frame.atoms?.filter((a) => a.slot_id === "T3.tracker").map((a) => a.text)).toEqual([
      "Стакан воды",
    ]);

    const unavailable = emitTodayDisplayFrame({
      contract: {
        ...persistContract,
        day_story: { contract_version: "day_story_v1", interpretation_status: "unavailable" },
      },
      capability: "light",
    });
    expect(unavailable.atoms?.some((a) => a.slot_id === "T3.unavailable")).toBe(true);
    expect(unavailable.atoms?.find((a) => a.slot_id === "T3.tracker")?.text).toBe("Стакан воды");
  });

  it("MY DAY paints habit tracker outside extraCards and keeps it on unavailable", () => {
    const rows = habitTrackerRows(
      buildTodayProgressRows({
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
      }),
    );
    expect(rows.map((r) => r.kind)).toEqual(["habit"]);

    const tracker = <TodayProgressTracker rows={rows} />;
    const extraCards = (
      <TodayDayTasksBlock
        todayTasks={[]}
        practiceSlot={<p>Практика дня</p>}
        affirmationSlot={<p>Я справлюсь с тем, что прямо сейчас.</p>}
      />
    );

    const { unmount } = render(
      <TodayMyDayPane headline="Тезис" extraCards={extraCards} tracker={tracker} />,
    );
    expect(screen.getByTestId("today-zone-progress")).toBeInTheDocument();
    expect(screen.getByTestId("today-progress-row-habit")).toBeInTheDocument();
    expect(screen.queryByTestId("today-progress-row-ascetic")).not.toBeInTheDocument();
    expect(screen.queryByTestId("today-progress-row-practice")).not.toBeInTheDocument();
    expect(screen.queryByTestId("today-day-tasks-daily")).not.toBeInTheDocument();
    unmount();

    render(
      <TodayMyDayPane meaningUnavailable extraCards={extraCards} tracker={tracker} />,
    );
    expect(screen.getByTestId("today-my-day-unavailable")).toBeInTheDocument();
    expect(screen.getByTestId("today-zone-progress")).toBeInTheDocument();
    expect(within(screen.getByTestId("today-progress-row-habit")).getByText("Стакан воды")).toBeInTheDocument();
    expect(screen.queryByTestId("today-day-tasks")).not.toBeInTheDocument();
  });
});
