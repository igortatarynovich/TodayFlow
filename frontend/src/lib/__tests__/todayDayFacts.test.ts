import { clearDayFactsCache, fetchDayFacts } from "@/lib/todayDayFacts";
import { getJson } from "@/lib/api";

jest.mock("@/lib/api", () => ({
  getJson: jest.fn(),
}));

const getJsonMock = getJson as jest.MockedFunction<typeof getJson>;

const sample = {
  schema_version: "day_facts_v1",
  id: "2:2026-07-30",
  user_id: "2",
  date: "2026-07-30",
  timezone: "Europe/Moscow",
  generated_at: "2026-07-30T10:00:00Z",
  natal_activations: [],
  domain_verdicts: [
    {
      domain: "work",
      verdict: "calm",
      why_short: "",
      driver_ids: [],
      logic_source: "top_driver_v1",
    },
  ],
  glance_timeline: [
    {
      time_local: "2026-07-30T14:00+03:00",
      label_short: "Есть опора",
      valence: "favorable",
      driver_id: "a1",
    },
  ],
  generation_provenance: {
    conflict_driver_ids: [],
    verdict_driver_ids: { work: [] },
    timeline_driver_ids: ["a1"],
  },
  is_fallback: false,
  partial: true,
};

describe("fetchDayFacts", () => {
  beforeEach(() => {
    getJsonMock.mockReset();
    clearDayFactsCache();
  });

  it("calls GET /today/day-facts once and dedupes in-flight", async () => {
    getJsonMock.mockResolvedValue(sample);
    const a = fetchDayFacts("2026-07-30");
    const b = fetchDayFacts("2026-07-30");
    const [ra, rb] = await Promise.all([a, b]);
    expect(getJsonMock).toHaveBeenCalledTimes(1);
    expect(getJsonMock).toHaveBeenCalledWith("/today/day-facts?local_date=2026-07-30");
    expect(ra.id).toBe("2:2026-07-30");
    expect(rb.glance_timeline).toHaveLength(1);
  });

  it("serves TTL cache on second call", async () => {
    getJsonMock.mockResolvedValue(sample);
    await fetchDayFacts("2026-07-30");
    await fetchDayFacts("2026-07-30");
    expect(getJsonMock).toHaveBeenCalledTimes(1);
  });
});
