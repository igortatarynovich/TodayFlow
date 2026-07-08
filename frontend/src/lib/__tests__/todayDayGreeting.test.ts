import { buildTodayDayGreeting, resolveTodayDayPhase } from "@/lib/todayDayGreeting";

describe("todayDayGreeting", () => {
  it("resolves morning phase", () => {
    expect(resolveTodayDayPhase(8)).toBe("morning");
    expect(resolveTodayDayPhase(18)).toBe("evening");
  });

  it("builds personalized morning greeting", () => {
    const g = buildTodayDayGreeting({
      phase: "morning",
      userName: "Игорь",
      tagline: "Сегодня лучше двигаться последовательно.",
      yesterdayClosed: false,
      todayOpened: false,
    });
    expect(g.salutation).toBe("Доброе утро, Игорь");
    expect(g.line).toMatch(/темп/);
  });

  it("builds first-today continuation greeting", () => {
    const g = buildTodayDayGreeting({
      phase: "day",
      userName: "Аня",
      tagline: "Сегодня лучше двигаться последовательно.",
      yesterdayClosed: false,
      todayOpened: false,
      isFirstToday: true,
    });
    expect(g.salutation).toBe("Добрый день, Аня");
    expect(g.line).toMatch(/первые линии карты/i);
  });
});
