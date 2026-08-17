import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import {
  ScreenFlow,
  ScreenFlowStep,
  resolveScreenFlowEntryIndex,
} from "@/design-system/primitives/ScreenFlow";

function Harness({
  axis = "x" as const,
  initial = 0,
  withButton = false,
}: {
  axis?: "x" | "y";
  initial?: number;
  withButton?: boolean;
}) {
  const [index, setIndex] = useState(initial);
  return (
    <ScreenFlow activeIndex={index} axis={axis} onIndexChange={(next) => setIndex(next)}>
      <ScreenFlowStep id="a" label="Альфа">
        {withButton ? <button type="button">Открыть число</button> : <p>Content A</p>}
      </ScreenFlowStep>
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

  it("does not swipe when the gesture starts on a button", () => {
    render(<Harness withButton />);
    const btn = screen.getByRole("button", { name: "Открыть число" });
    const viewport = screen.getByTestId("screen-flow-viewport");
    fireEvent.touchStart(btn, { changedTouches: [{ identifier: 1, clientX: 220, clientY: 120 }] });
    fireEvent.touchEnd(viewport, { changedTouches: [{ identifier: 1, clientX: 40, clientY: 120 }] });
    expect(screen.getByTestId("screen-flow")).toHaveAttribute("data-active-index", "0");
  });

  it("swipes to the next step from the pane", () => {
    render(<Harness />);
    const viewport = screen.getByTestId("screen-flow-viewport");
    fireEvent.touchStart(viewport, { changedTouches: [{ identifier: 1, clientX: 220, clientY: 120 }] });
    fireEvent.touchEnd(viewport, { changedTouches: [{ identifier: 1, clientX: 40, clientY: 120 }] });
    expect(screen.getByTestId("screen-flow")).toHaveAttribute("data-active-index", "1");
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
