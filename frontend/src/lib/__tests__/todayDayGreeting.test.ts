import {
  buildTodayDayGreeting,
  pickWarmGreetingLine,
  resolveTodayDayPhase,
} from "@/lib/todayDayGreeting";

describe("todayDayGreeting", () => {
  it("resolves phases aligned with day-phase atmosphere", () => {
    expect(resolveTodayDayPhase(8)).toBe("morning");
    expect(resolveTodayDayPhase(11)).toBe("day");
    expect(resolveTodayDayPhase(14)).toBe("day");
    expect(resolveTodayDayPhase(18)).toBe("evening");
    expect(resolveTodayDayPhase(23)).toBe("night");
  });

  it("builds personalized morning greeting without day theme", () => {
    const g = buildTodayDayGreeting({
      phase: "morning",
      userName: "Игорь",
      dateISO: "2026-08-05",
      yesterdayClosed: false,
      todayOpened: false,
      tagline: "Разгонять или договариваться с телом.",
    });
    expect(g.salutation).toBe("Доброе утро, Игорь");
    expect(g.line).not.toMatch(/Разгонять|договариваться/i);
    expect(g.line.length).toBeGreaterThan(10);
  });

  it("never echoes tagline when today is already opened", () => {
    const g = buildTodayDayGreeting({
      phase: "day",
      userName: "Аня",
      dateISO: "2026-08-05",
      yesterdayClosed: false,
      todayOpened: true,
      tagline: "Разгонять или договариваться с телом.",
    });
    expect(g.salutation).toBe("Добрый день, Аня");
    expect(g.line).not.toMatch(/Разгонять|договариваться/i);
  });

  it("builds first-today continuation greeting", () => {
    const g = buildTodayDayGreeting({
      phase: "day",
      userName: "Аня",
      dateISO: "2026-08-05",
      yesterdayClosed: false,
      todayOpened: false,
      isFirstToday: true,
    });
    expect(g.salutation).toBe("Добрый день, Аня");
    expect(g.line).toMatch(/карты|первый день|спокойно/i);
  });

  it("rotates warm lines by date within a phase", () => {
    const a = pickWarmGreetingLine("morning", "2026-08-05|morning");
    const b = pickWarmGreetingLine("morning", "2026-08-06|morning");
    const c = pickWarmGreetingLine("evening", "2026-08-05|evening");
    expect(a.length).toBeGreaterThan(8);
    expect(b.length).toBeGreaterThan(8);
    expect(c).not.toBe(a);
  });

  it("uses evening salutation and warm close line", () => {
    const g = buildTodayDayGreeting({
      phase: "evening",
      userName: "Игорь",
      dateISO: "2026-08-05",
      isEveningSurface: true,
      todayOpened: true,
    });
    expect(g.salutation).toBe("Добрый вечер, Игорь");
    expect(g.line).toMatch(/вечер|день|тихим|паузы|тепло/i);
  });
});
