import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { profileMotionStyles } from "@/components/foundation/ProfileMotion";
import { ProfileWhyScene } from "@/components/profile/v2/scenes/ProfileWhyScene";
import {
  consumeProfileMotionOnce,
  resetProfileMotionOnceForTests,
} from "@/lib/profile/profileMotionOnce";
import type { ProfileJourneyWhy } from "@/lib/profilePage/buildProfileJourneyProjection";

const why: ProfileJourneyWhy = {
  title: "Главное, что формирует тебя",
  honesty: null,
  selectedBy: [
    {
      id: "archetype_from_life_path",
      label: "Архетип Исследователя — рассчитан из числа пути 7",
      class: "selected_by",
    },
  ],
  influencedBy: [
    {
      id: "sun",
      label: "Солнце в Деве",
      class: "portrait_influenced_by",
    },
    {
      id: "moon",
      label: "Луна в Раке",
      class: "portrait_influenced_by",
    },
    {
      id: "asc",
      label: "Асцендент во Льве",
      class: "portrait_influenced_by",
    },
    {
      id: "mc",
      label: "MC в Овне",
      class: "portrait_influenced_by",
    },
  ],
};

describe("ProfileWhyScene motion accents (B)", () => {
  beforeEach(() => {
    resetProfileMotionOnceForTests();
  });

  it("expands Sun/Moon/ASC/MC meaning on tap with expanded shadow state", async () => {
    const user = userEvent.setup();
    render(<ProfileWhyScene why={why} />);

    for (const id of ["sun", "moon", "asc", "mc"] as const) {
      const card = await screen.findByTestId(`profile-v2-why-anchor-${id}`);
      expect(card).toHaveAttribute("data-expanded", "false");
      expect(card.className).toMatch(/whyProofCardInteractive/);
      await user.click(screen.getByTestId(`profile-v2-why-toggle-${id}`));
      expect(card).toHaveAttribute("data-expanded", "true");
      expect(card.className).toMatch(/whyProofCardExpanded/);
    }
  });

  it("plays Act 2 selected_by reveal once via profileMotionOnce", async () => {
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

    const { unmount } = render(<ProfileWhyScene why={why} />);
    const scene = screen.getByTestId("profile-v2-why");

    act(() => {
      observers[0]?.(
        [{ isIntersecting: true, intersectionRatio: 0.5, target: scene } as IntersectionObserverEntry],
        {} as IntersectionObserver,
      );
    });

    await waitFor(() => {
      expect(scene.className).toMatch(/reveal/);
    });

    await waitFor(() => {
      const selected = screen.getByTestId("profile-v2-why-anchor-archetype_from_life_path");
      expect(selected.className).toContain(profileMotionStyles.selectedOnceReveal);
    });
    expect(consumeProfileMotionOnce("act2-selected-by-reveal")).toBe(false);

    unmount();

    // Remount after once-key consumed: stagger, not selectedOnceReveal.
    render(<ProfileWhyScene why={why} />);
    const scene2 = screen.getByTestId("profile-v2-why");
    act(() => {
      observers[observers.length - 1]?.(
        [{ isIntersecting: true, intersectionRatio: 0.5, target: scene2 } as IntersectionObserverEntry],
        {} as IntersectionObserver,
      );
    });
    await waitFor(() => {
      expect(scene2.className).toMatch(/reveal/);
    });
    expect(
      screen.getByTestId("profile-v2-why-anchor-archetype_from_life_path").className,
    ).not.toContain(profileMotionStyles.selectedOnceReveal);

    Object.defineProperty(window, "IntersectionObserver", {
      writable: true,
      configurable: true,
      value: prev,
    });
  });
});
