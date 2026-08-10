import { buildTodayDayTasks } from "@/lib/todayDayTasks";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { TodayProgressRow } from "@/lib/todayGrowthTrackers";

const baseContract: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "p" },
  personal_growth: { development_point: "d" },
  domains: {
    work: { status: "s", opportunity: "o", risk: "r", action: "a" },
    money: { status: "s", opportunity: "o", risk: "r", action: "a" },
    relationships: { status: "s", opportunity: "o", risk: "r", action: "a" },
    energy: { status: "s", opportunity: "o", risk: "r", action: "a" },
  },
};

const dailyRow = (id: string, name: string, kind: TodayProgressRow["kind"]): TodayProgressRow => ({
  id,
  kind,
  kindLabel: kind === "habit" ? "Привычка" : kind === "ascetic" ? "Аскеза" : "Практика",
  name,
  streakDays: 3,
  days: Array.from({ length: 7 }, (_, i) => ({
    dateISO: `2026-08-0${i + 1}`,
    completed: i < 3,
    isFuture: false,
  })),
});

describe("buildTodayDayTasks", () => {
  it("caps today assignments at 2 and separates daily progress", () => {
    const result = buildTodayDayTasks({
      contract: {
        ...baseContract,
        day_story: {
          contract_version: "day_story_v1",
          practice_recommendation: {
            kind: "ascetic",
            text: "Без сахара",
            reason: "Чище фокус",
          },
        },
      },
      practiceTitle: "Дыхание 3 минуты",
      practiceDetail: "Тихий вход",
      progressRows: [dailyRow("h1", "Вода", "habit"), dailyRow("a1", "Без новостей", "ascetic")],
      maxToday: 2,
    });

    expect(result.today).toHaveLength(2);
    expect(result.today[0].kind).toBe("practice");
    expect(result.today[1].kind).toBe("ascetic");
    expect(result.today[1].title).toBe("Без сахара");
    expect(result.daily).toHaveLength(2);
    expect(result.daily.every((t) => t.cadence === "daily")).toBe(true);
  });

  it("does not duplicate practice gift and practice recommendation", () => {
    const result = buildTodayDayTasks({
      contract: {
        ...baseContract,
        day_story: {
          contract_version: "day_story_v1",
          practice_recommendation: {
            kind: "practice",
            text: "Та же практика",
          },
        },
      },
      practiceTitle: "Та же практика",
    });
    expect(result.today).toHaveLength(1);
    expect(result.today[0].kind).toBe("practice");
  });

  it("returns empty today when no signals", () => {
    const result = buildTodayDayTasks({ contract: baseContract });
    expect(result.today).toEqual([]);
    expect(result.daily).toEqual([]);
  });
});
