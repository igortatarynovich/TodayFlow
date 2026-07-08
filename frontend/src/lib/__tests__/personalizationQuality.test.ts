import {
  isTodayContractFallback,
  shouldShowTodayServiceUnavailableNotice,
  TODAY_SERVICE_UNAVAILABLE_MESSAGE,
} from "@/lib/personalizationQuality";
import type { TodayContractV1 } from "@/lib/todayContract";

describe("personalizationQuality", () => {
  it("detects contract fallback generation id", () => {
    const contract = { generation_id: "fallback-today-contract-v1" } as TodayContractV1;
    expect(isTodayContractFallback(contract)).toBe(true);
    expect(
      shouldShowTodayServiceUnavailableNotice({ contract, narrativeRequestFailed: false }),
    ).toBe(true);
  });

  it("shows notice only on narrative request failure, not server-side fallback", () => {
    expect(
      shouldShowTodayServiceUnavailableNotice({ contract: null, narrativeRequestFailed: true }),
    ).toBe(true);
    expect(
      shouldShowTodayServiceUnavailableNotice({ contract: null, narrativeRequestFailed: false }),
    ).toBe(false);
  });

  it("uses network/service copy without meta language", () => {
    expect(TODAY_SERVICE_UNAVAILABLE_MESSAGE).toMatch(/нет связи с сервером/i);
    expect(TODAY_SERVICE_UNAVAILABLE_MESSAGE).not.toMatch(/базов|генерац|текст|ии|систем/i);
  });
});
