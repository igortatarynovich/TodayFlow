import { render, screen } from "@testing-library/react";
import { TodayMyDayRhythm } from "@/components/today/composition/TodayMyDayRhythm";

describe("TodayMyDayRhythm", () => {
  it("omits the block when natal clocks are empty", () => {
    const { container } = render(
      <TodayMyDayRhythm dateISO="2026-08-15" glanceRows={[]} windows={[{ time: "14:30", supports: ["rest"] }]} />,
    );
    expect(container).toBeEmptyDOMElement();
    expect(screen.queryByTestId("today-my-day-rhythm")).not.toBeInTheDocument();
  });

  it("renders natal clocks with Engine action labels", () => {
    render(
      <TodayMyDayRhythm
        dateISO="2026-08-15"
        glanceRows={[
          {
            time_local: "14:20",
            label_short: "Точный аспект",
            valence: "favorable",
            driver_id: "natal-1",
          },
        ]}
        windows={[
          { time: "14:30", driver_id: "sky-1", supports: ["deep_work"], cautions: ["hard_negotiation"] },
        ]}
      />,
    );
    expect(screen.getByTestId("today-my-day-rhythm")).toBeInTheDocument();
    expect(screen.getByText(/14:20/)).toBeInTheDocument();
    expect(screen.getByText(/Глубокая работа/)).toBeInTheDocument();
  });
});
