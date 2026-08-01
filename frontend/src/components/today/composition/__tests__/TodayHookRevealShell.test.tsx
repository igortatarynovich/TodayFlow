import { render, screen } from "@testing-library/react";
import { TodayHookRevealShell } from "@/components/today/composition/TodayHookRevealShell";

describe("TodayHookRevealShell", () => {
  it("does not throw when instruction is where_to_use object (pre-hydrate fallback)", () => {
    expect(() =>
      render(
        <TodayHookRevealShell
          kindLabel="Цвет дня"
          title="Янтарный"
          testId="today-zone-color-hook"
          hook={{
            kind: "color",
            base: { meaning: "тёплая энергия без суеты" },
            bridge_to_day: "якорь против срыва",
            bridge_status: "ok",
            instruction: {
              clothing: "Янтарный шарф",
              accessory: "Украшение",
            },
          }}
        />,
      ),
    ).not.toThrow();

    expect(screen.getByTestId("today-zone-color-hook")).toBeInTheDocument();
    expect(screen.getByText(/Янтарный шарф/)).toBeInTheDocument();
  });
});
