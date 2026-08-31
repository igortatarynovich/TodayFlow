import {
  contractHasDeterministicPersonalDayForMyDay,
  isDayNotReady,
  isTodayInterpretationUnavailable,
  localCalendarDateISO,
  readDayLifecycle,
  type TodayContractV1,
} from "@/lib/todayContract";

describe("day lifecycle C5 helpers", () => {
  it("detects day_not_ready by generation_id and progress", () => {
    const byId = {
      generation_id: "day-not-ready-c5",
      progress: {},
    } as TodayContractV1;
    expect(isDayNotReady(byId)).toBe(true);

    const byStatus = {
      generation_id: "329",
      progress: { day_lifecycle: { status: "day_not_ready", ready_time: "05:00" } },
    } as TodayContractV1;
    expect(isDayNotReady(byStatus)).toBe(true);
    expect(readDayLifecycle(byStatus)?.ready_time).toBe("05:00");

    const ready = {
      generation_id: "329",
      progress: { day_lifecycle: { status: "ready" } },
    } as TodayContractV1;
    expect(isDayNotReady(ready)).toBe(false);
  });

  it("detects Personal Day interpretation unavailable", () => {
    const unavailable = {
      generation_id: "1",
      progress: { interpretation_status: "unavailable" },
      day_story: { contract_version: "day_story_v1", interpretation_status: "unavailable" },
    } as TodayContractV1;
    expect(isTodayInterpretationUnavailable(unavailable)).toBe(true);
    expect(
      isTodayInterpretationUnavailable({
        generation_id: "1",
        day_story: { contract_version: "day_story_v1", interpretation_status: "ok" },
      } as TodayContractV1),
    ).toBe(false);
  });

  it("detects deterministic personal day material regardless of interpretation_status", () => {
    const unavailableButPersonal = {
      generation_id: "1",
      day_story: {
        contract_version: "day_story_v1",
        interpretation_status: "unavailable",
        day_personal: {
          contract_version: "day_personal_v1",
          summary_ru: "Транзит Солнца активирует натальную Венеру.",
        },
      },
    } as TodayContractV1;
    expect(contractHasDeterministicPersonalDayForMyDay(unavailableButPersonal)).toBe(true);

    const noPersonal = {
      generation_id: "1",
      day_story: {
        contract_version: "day_story_v1",
        interpretation_status: "unavailable",
      },
    } as TodayContractV1;
    expect(contractHasDeterministicPersonalDayForMyDay(noPersonal)).toBe(false);
  });

  it("localCalendarDateISO matches local Y-M-D", () => {
    const d = new Date(2026, 6, 27, 1, 30, 0); // Jul 27 local
    expect(localCalendarDateISO(d)).toBe("2026-07-27");
  });
});
