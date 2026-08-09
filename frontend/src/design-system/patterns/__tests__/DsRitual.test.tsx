import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { DsChipGroup, DsGlassCard, DsHabitStreakRow } from "@/design-system/patterns/DsRitual";

describe("DsRitual primitives", () => {
  it("renders glass card and chip selection", async () => {
    const user = userEvent.setup();
    const onSelect = jest.fn();
    render(
      <DsGlassCard testId="glass">
        <DsChipGroup
          options={[
            { id: "a", label: "Фокус", sub: "работа" },
            { id: "b", label: "Энергия", sub: "темп" },
          ]}
          selected="a"
          onSelect={onSelect}
          testId="chips"
        />
      </DsGlassCard>,
    );
    expect(screen.getByTestId("glass")).toBeInTheDocument();
    await user.click(screen.getByTestId("ds-chip-b"));
    expect(onSelect).toHaveBeenCalledWith("b");
  });

  it("renders habit streak dots from boolean days", () => {
    render(
      <DsHabitStreakRow
        name="Тишина"
        kind="Практика"
        streakLabel="3 дн."
        days={[true, true, true, false, false, false, false]}
        testId="streak"
      />,
    );
    expect(screen.getByTestId("streak")).toHaveTextContent("Тишина");
    expect(screen.getByTestId("streak").querySelectorAll('[data-done="true"]')).toHaveLength(3);
  });
});
