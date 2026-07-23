import { redactUnrevealedRitualProse, pickPreRitualHeroTitle } from "@/lib/todayRitualRevealSanitize";

describe("todayRitualRevealSanitize", () => {
  it("strips day-number sentences before reveal", () => {
    const raw =
      "Этот день не требует размаха. Число дня — 22: ритм коротких циклов; десять параллельных входов сегодня скорее шумят, чем помогают. Ресурс около среднего.";
    const cleaned = redactUnrevealedRitualProse(raw, { numberRevealed: false, tarotRevealed: false });
    expect(cleaned).not.toMatch(/22/);
    expect(cleaned).not.toMatch(/число дня/i);
    expect(cleaned).toMatch(/размаха/i);
    expect(cleaned).toMatch(/среднего/i);
  });

  it("keeps number prose after reveal", () => {
    const raw = "Число дня — 22 задаёт ритм. Действуй спокойно.";
    expect(redactUnrevealedRitualProse(raw, { numberRevealed: true, tarotRevealed: true })).toContain("22");
  });

  it("picks short theme for pre-ritual hero", () => {
    const title = pickPreRitualHeroTitle("Общий фон дня", "Длинная история со числом дня — 7 внутри.", {
      numberRevealed: false,
      tarotRevealed: false,
    });
    expect(title).toBe("Общий фон дня");
  });
});
