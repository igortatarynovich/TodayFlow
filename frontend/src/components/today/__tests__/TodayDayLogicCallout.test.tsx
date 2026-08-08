import { render, screen } from "@testing-library/react";
import { TodayDayLogicCallout } from "@/components/today/TodayDayLogicCallout";

describe("TodayDayLogicCallout → DsCallout pilot", () => {
  it("renders day engine brief inside semantic callout", () => {
    render(
      <TodayDayLogicCallout
        variant="ritual"
        dayEngineBrief={{
          anchor: "Держи одну линию до обеда.",
          hints: ["Не раздувай тему."],
        }}
        dayModelBrief={null}
      />,
    );
    expect(screen.getByTestId("today-day-logic-callout")).toHaveAttribute("data-tone", "insight");
    expect(screen.getByText("Держи одну линию до обеда.")).toBeInTheDocument();
    expect(screen.getByText("Не раздувай тему.")).toBeInTheDocument();
  });

  it("renders day model focus when engine brief absent", () => {
    render(
      <TodayDayLogicCallout
        variant="guide"
        dayEngineBrief={null}
        dayModelBrief={{
          contractVersion: "day_model_v0",
          vectorSummary: "Вектор: ясность.",
          oneFocus: "Один разговор.",
        }}
      />,
    );
    expect(screen.getByTestId("today-day-logic-callout")).toBeInTheDocument();
    expect(screen.getByText("Вектор: ясность.")).toBeInTheDocument();
    expect(screen.getByText(/Один разговор/)).toBeInTheDocument();
  });

  it("returns null without briefs", () => {
    const { container } = render(
      <TodayDayLogicCallout variant="ritual" dayEngineBrief={null} dayModelBrief={null} />,
    );
    expect(container).toBeEmptyDOMElement();
  });
});
