import { act, render, screen } from "@testing-library/react";
import {
  ProfileMotionExpand,
  ProfileMotionReveal,
  ProfileMotionStagger,
  profileMotionStaggerDelay,
  useProfileMotionInView,
} from "../ProfileMotion";

function InViewProbe() {
  const motion = useProfileMotionInView<HTMLDivElement>(30);
  return (
    <div ref={motion.ref} className={motion.className} style={motion.style} data-testid="in-view-probe">
      Scene
    </div>
  );
}

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

  it("reveals once when intersecting", () => {
    const observers: IntersectionObserverCallback[] = [];
    class MockObserver {
      constructor(cb: IntersectionObserverCallback) {
        observers.push(cb);
      }
      observe() {}
      disconnect() {}
      unobserve() {}
      takeRecords() {
        return [];
      }
      root = null;
      rootMargin = "";
      thresholds: number[] = [];
    }
    const prev = window.IntersectionObserver;
    Object.defineProperty(window, "IntersectionObserver", {
      writable: true,
      configurable: true,
      value: MockObserver,
    });

    render(<InViewProbe />);
    const probe = screen.getByTestId("in-view-probe");
    expect(probe.className).toMatch(/inViewPending/);

    act(() => {
      observers[0]?.(
        [{ isIntersecting: true, intersectionRatio: 0.5, target: probe } as IntersectionObserverEntry],
        {} as IntersectionObserver,
      );
    });
    expect(probe.className).toMatch(/reveal/);

    Object.defineProperty(window, "IntersectionObserver", {
      writable: true,
      configurable: true,
      value: prev,
    });
  });
});
