import {
  dayStoryHeadline,
  dayStoryActionTitles,
  hasAuthoritativeDayStory,
  parseContractGenerationId,
  usesDayStorySingleVoice,
} from "@/lib/todayContractMapper";
import type { TodayContractV1 } from "@/lib/todayContract";

const base: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "Период" },
  personal_growth: { development_point: "Рост" },
  domains: {
    relationships: { status: "", opportunity: "", risk: "", action: "a" },
    money_work: { status: "", opportunity: "", risk: "", action: "b" },
    family: { status: "", opportunity: "", risk: "", action: "c" },
  },
  primary_action: "Шаг",
  progress: {},
  generation_id: "42",
};

describe("todayContractMapper single voice", () => {
  it("detects authoritative day_story", () => {
    expect(hasAuthoritativeDayStory(base)).toBe(false);
    expect(
      hasAuthoritativeDayStory({
        ...base,
        day_story: { contract_version: "day_story_v1", story: "Один связный текст дня." },
      }),
    ).toBe(true);
  });

  it("parses numeric generation_id for learning feedback", () => {
    expect(parseContractGenerationId({ ...base, generation_id: "128" })).toBe(128);
    expect(parseContractGenerationId({ ...base, generation_id: "fallback" })).toBeNull();
  });

  it("prefers theme for headline", () => {
    expect(
      dayStoryHeadline({
        ...base,
        day_story: {
          contract_version: "day_story_v1",
          theme: "Ясный день.",
          story: "Длинная история дня.",
        },
      }),
    ).toBe("Ясный день.");
  });

  it("usesDayStorySingleVoice mirrors hasAuthoritativeDayStory", () => {
    expect(usesDayStorySingleVoice(null)).toBe(false);
    expect(
      usesDayStorySingleVoice({
        ...base,
        day_story: { contract_version: "day_story_v1", direction: "Один фокус." },
      }),
    ).toBe(true);
  });

  it("derives ritual action titles from day_story", () => {
    expect(
      dayStoryActionTitles({
        ...base,
        primary_action: "Fallback step",
        day_story: {
          contract_version: "day_story_v1",
          today_move: "Главный шаг из story",
          do: ["Второй шаг", "Третий"],
        },
      }),
    ).toEqual(["Главный шаг из story", "Второй шаг", "Третий"]);
  });
});
