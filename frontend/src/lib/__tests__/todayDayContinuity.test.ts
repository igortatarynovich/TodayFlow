import {
  buildContinuityOpeningLine,
  buildMemorySlotCopy,
  buildTomorrowContinuityHook,
  dayContinuityStorageKey,
  formatDayContinuityDateRu,
  isDayContinuityClosed,
  listClosedDayContinuityRecords,
  normalizeDayContinuityRecord,
  outcomeLabelRu,
  previousDateISO,
  saveDayContinuity,
} from "@/lib/todayDayContinuity";

describe("todayDayContinuity", () => {
  it("previousDateISO steps back one calendar day", () => {
    expect(previousDateISO("2026-06-23")).toBe("2026-06-22");
  });

  it("isDayContinuityClosed requires outcome and closedAt", () => {
    expect(isDayContinuityClosed(null)).toBe(false);
    expect(
      isDayContinuityClosed({
        dateISO: "2026-06-23",
        mainFocus: "Один фокус",
        outcome: "done",
        closedAt: "2026-06-23T20:00:00.000Z",
      }),
    ).toBe(true);
    expect(
      isDayContinuityClosed({
        dateISO: "2026-06-23",
        mainFocus: "Один фокус",
      }),
    ).toBe(false);
  });

  it("buildContinuityOpeningLine uses focus and outcome", () => {
    const line = buildContinuityOpeningLine({
      dateISO: "2026-06-22",
      mainFocus: "Разговор с командой",
      outcome: "partial",
      closedAt: "2026-06-22T20:00:00.000Z",
    });
    expect(line).toContain("Разговор с командой");
    expect(line).toMatch(/частично/i);
  });

  it("outcomeLabelRu matches WEB_LAUNCH soft close labels", () => {
    expect(outcomeLabelRu("done")).toBe("Получилось");
    expect(outcomeLabelRu("partial")).toBe("Частично");
    expect(outcomeLabelRu("not_done")).toBe("Не получилось");
  });

  it("buildTomorrowContinuityHook is stable WEB_LAUNCH copy", () => {
    expect(buildTomorrowContinuityHook()).toMatch(/Завтра утром TodayFlow начнёт/);
  });

  it("buildMemorySlotCopy stubs without yesterday and fills when closed", () => {
    const stub = buildMemorySlotCopy(null);
    expect(stub.state).toBe("stub");
    expect(stub.body).toMatch(/вечером закрой/i);

    const filled = buildMemorySlotCopy({
      dateISO: "2026-06-22",
      mainFocus: "Один шаг",
      outcome: "done",
      closedAt: "2026-06-22T20:00:00.000Z",
    });
    expect(filled.state).toBe("filled");
    expect(filled.body).toContain("Один шаг");
    expect(filled.body).toMatch(/получилось/i);
  });

  it("normalizeDayContinuityRecord rejects empty focus", () => {
    expect(normalizeDayContinuityRecord({ mainFocus: "  " }, "2026-06-23")).toBeNull();
    expect(
      normalizeDayContinuityRecord({ mainFocus: "Фокус", outcome: "done" }, "2026-06-23")?.mainFocus,
    ).toBe("Фокус");
  });

  it("listClosedDayContinuityRecords returns newest closed days up to limit", () => {
    window.localStorage.clear();
    saveDayContinuity({
      dateISO: "2026-06-20",
      mainFocus: "Старый день",
      outcome: "done",
      closedAt: "2026-06-20T20:00:00.000Z",
    });
    saveDayContinuity({
      dateISO: "2026-06-22",
      mainFocus: "Разговор",
      outcome: "partial",
      closedAt: "2026-06-22T20:00:00.000Z",
    });
    saveDayContinuity({
      dateISO: "2026-06-21",
      mainFocus: "Черновик без закрытия",
    });
    saveDayContinuity({
      dateISO: "2026-06-23",
      mainFocus: "Сегодня",
      outcome: "done",
      closedAt: "2026-06-23T20:00:00.000Z",
    });

    const rows = listClosedDayContinuityRecords(3);
    expect(rows).toHaveLength(3);
    expect(rows[0]?.dateISO).toBe("2026-06-23");
    expect(rows[1]?.dateISO).toBe("2026-06-22");
    expect(rows[2]?.dateISO).toBe("2026-06-20");
  });

  it("formatDayContinuityDateRu renders Russian month", () => {
    expect(formatDayContinuityDateRu("2026-06-23")).toMatch(/23/);
    expect(dayContinuityStorageKey("2026-06-23")).toContain("2026-06-23");
  });
});
