import { contractHasPersistedPersonalDay } from "@/lib/todayContract";
import type { TodayContractV1 } from "@/lib/todayContract";
import {
  auditTodayActionSlotLock,
  auditTodayFocusSplitLock,
  auditTodayInventedFallback,
  auditTodayRitualLensLock,
} from "@/lib/todayDisplayLockAudit";
import { todayAllowsRitualLens } from "@/lib/todayScreenFlowCapability";

const base: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "p" },
  personal_growth: { development_point: "d" },
  domains: {
    work: { status: "s", opportunity: "o", risk: "r", action: "a" },
    money: { status: "s", opportunity: "o", risk: "r", action: "a" },
    relationships: { status: "s", opportunity: "o", risk: "r", action: "a" },
    energy: { status: "s", opportunity: "o", risk: "r", action: "a" },
  },
  primary_action: "a",
  progress: {},
  generation_id: "g",
};

describe("contractHasPersistedPersonalDay", () => {
  it("is false for empty, unavailable, or numerology-only identity", () => {
    expect(contractHasPersistedPersonalDay(null)).toBe(false);
    expect(contractHasPersistedPersonalDay(base)).toBe(false);
    expect(
      contractHasPersistedPersonalDay({
        ...base,
        day_story: {
          contract_version: "day_story_v1",
          interpretation_status: "unavailable",
          day_personal: { summary_ru: "Сегодня твоя ось — одно обещание." },
        },
      }),
    ).toBe(false);
    expect(
      contractHasPersistedPersonalDay({
        ...base,
        day_story: {
          contract_version: "day_story_v1",
          day_foundation: { numerology: { personal_day: 8 } },
        },
      }),
    ).toBe(false);
  });

  it("is true when natal overlay nest or why_personal is on the contract", () => {
    expect(
      contractHasPersistedPersonalDay({
        ...base,
        personal_day: { natal_overlay: { activations: [{ id: "a1" }] } },
      }),
    ).toBe(true);
    expect(
      contractHasPersistedPersonalDay({
        ...base,
        day_story: {
          contract_version: "day_story_v1",
          day_scenario: { conflict: { why_personal: "тебе обычно проще держать слово" } },
        },
      }),
    ).toBe(true);
  });
});

describe("todayAllowsRitualLens", () => {
  it("requires both capability and persist — light without nest omits", () => {
    expect(todayAllowsRitualLens("guest", {
      ...base,
      personal_day: { natal_overlay: { activations: [{ id: "a1" }] } },
    })).toBe(false);
    expect(todayAllowsRitualLens("light", base)).toBe(false);
    expect(
      todayAllowsRitualLens("light", {
        ...base,
        personal_day: { natal_overlay: { activations: [{ id: "a1" }] } },
      }),
    ).toBe(true);
  });
});

describe("auditTodayInventedFallback Grammar §9 #7", () => {
  it("flags canned fill and CE reused as Today copy", () => {
    expect(
      auditTodayInventedFallback({
        texts: ["Сегодня лучше двигаться последовательно, чем быстро."],
      }).map((f) => f.grammar),
    ).toEqual([7]);
    expect(
      auditTodayInventedFallback({
        texts: ["Замедлиться и услышать себя."],
        developmentPoint: "Замедлиться и услышать себя.",
      }).map((f) => f.grammar),
    ).toEqual([7]);
    expect(
      auditTodayInventedFallback({
        texts: ["спокойный ритм и одна главная линия."],
        developmentPoint: "Замедлиться и услышать себя.",
      }),
    ).toEqual([]);
  });
});

describe("auditTodayRitualLensLock Grammar §9", () => {
  it("flags guest lens (12) and lens without persist (15)", () => {
    expect(
      auditTodayRitualLensLock({
        depth: "guest",
        contract: base,
        lensText: "якорь дня",
      }).map((f) => f.grammar),
    ).toEqual([12, 15]);
    expect(
      auditTodayRitualLensLock({
        depth: "light",
        contract: { ...base, personal_day: { natal_overlay: { activations: [{ id: "a1" }] } } },
        lensText: "якорь дня",
      }),
    ).toEqual([]);
    expect(
      auditTodayRitualLensLock({
        depth: "light",
        contract: base,
        lensText: null,
      }),
    ).toEqual([]);
  });
});

describe("auditTodayActionSlotLock Grammar §9 #17", () => {
  it("flags primary_action reused as focus title or empty-tasks chrome next to Priority", () => {
    expect(
      auditTodayActionSlotLock({
        focusTitle: "Закрой одну задачу до 13:00",
        primaryAction: "Закрой одну задачу до 13:00",
      }).map((f) => f.grammar),
    ).toEqual([17]);
    expect(
      auditTodayActionSlotLock({
        emptyTasksChrome: true,
        priorities: ["Скажи одну конкретную просьбу."],
      }).map((f) => f.grammar),
    ).toEqual([17]);
    expect(
      auditTodayActionSlotLock({
        focusTitle: "Работа",
        primaryAction: "Закрой одну задачу до 13:00",
        priorities: ["Скажи одну конкретную просьбу."],
      }),
    ).toEqual([]);
  });
});

describe("auditTodayFocusSplitLock Grammar §9 #18", () => {
  it("flags a free-form title that repeats the headline", () => {
    expect(
      auditTodayFocusSplitLock({
        headline: "Сегодня твоя ось — одно обещание без лишнего шума.",
        focusTitle: "Сегодня твоя ось — одно обещание без лишнего шума.",
      }).map((f) => f.grammar),
    ).toEqual([18]);
    expect(
      auditTodayFocusSplitLock({
        headline: "Сегодня твоя ось — одно обещание без лишнего шума.",
        focusTitle: "Работа",
      }),
    ).toEqual([]);
  });
});
