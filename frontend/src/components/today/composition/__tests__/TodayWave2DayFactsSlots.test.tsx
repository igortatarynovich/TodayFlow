import { render, screen, waitFor } from "@testing-library/react";
import {
  TodayGlanceTimelineSlot,
  TodayVerdictStripSlot,
} from "@/components/today/composition/TodayWave2Slots";

jest.mock("@/lib/todayDayFacts", () => ({
  fetchDayFacts: jest.fn(),
  clearDayFactsCache: jest.fn(),
}));

import { fetchDayFacts } from "@/lib/todayDayFacts";

const fetchMock = fetchDayFacts as jest.MockedFunction<typeof fetchDayFacts>;

describe("Wave2 slots from shared day_facts payload", () => {
  beforeEach(() => {
    fetchMock.mockReset();
  });

  it("strip + timeline render from parent without double network", async () => {
    const dayFacts = {
      domain_verdicts: [
        {
          domain: "energy",
          verdict: "open",
          why_short: "Есть опора — можно опереться",
          driver_ids: ["a1"],
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
      day_facts_id: "2:2026-07-30",
    };

    render(
      <>
        <TodayVerdictStripSlot dateISO="2026-07-30" dayFacts={dayFacts} />
        <TodayGlanceTimelineSlot dateISO="2026-07-30" dayFacts={dayFacts} />
      </>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("today-verdict-energy")).toBeInTheDocument();
      expect(screen.getByTestId("today-glance-a1")).toBeInTheDocument();
    });
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
