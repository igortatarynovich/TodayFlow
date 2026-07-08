import { render, screen } from "@testing-library/react";
import { TodayDayLogicCallout } from "@/components/today/TodayDayLogicCallout";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";

describe("TodayDayLogicCallout", () => {
  it("renders nothing when both briefs are null", () => {
    const { container } = render(
      <TodayDayLogicCallout variant="ritual" dayEngineBrief={null} dayModelBrief={null} />,
    );
    expect(container.firstChild).toBeNull();
  });

  it("renders day engine eyebrow, anchor and hints (ritual)", () => {
    render(
      <TodayDayLogicCallout
        variant="ritual"
        dayEngineBrief={{ anchor: "Ось дня — завершение.", hints: ["Шаг один", "Шаг два"] }}
        dayModelBrief={null}
      />,
    );
    expect(screen.getByText(RITUAL_COPY.dayEngineBriefEyebrow)).toBeInTheDocument();
    expect(screen.getByText("Ось дня — завершение.")).toBeInTheDocument();
    expect(screen.getByText("Шаг один")).toBeInTheDocument();
    expect(screen.getByText("Шаг два")).toBeInTheDocument();
  });

  it("renders engine block with nested day model one focus and vector (guide)", () => {
    render(
      <TodayDayLogicCallout
        variant="guide"
        dayEngineBrief={{ anchor: "Якорь", hints: [] }}
        dayModelBrief={{
          contractVersion: "day_model_v0",
          oneFocus: "Закрыть одну задачу",
          vectorSummary: "Вектор: ровный темп.",
        }}
      />,
    );
    expect(screen.getByText("Якорь")).toBeInTheDocument();
    expect(screen.getByText("Вектор: ровный темп.")).toBeInTheDocument();
    expect(screen.getByText(/Закрыть одну задачу/)).toBeInTheDocument();
    expect(screen.getByText(new RegExp(`${RITUAL_COPY.dayModelOneFocusLabel}:`))).toBeInTheDocument();
  });

  it("renders only day model when engine is null (ritual)", () => {
    render(
      <TodayDayLogicCallout
        variant="ritual"
        dayEngineBrief={null}
        dayModelBrief={{
          contractVersion: "day_model_v0",
          oneFocus: "Только фокус",
          vectorSummary: "Краткий вектор",
        }}
      />,
    );
    expect(screen.getByText(RITUAL_COPY.dayModelBriefEyebrow)).toBeInTheDocument();
    expect(screen.queryByText(RITUAL_COPY.dayEngineBriefEyebrow)).not.toBeInTheDocument();
    expect(screen.getByText("Краткий вектор")).toBeInTheDocument();
    expect(screen.getByText(/Только фокус/)).toBeInTheDocument();
  });
});
