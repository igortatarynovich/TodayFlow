import {
  todayDayBundleIsReady,
  type TodayDayBundle,
} from "@/lib/todayDayBundleCache";

describe("todayDayBundleIsReady", () => {
  it("requires both contract and cycle", () => {
    expect(todayDayBundleIsReady(null)).toBe(false);
    expect(
      todayDayBundleIsReady({
        savedAt: 1,
        localDate: "2026-07-25",
        contract: { contract_version: "v1" } as TodayDayBundle["contract"],
        morning: null,
        cycle: null,
      }),
    ).toBe(false);
    expect(
      todayDayBundleIsReady({
        savedAt: 1,
        localDate: "2026-07-25",
        contract: { contract_version: "v1" } as TodayDayBundle["contract"],
        morning: null,
        cycle: { date: "2026-07-25" } as TodayDayBundle["cycle"],
      }),
    ).toBe(true);
  });
});
