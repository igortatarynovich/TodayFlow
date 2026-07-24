import { render, screen } from "@testing-library/react";
import { MotionDrift, MotionFlip, MotionPulse, MotionReveal, MotionSettle, MOTION } from "@/design-system/motion";

describe("design-system/motion", () => {
  it("exposes FOUNDATION_UI §7 token durations", () => {
    expect(MOTION.microMs).toBe(150);
    expect(MOTION.revealMs).toBe(280);
    expect(MOTION.cardMs).toBe(320);
    expect(MOTION.pageMs).toBe(420);
    expect(MOTION.staggerMs).toBe(45);
  });

  it("MotionReveal renders children under reduced motion", () => {
    render(
      <MotionReveal reducedMotion>
        <span>insight</span>
      </MotionReveal>,
    );
    expect(screen.getByText("insight")).toBeInTheDocument();
  });

  it("MotionSettle / MotionDrift / MotionPulse render children under reduced motion", () => {
    render(
      <>
        <MotionSettle reducedMotion>
          <span>settle-card</span>
        </MotionSettle>
        <MotionDrift reducedMotion>
          <span>drift-orbit</span>
        </MotionDrift>
        <MotionPulse reducedMotion>
          <span>pulse-cta</span>
        </MotionPulse>
        <MotionPulse active={false}>
          <span>pulse-paused</span>
        </MotionPulse>
      </>,
    );
    expect(screen.getByText("settle-card")).toBeInTheDocument();
    expect(screen.getByText("drift-orbit")).toBeInTheDocument();
    expect(screen.getByText("pulse-cta")).toBeInTheDocument();
    expect(screen.getByText("pulse-paused")).toBeInTheDocument();
  });

  it("MotionFlip shows back then face by flipped prop (reduced)", () => {
    const { rerender } = render(
      <MotionFlip
        flipped={false}
        reducedMotion
        back={<span>back</span>}
        front={<span>front</span>}
      />,
    );
    expect(screen.getByText("back")).toBeInTheDocument();
    expect(screen.queryByText("front")).not.toBeInTheDocument();

    rerender(
      <MotionFlip
        flipped
        reducedMotion
        back={<span>back</span>}
        front={<span>front</span>}
      />,
    );
    expect(screen.getByText("front")).toBeInTheDocument();
    expect(screen.getByTestId("motion-flip")).toHaveAttribute("data-flipped", "true");
  });
});
