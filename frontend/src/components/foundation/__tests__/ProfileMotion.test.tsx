import { render, screen } from "@testing-library/react";
import {
  ProfileMotionExpand,
  ProfileMotionReveal,
  ProfileMotionStagger,
  profileMotionStaggerDelay,
} from "../ProfileMotion";

describe("ProfileMotion", () => {
  it("renders reveal wrapper", () => {
    render(
      <ProfileMotionReveal delayMs={90}>
        <p>Reveal block</p>
      </ProfileMotionReveal>,
    );
    expect(screen.getByText("Reveal block")).toBeInTheDocument();
  });

  it("staggers children with 45ms steps", () => {
    const { container } = render(
      <ProfileMotionStagger baseDelayMs={120}>
        <section>A</section>
        <section>B</section>
      </ProfileMotionStagger>,
    );
    const items = container.querySelectorAll('[class*="staggerItem"]');
    expect(items).toHaveLength(2);
    expect((items[0] as HTMLElement).style.getPropertyValue("--pm-stagger")).toBe("120ms");
    expect((items[1] as HTMLElement).style.getPropertyValue("--pm-stagger")).toBe("165ms");
  });

  it("expands content when open", () => {
    const { rerender } = render(
      <ProfileMotionExpand open={false}>
        <p>Deep chart</p>
      </ProfileMotionExpand>,
    );
    expect(screen.queryByText("Deep chart")).not.toBeInTheDocument();

    rerender(
      <ProfileMotionExpand open>
        <p>Deep chart</p>
      </ProfileMotionExpand>,
    );
    expect(screen.getByText("Deep chart")).toBeInTheDocument();
  });

  it("computes stagger delay helper", () => {
    expect(profileMotionStaggerDelay(2, 60)["--pm-stagger"]).toBe("150ms");
  });
});
