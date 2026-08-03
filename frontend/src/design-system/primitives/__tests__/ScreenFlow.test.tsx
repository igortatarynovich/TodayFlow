import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import {
  ScreenFlow,
  ScreenFlowStep,
  resolveScreenFlowEntryIndex,
} from "@/design-system/primitives/ScreenFlow";

function Harness({ axis = "x" as const, initial = 0 }: { axis?: "x" | "y"; initial?: number }) {
  const [index, setIndex] = useState(initial);
  return (
    <ScreenFlow activeIndex={index} axis={axis} onIndexChange={(next) => setIndex(next)}>
      <ScreenFlowStep id="a" label="Альфа"><p>Content A</p></ScreenFlowStep>
      <ScreenFlowStep id="b" label="Бета"><p>Content B</p></ScreenFlowStep>
      <ScreenFlowStep id="c" label="Гамма" status="pending" />
      <ScreenFlowStep id="d" label="Дельта" status="failed" />
    </ScreenFlow>
  );
}

describe("ScreenFlow", () => {
  it("moves focus to heading and updates aria-live on dot select", async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByTestId("screen-flow-dot-1"));
    await waitFor(() => {
      expect(document.activeElement).toBe(screen.getByTestId("screen-flow-heading-b"));
    });
    expect(screen.getByTestId("screen-flow-live")).toHaveTextContent("Шаг 2 из 4: Бета");
    expect(screen.queryByTestId("screen-flow-next")).not.toBeInTheDocument();
    expect(screen.queryByTestId("screen-flow-prev")).not.toBeInTheDocument();
  });

  it("does not invent content for failed/pending steps", () => {
    const { unmount } = render(<Harness initial={2} />);
    expect(screen.getByTestId("screen-flow-skeleton-c")).toBeInTheDocument();
    unmount();
    render(<Harness initial={3} />);
    expect(screen.getByTestId("screen-flow-fail-d")).toHaveTextContent("Нет соединения.");
  });

  it("supports both axes on the primitive; Today locks x", () => {
    const { rerender } = render(<Harness axis="x" />);
    expect(screen.getByTestId("screen-flow")).toHaveAttribute("data-axis", "x");
    rerender(<Harness axis="y" />);
    expect(screen.getByTestId("screen-flow")).toHaveAttribute("data-axis", "y");
  });

  it("exports locked Today axis and edge deadzone", async () => {
    const mod = await import("@/design-system/primitives/ScreenFlow");
    expect(mod.TODAY_SCREEN_FLOW_AXIS).toBe("x");
    expect(mod.SCREEN_FLOW_EDGE_DEADZONE_PX).toBe(24);
  });
});

describe("resolveScreenFlowEntryIndex", () => {
  it("defaults to 0 without deep-link intent", () => {
    expect(resolveScreenFlowEntryIndex({ searchParams: new URLSearchParams("step=3"), stepCount: 6 })).toBe(0);
  });

  it("honors explicit deep-link", () => {
    expect(resolveScreenFlowEntryIndex({ searchParams: new URLSearchParams("sf=1&step=3"), stepCount: 6 })).toBe(3);
  });
});
