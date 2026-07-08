import { postTodayNarrative } from "@/lib/todayNarrativeApi";
import {
  buildTodayNarrativeCacheKey,
  clearTodayNarrativeCache,
  fetchTodayNarrativeCached,
  readTodayNarrativeCache,
  ritualContextFingerprint,
  writeTodayNarrativeCache,
} from "@/lib/todayNarrativeCache";

jest.mock("@/lib/todayNarrativeApi", () => ({
  postTodayNarrative: jest.fn(),
}));

const mockedPost = postTodayNarrative as jest.MockedFunction<typeof postTodayNarrative>;

const guideBody = {
  target_date: "2026-07-08",
  surface: "guide" as const,
};

const guideResponse = {
  generation_id: 42,
  generation_log_id: 42,
  surface: "guide",
  used_fallback: false,
  payload: { headline: "cached guide" },
};

describe("todayNarrativeCache", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    sessionStorage.clear();
    clearTodayNarrativeCache();
  });

  it("builds stable cache keys from ritual context fingerprint", () => {
    expect(
      buildTodayNarrativeCacheKey({
        ...guideBody,
        ritual_context: {
          tarot_main_id: 3,
          numerology_value: "7",
          mood: "calm",
          head_topic: "focus",
        },
      }),
    ).toBe("2026-07-08|guide|-1|||3|7|calm|focus");
    expect(ritualContextFingerprint(null)).toBe("");
  });

  it("returns sessionStorage hit without network", async () => {
    writeTodayNarrativeCache(guideBody, guideResponse);
    const hit = await fetchTodayNarrativeCached(guideBody);
    expect(hit).toEqual(guideResponse);
    expect(mockedPost).not.toHaveBeenCalled();
  });

  it("coalesces in-flight requests for the same key", async () => {
    let resolvePost!: (v: typeof guideResponse) => void;
    mockedPost.mockReturnValueOnce(
      new Promise((resolve) => {
        resolvePost = resolve;
      }),
    );

    const p1 = fetchTodayNarrativeCached(guideBody);
    const p2 = fetchTodayNarrativeCached(guideBody);
    resolvePost(guideResponse);

    const [r1, r2] = await Promise.all([p1, p2]);
    expect(r1).toEqual(guideResponse);
    expect(r2).toEqual(guideResponse);
    expect(mockedPost).toHaveBeenCalledTimes(1);
  });

  it("force bypasses cache and writes a fresh entry", async () => {
    writeTodayNarrativeCache(guideBody, guideResponse);
    const fresh = {
      ...guideResponse,
      generation_id: 99,
      payload: { headline: "fresh" },
    };
    mockedPost.mockResolvedValueOnce(fresh);

    const hit = await fetchTodayNarrativeCached(guideBody, { force: true });
    expect(hit.generation_id).toBe(99);
    expect(mockedPost).toHaveBeenCalledTimes(1);
    expect(readTodayNarrativeCache(guideBody)?.generation_id).toBe(99);
  });

  it("clears entries for a specific date", () => {
    writeTodayNarrativeCache(guideBody, guideResponse);
    writeTodayNarrativeCache(
      { target_date: "2026-07-09", surface: "guide" },
      { ...guideResponse, generation_id: 2 },
    );
    clearTodayNarrativeCache("2026-07-08");
    expect(readTodayNarrativeCache(guideBody)).toBeNull();
    expect(
      readTodayNarrativeCache({ target_date: "2026-07-09", surface: "guide" })?.generation_id,
    ).toBe(2);
  });
});
