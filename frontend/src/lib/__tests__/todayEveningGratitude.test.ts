import { persistEveningGratitude } from "@/lib/todayEveningGratitude";
import { TODAY_NO_CONNECTION_COPY } from "@/lib/todaySlotAvailability";
import { postJson } from "@/lib/api";

jest.mock("@/lib/api", () => {
  const actual = jest.requireActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    postJson: jest.fn(),
  };
});

const postJsonMock = postJson as jest.MockedFunction<typeof postJson>;

describe("persistEveningGratitude", () => {
  beforeEach(() => {
    window.localStorage.clear();
    postJsonMock.mockReset();
    postJsonMock.mockResolvedValue({});
  });

  it("writes local record and journal + day-connection without rewriting the day", async () => {
    const result = await persistEveningGratitude({
      dateISO: "2026-08-15",
      categories: ["people", "quiet"],
      text: "тихий вечер",
      manifestVersion: "today_contract_v1",
    });
    expect(result).toEqual({ ok: true });
    expect(postJsonMock).toHaveBeenCalledWith("/journal/entries", {
      type: "gratitude",
      content: expect.stringContaining("тихий вечер"),
      day: "2026-08-15",
    });
    expect(postJsonMock).toHaveBeenCalledWith("/day-connection/2026-08-15", {
      evening_completed: true,
      evening_reflection: expect.stringContaining("тихий вечер"),
    });
    const stored = JSON.parse(
      window.localStorage.getItem("todayflow_evening_gratitude_v1:2026-08-15") || "null",
    );
    expect(stored.categories).toEqual(["people", "quiet"]);
    expect(stored.text).toBe("тихий вечер");
  });

  it("says Нет соединения. on transport failure", async () => {
    postJsonMock.mockRejectedValue(new TypeError("Failed to fetch"));
    const result = await persistEveningGratitude({
      dateISO: "2026-08-15",
      categories: ["self"],
      text: "",
    });
    expect(result).toEqual({ ok: false, reason: "no_connection" });
    expect(TODAY_NO_CONNECTION_COPY).toMatch(/^Нет соединения\.?$/);
  });
});
