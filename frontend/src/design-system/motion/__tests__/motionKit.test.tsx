import { render, screen } from "@testing-library/react";
import { MotionFlip, MotionReveal, MOTION } from "@/design-system/motion";

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
