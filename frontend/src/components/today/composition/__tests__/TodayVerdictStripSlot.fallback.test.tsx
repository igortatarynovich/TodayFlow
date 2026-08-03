import { render, screen, waitFor } from "@testing-library/react";
import { TodayVerdictStripSlot } from "@/components/today/composition/TodayWave2Slots";
import { TODAY_NO_CONNECTION_COPY, TODAY_UNAVAILABLE_COPY } from "@/lib/todaySlotAvailability";

jest.mock("@/lib/todayDayFacts", () => ({
  fetchDayFacts: jest.fn(),
  clearDayFactsCache: jest.fn(),
}));

jest.mock("@/lib/todayDomainVerdicts", () => {
  const actual = jest.requireActual("@/lib/todayDomainVerdicts");
  return {
    ...actual,
    fetchDomainVerdicts: jest.fn(),
  };
});

import { fetchDayFacts } from "@/lib/todayDayFacts";

const fetchMock = fetchDayFacts as jest.MockedFunction<typeof fetchDayFacts>;

describe("TodayVerdictStripSlot transport honesty", () => {
  beforeEach(() => {
    fetchMock.mockReset();
  });

  it("shows Не удалось загрузить. when is_fallback without inventing calm rows", async () => {
    fetchMock.mockResolvedValue({
      schema_version: "day_facts_v1",
      id: "x",
      user_id: "1",
      date: "2026-07-30",
      timezone: "UTC",
      generated_at: "2026-07-30T00:00:00Z",
      natal_activations: [],
      domain_verdicts: [],
      glance_timeline: [],
      generation_provenance: {
        conflict_driver_ids: [],
        verdict_driver_ids: {},
        timeline_driver_ids: [],
      },
      is_fallback: true,
    });
    render(<TodayVerdictStripSlot dateISO="2026-07-30" />);
    await waitFor(() => {
      expect(screen.getByTestId("today-verdict-fallback")).toHaveTextContent(TODAY_UNAVAILABLE_COPY);
    });
    expect(screen.getByTestId("today-slot-verdict-strip")).toHaveAttribute("data-fallback", "true");
    expect(screen.queryByTestId("today-verdict-work")).not.toBeInTheDocument();
  });

  it("shows Нет соединения. on network throw", async () => {
    fetchMock.mockRejectedValue(new Error("Network error"));
    render(<TodayVerdictStripSlot dateISO="2026-07-30" />);
    await waitFor(() => {
      expect(screen.getByTestId("today-verdict-fallback")).toHaveTextContent(TODAY_NO_CONNECTION_COPY);
    });
    expect(screen.getByTestId("today-slot-verdict-strip")).toHaveAttribute("data-failure", "no_connection");
  });

  it("renders from parent dayFacts without calling fetchDayFacts", async () => {
    render(
      <TodayVerdictStripSlot
        dateISO="2026-07-30"
        dayFacts={{
          domain_verdicts: [
            {
              domain: "work",
              verdict: "charged",
              why_short: "Есть сопротивление — короче шаг",
              driver_ids: ["a1"],
              logic_source: "top_driver_v1",
            },
          ],
          glance_timeline: [],
          day_facts_id: "1:2026-07-30",
        }}
      />,
    );
    await waitFor(() => {
      expect(screen.getByTestId("today-verdict-work")).toBeInTheDocument();
    });
    expect(fetchMock).not.toHaveBeenCalled();
    expect(screen.getByTestId("today-verdict-why-work")).toHaveTextContent("короче шаг");
  });

  it("renders a domain icon for a known domain (FOUNDATION_UI §16.6)", async () => {
    render(
      <TodayVerdictStripSlot
        dateISO="2026-07-30"
        dayFacts={{
          domain_verdicts: [
            { domain: "work", verdict: "charged", why_short: "", driver_ids: [], logic_source: "top_driver_v1" },
            { domain: "money", verdict: "calm", why_short: "", driver_ids: [], logic_source: "top_driver_v1" },
          ],
          glance_timeline: [],
          day_facts_id: "1:2026-07-30",
        }}
      />,
    );
    await waitFor(() => {
      expect(screen.getByTestId("today-verdict-work")).toBeInTheDocument();
    });
    expect(screen.getByTestId("today-verdict-work").querySelector("svg")).not.toBeNull();
    expect(screen.getByTestId("today-verdict-money").querySelector("svg")).not.toBeNull();
  });

  it("omits the icon (not the row) for an unknown/legacy domain string", async () => {
    render(
      <TodayVerdictStripSlot
        dateISO="2026-07-30"
        dayFacts={{
          domain_verdicts: [
            {
              domain: "money_work" as never,
              verdict: "calm",
              why_short: "",
              driver_ids: [],
              logic_source: "top_driver_v1",
            },
          ],
          glance_timeline: [],
          day_facts_id: "1:2026-07-30",
        }}
      />,
    );
    await waitFor(() => {
      expect(screen.getByTestId("today-verdict-money_work")).toBeInTheDocument();
    });
    expect(screen.getByTestId("today-verdict-money_work").querySelector("svg")).toBeNull();
  });
});
