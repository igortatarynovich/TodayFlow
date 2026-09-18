import {
  buildGratitudeMemorySlot,
  eveningGratitudeStorageKey,
  loadLocalYesterdayEveningClose,
  loadYesterdayEveningClose,
  persistEveningGratitude,
} from "@/lib/todayEveningGratitude";
import { TODAY_NO_CONNECTION_COPY } from "@/lib/todaySlotAvailability";
import { getJson, postJson } from "@/lib/api";

jest.mock("@/lib/api", () => {
  const actual = jest.requireActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    postJson: jest.fn(),
    getJson: jest.fn(),
  };
});

const postJsonMock = postJson as jest.MockedFunction<typeof postJson>;
const getJsonMock = getJson as jest.MockedFunction<typeof getJson>;

describe("persistEveningGratitude", () => {
  beforeEach(() => {
    window.localStorage.clear();
    postJsonMock.mockReset();
    postJsonMock.mockResolvedValue({});
    getJsonMock.mockReset();
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
      evening_observations: {
        kind: "gratitude",
        categories: ["people", "quiet"],
        text: "тихий вечер",
        manifest_version: "today_contract_v1",
      },
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

describe("yesterday evening close for D+1", () => {
  beforeEach(() => {
    window.localStorage.clear();
    getJsonMock.mockReset();
  });

  it("builds a gratitude memory line without promise-outcome language", () => {
    const filled = buildGratitudeMemorySlot({
      dateISO: "2026-08-15",
      eveningCompleted: true,
      categories: ["quiet"],
      text: "тихий вечер",
      morningFocus: "Один разговор",
    });
    expect(filled.state).toBe("filled");
    expect(filled.body).toContain("Один разговор");
    expect(filled.body).toContain("тихий вечер");
    expect(filled.body).not.toMatch(/получилось|частично|не получилось/i);
  });

  it("omits when yesterday was not closed", () => {
    expect(buildGratitudeMemorySlot(null).state).toBe("stub");
    expect(loadLocalYesterdayEveningClose("2026-08-16")).toBeNull();
  });

  it("prefers server day-connection over local storage", async () => {
    window.localStorage.setItem(
      eveningGratitudeStorageKey("2026-08-15"),
      JSON.stringify({
        dateISO: "2026-08-15",
        categories: ["self"],
        text: "локально",
        savedAt: "2026-08-15T20:00:00.000Z",
      }),
    );
    getJsonMock.mockResolvedValue({
      date: "2026-08-15",
      evening_completed: true,
      evening_reflection: "сервер",
      evening_observations: {
        kind: "gratitude",
        categories: ["people"],
        text: "сервер",
      },
      morning_focus: "Фокус дня",
    });
    const snap = await loadYesterdayEveningClose("2026-08-16", { authenticated: true });
    expect(getJsonMock).toHaveBeenCalledWith("/day-connection/2026-08-15");
    expect(snap?.text).toBe("сервер");
    expect(snap?.morningFocus).toBe("Фокус дня");
  });
});
