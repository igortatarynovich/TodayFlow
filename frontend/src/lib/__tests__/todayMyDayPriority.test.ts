import type { TodayContractV1 } from "@/lib/todayContract";
import { pickMyDayPriorityLines } from "@/lib/todayMyDayPriority";

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
