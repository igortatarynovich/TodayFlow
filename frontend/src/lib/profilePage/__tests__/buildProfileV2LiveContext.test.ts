import {
  buildProfileV2DailyAnchors,
  buildProfileV2LiveContext,
  resolveProfileV2AwarenessPercent,
} from "../buildProfileV2LiveContext";
import type { MorningRitualData } from "@/components/today/todayPageUtils";
import type { CompactUserModel, CoreProfile } from "@/lib/types";

const morningRitual = {
  celestial_events: {
    daily_symbols: {
      stone: { name: "Лабрадорит", story_ru: "Держит фокус без спешки." },
      color: { name: "Оливковый" },
      totem: { name: "Сова", emoji: "🦉", story_ru: "Наблюдение." },
    },
    personal_transits: [{ title: "Меркурий" }],
  },
} as MorningRitualData;

describe("buildProfileV2LiveContext", () => {
  it("builds daily anchors from morning ritual API shape", () => {
    const anchors = buildProfileV2DailyAnchors(morningRitual);
    expect(anchors.stoneName).toBe("Лабрадорит");
    expect(anchors.line).toContain("Лабрадорит");
    expect(anchors.line).toContain("Оливковый");
    expect(anchors.line).toContain("Меркурий");
  });

  it("prefers CUM confidence for awareness percent", () => {
    const cum = { confidence: { overall: 0.68 } } as CompactUserModel;
    expect(
      resolveProfileV2AwarenessPercent({ cum, coreProfile: null, localClosedDays: 0 }),
    ).toBe(68);
  });

  it("uses stone story and CUM recommendation in live cards", () => {
    const cum = {
      generated_at: "2026-07-07T07:14:00.000Z",
      confidence: { overall: 0.68, delta_30d: 0.03 },
      recommendations: { primary: { id: "p1", text: "Один сложный разговор до 14:00." } },
      behavioral_patterns: { hints: ["точность", "глубина"], works: [], does_not_work: [] },
    } as CompactUserModel;

    const live = buildProfileV2LiveContext({
      coreProfile: { generated_at: "2026-07-06T10:00:00.000Z" } as CoreProfile,
      cum,
      morningRitual,
      thriveAreas: ["ритм"],
      identitySummary: "Видит связи раньше событий.",
    });

    expect(live.awarenessPercent).toBe(68);
    expect(live.awarenessDeltaLabel).toBe("+3 за 30 дн");
    expect(live.stoneCardTitle).toContain("лабрадорит");
    expect(live.stoneCardBody).toBe("Держит фокус без спешки.");
    expect(live.supportsCardBody).toBe("Один сложный разговор до 14:00.");
    expect(live.helps).toEqual(["Один сложный разговор до 14:00.", "точность", "глубина"]);
  });

  it("uses personal_transits[0] only for planet anchor", () => {
    const anchors = buildProfileV2DailyAnchors({
      celestial_events: {
        daily_symbols: { stone: { name: "X" }, color: { name: "Y" }, totem: { name: "Z", emoji: "🦉" } },
        personal_transits: [],
        retrogrades: [{ planet_ru: "Меркурий" }],
      },
    } as MorningRitualData);
    expect(anchors.planetName).toBeNull();
    expect(anchors.line).not.toContain("Меркурий");
  });
});
