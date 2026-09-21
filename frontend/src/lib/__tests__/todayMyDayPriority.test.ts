import type { TodayContractV1 } from "@/lib/todayContract";
import { pickMyDayCautionLines, pickMyDayPriorityLines } from "@/lib/todayMyDayPriority";

const base: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "День ясности — спокойный ритм." },
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
  global_day: { strength: ["deep_work"], risk: ["hard_negotiation"] },
};

const persisted = {
  personal_day: { natal_overlay: { activations: [{ id: "a1" }] } },
} as const;

describe("pickMyDayPriorityLines", () => {
  it("uses Personal do[] and ignores glance Global expect", () => {
    expect(
      pickMyDayPriorityLines({
        contract: {
          ...base,
          ...persisted,
          day_story: {
            contract_version: "day_story_v1",
            do: ["Скажи одну конкретную просьбу."],
            expect: "День просит не спешить с резкими жестами.",
          },
        },
        doItems: ["Скажи одну конкретную просьбу."],
        glancePrioritize: "День просит не спешить с резкими жестами.",
      }),
    ).toEqual(["Скажи одну конкретную просьбу."]);
  });

  it("omits Global recommended_action packaged as do[] even with persist", () => {
    const rec = "Назови одну вещь прямо.";
    expect(
      pickMyDayPriorityLines({
        contract: {
          ...base,
          ...persisted,
          day_story: {
            contract_version: "day_story_v1",
            do: [rec],
            today_move: rec,
            day_scenario: {
              scenes: [{ scene_id: "s1", recommended_action: rec }],
              props: { goals: [{ text: rec, origin_scene_id: "s1" }] },
            },
          },
        },
        doItems: [rec],
        glancePrioritize: rec,
      }),
    ).toEqual([]);
  });

  it("omits Personal-looking do[] without persisted Personal Day", () => {
    expect(
      pickMyDayPriorityLines({
        contract: {
          ...base,
          day_story: {
            contract_version: "day_story_v1",
            do: ["Скажи одну конкретную просьбу."],
          },
        },
        doItems: ["Скажи одну конкретную просьбу."],
      }),
    ).toEqual([]);
  });

  it("omits glance expect and strength chip when do[] is empty", () => {
    expect(
      pickMyDayPriorityLines({
        contract: {
          ...base,
          ...persisted,
          day_story: {
            contract_version: "day_story_v1",
            expect: "День просит не спешить с резкими жестами.",
          },
        },
        doItems: [],
        glancePrioritize: "День просит не спешить с резкими жестами.",
      }),
    ).toEqual([]);
    expect(
      pickMyDayPriorityLines({
        contract: { ...base, ...persisted },
        doItems: [],
        glancePrioritize: "Глубокая работа",
      }),
    ).toEqual([]);
  });

  it("allows glance prioritize only when it is today_move and Personal Day persisted", () => {
    const move = "Назови одну просьбу до вечера, без списка условий.";
    expect(
      pickMyDayPriorityLines({
        contract: {
          ...base,
          ...persisted,
          day_story: { contract_version: "day_story_v1", today_move: move },
        },
        doItems: [],
        glancePrioritize: move,
      }),
    ).toEqual([move]);
    expect(
      pickMyDayPriorityLines({
        contract: {
          ...base,
          day_story: { contract_version: "day_story_v1", today_move: move },
        },
        doItems: [],
        glancePrioritize: move,
      }),
    ).toEqual([]);
  });

  it("omits when interpretation is unavailable", () => {
    expect(
      pickMyDayPriorityLines({
        contract: {
          ...base,
          ...persisted,
          day_story: {
            contract_version: "day_story_v1",
            interpretation_status: "unavailable",
            do: ["Скажи одну конкретную просьбу."],
            today_move: "Назови одну просьбу до вечера.",
          },
        },
        doItems: ["Скажи одну конкретную просьбу."],
        glancePrioritize: "Назови одну просьбу до вечера.",
      }),
    ).toEqual([]);
  });
});

describe("pickMyDayCautionLines", () => {
  it("uses Personal avoid[] and ignores Global do_not", () => {
    expect(
      pickMyDayCautionLines({
        contract: {
          ...base,
          ...persisted,
          day_story: {
            contract_version: "day_story_v1",
            avoid: ["Не обещай второе слово до вечера."],
            day_scenario: {
              scenes: [{ scene_id: "s1", do_not: "Не делай вид, что всё нормально." }],
            },
          },
        },
        avoidItems: ["Не обещай второе слово до вечера."],
      }),
    ).toEqual(["Не обещай второе слово до вечера."]);
  });

  it("omits Global do_not packaged as avoid[] even with persist", () => {
    const caution = "Не делай вид, что всё нормально.";
    expect(
      pickMyDayCautionLines({
        contract: {
          ...base,
          ...persisted,
          day_story: {
            contract_version: "day_story_v1",
            avoid: [caution],
            day_scenario: {
              scenes: [{ scene_id: "s1", do_not: caution, avoid_action: caution }],
            },
          },
        },
        avoidItems: [caution],
      }),
    ).toEqual([]);
  });

  it("does not invert Personal do[] into a caution", () => {
    const doLine = "Скажи одну конкретную просьбу.";
    expect(
      pickMyDayCautionLines({
        contract: {
          ...base,
          ...persisted,
          day_story: {
            contract_version: "day_story_v1",
            do: [doLine],
            avoid: [doLine],
          },
        },
        avoidItems: [doLine],
        priorityLines: [doLine],
      }),
    ).toEqual([]);
  });

  it("omits Personal-looking avoid[] without persisted Personal Day", () => {
    expect(
      pickMyDayCautionLines({
        contract: {
          ...base,
          day_story: {
            contract_version: "day_story_v1",
            avoid: ["Не обещай второе слово до вечера."],
          },
        },
        avoidItems: ["Не обещай второе слово до вечера."],
      }),
    ).toEqual([]);
  });
});
