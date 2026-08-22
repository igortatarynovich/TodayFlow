import { render, screen } from "@testing-library/react";
import { TodayMyDayPane } from "@/components/today/composition/TodayMyDayPane";
import { TODAY_UNAVAILABLE_COPY } from "@/lib/todaySlotAvailability";

describe("TodayMyDayPane", () => {
  it("omits leftover focus, timeline and color when meaning is unavailable", () => {
    render(
      <TodayMyDayPane
        meaningUnavailable
        headline="Не удалось загрузить."
        focusTitle="Ровный продуктивный ритм."
        focusBody="Не удалось загрузить."
        priorities={["Не удалось загрузить."]}
        timeline={<div data-testid="today-my-day-rhythm">таймлайн</div>}
        colorCard={<div data-testid="today-zone-color-guide">Янтарный</div>}
      />,
    );
    expect(screen.getByTestId("today-my-day-unavailable")).toHaveTextContent(TODAY_UNAVAILABLE_COPY);
    expect(screen.queryByTestId("today-handoff-focus")).not.toBeInTheDocument();
    expect(screen.queryByTestId("today-my-day-rhythm")).not.toBeInTheDocument();
    expect(screen.queryByTestId("today-zone-color-guide")).not.toBeInTheDocument();
    expect(screen.queryByText("Ровный продуктивный ритм.")).not.toBeInTheDocument();
    expect(screen.queryByText("Янтарный")).not.toBeInTheDocument();
  });
});
