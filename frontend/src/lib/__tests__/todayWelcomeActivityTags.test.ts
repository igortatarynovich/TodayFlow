import { resolveWelcomeActivityTags } from "@/lib/todayWelcomeActivityTags";
import type { TodayContractV1 } from "@/lib/todayContract";

describe("resolveWelcomeActivityTags", () => {
  it("prefers short day_story.do and caps at 3", () => {
    const contract = {
      day_story: { do: ["Прогулка", "Тихий звонок", "План на час", "Слишком длинная активность"] },
    } as TodayContractV1;
    expect(resolveWelcomeActivityTags({ contract })).toEqual([
      "Прогулка",
      "Тихий звонок",
      "План на час",
    ]);
  });

  it("falls back to morning priorities when do empty", () => {
    expect(
      resolveWelcomeActivityTags({
        contract: { day_story: { do: [] } } as TodayContractV1,
        morningPriorities: ["Фокус", "Отдых"],
      }),
    ).toEqual(["Фокус", "Отдых"]);
  });

  it("returns empty when no signals — never invents", () => {
    expect(resolveWelcomeActivityTags({ contract: null, morningPriorities: null })).toEqual([]);
  });
});
