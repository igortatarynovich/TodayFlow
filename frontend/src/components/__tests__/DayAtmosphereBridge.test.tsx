/**
 * @jest-environment jsdom
 */

import { act, render } from "@testing-library/react";
import { DayAtmosphereBridge } from "@/components/DayAtmosphereBridge";
import {
  DAY_ATMOSPHERE_TOKEN_KEYS,
  DAY_MODE_PIN_STORAGE_KEY,
  writeDayModePin,
} from "@/lib/dayAtmosphere";

const mockPathname = jest.fn<() => string | null>(() => "/today");

jest.mock("next/navigation", () => ({
  usePathname: () => mockPathname(),
}));

type MatchMediaListener = (event: MediaQueryListEvent) => void;

function installMatchMedia(initialMatches: boolean) {
  const listeners = new Set<MatchMediaListener>();
  let matches = initialMatches;

  const mql: MediaQueryList = {
    get matches() {
      return matches;
    },
    media: "(prefers-reduced-motion: reduce)",
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn((type: string, listener: EventListenerOrEventListenerObject) => {
      if (type === "change" && typeof listener === "function") {
        listeners.add(listener as MatchMediaListener);
      }
    }),
    removeEventListener: jest.fn((type: string, listener: EventListenerOrEventListenerObject) => {
      if (type === "change" && typeof listener === "function") {
        listeners.delete(listener as MatchMediaListener);
      }
    }),
    dispatchEvent: jest.fn(),
  };

  Object.defineProperty(window, "matchMedia", {
    writable: true,
    configurable: true,
    value: jest.fn((query: string) => {
      if (query.includes("prefers-reduced-motion")) return mql;
      return {
        matches: false,
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      };
    }),
  });

  return {
    setMatches(next: boolean) {
      matches = next;
      const event = { matches: next, media: mql.media } as MediaQueryListEvent;
      for (const listener of Array.from(listeners)) listener(event);
    },
  };
}

describe("DayAtmosphereBridge", () => {
  beforeEach(() => {
    window.localStorage.clear();
    document.documentElement.removeAttribute("data-day-mode");
    for (const key of DAY_ATMOSPHERE_TOKEN_KEYS) {
      document.documentElement.style.removeProperty(key);
    }
    mockPathname.mockReturnValue("/today");
    installMatchMedia(false);
  });

  it("sets default data-day-mode and --day-* tokens on a product route", () => {
    render(<DayAtmosphereBridge />);
    expect(document.documentElement.getAttribute("data-day-mode")).toBe("clarity");
    expect(document.documentElement.style.getPropertyValue("--day-bg-base")).toBe("#f1f2f4");
    expect(document.documentElement.style.getPropertyValue("--day-motion-duration")).not.toBe("0s");
  });

  it("does not set data-day-mode on a marketing route", () => {
    mockPathname.mockReturnValue("/");
    render(<DayAtmosphereBridge />);
    expect(document.documentElement.hasAttribute("data-day-mode")).toBe(false);
    expect(document.documentElement.style.getPropertyValue("--day-bg-base")).toBe("");
  });

  it("applies day-mode on Tarot so shell follows day atmosphere app-wide", () => {
    mockPathname.mockReturnValue("/tarot");
    render(<DayAtmosphereBridge />);
    expect(document.documentElement.getAttribute("data-day-mode")).toBe("clarity");
  });

  it("applies a pin already present at mount immediately", () => {
    writeDayModePin("grounded");
    render(<DayAtmosphereBridge />);
    expect(document.documentElement.getAttribute("data-day-mode")).toBe("grounded");
    expect(document.documentElement.style.getPropertyValue("--day-bg-base")).toBe("#f3ede1");
  });

  it("reacts to a same-key storage event from another tab", () => {
    render(<DayAtmosphereBridge />);
    expect(document.documentElement.getAttribute("data-day-mode")).toBe("clarity");

    act(() => {
      window.localStorage.setItem(DAY_MODE_PIN_STORAGE_KEY, JSON.stringify({ mode: "flow" }));
      window.dispatchEvent(
        new StorageEvent("storage", {
          key: DAY_MODE_PIN_STORAGE_KEY,
          newValue: JSON.stringify({ mode: "flow" }),
        }),
      );
    });

    expect(document.documentElement.getAttribute("data-day-mode")).toBe("flow");
  });

  it("ignores storage events for unrelated keys", () => {
    render(<DayAtmosphereBridge />);
    act(() => {
      window.dispatchEvent(
        new StorageEvent("storage", {
          key: "todayflow_mood_pin_v1",
          newValue: JSON.stringify({ mood: "night" }),
        }),
      );
    });
    expect(document.documentElement.getAttribute("data-day-mode")).toBe("clarity");
  });

  it("zeroes motion tokens when prefers-reduced-motion is already on at mount", () => {
    installMatchMedia(true);
    render(<DayAtmosphereBridge />);
    expect(document.documentElement.style.getPropertyValue("--day-motion-duration")).toBe("0s");
    expect(document.documentElement.style.getPropertyValue("--day-motion-distance")).toBe("0px");
  });

  it("zeroes motion tokens when reduced-motion turns on live", () => {
    const media = installMatchMedia(false);
    render(<DayAtmosphereBridge />);
    expect(document.documentElement.style.getPropertyValue("--day-motion-duration")).not.toBe("0s");

    act(() => {
      media.setMatches(true);
    });

    expect(document.documentElement.style.getPropertyValue("--day-motion-duration")).toBe("0s");
    expect(document.documentElement.style.getPropertyValue("--day-motion-distance")).toBe("0px");
  });

  it("clears data-day-mode and inline tokens on unmount", () => {
    const { unmount } = render(<DayAtmosphereBridge />);
    expect(document.documentElement.getAttribute("data-day-mode")).toBe("clarity");
    unmount();
    expect(document.documentElement.hasAttribute("data-day-mode")).toBe(false);
    expect(document.documentElement.style.getPropertyValue("--day-bg-base")).toBe("");
  });

  it("clears product atmosphere when navigating to a marketing route", () => {
    const { rerender } = render(<DayAtmosphereBridge />);
    expect(document.documentElement.getAttribute("data-day-mode")).toBe("clarity");

    mockPathname.mockReturnValue("/");
    rerender(<DayAtmosphereBridge />);

    expect(document.documentElement.hasAttribute("data-day-mode")).toBe(false);
  });

  it("applies engine nest from custom event; pin still wins", () => {
    const { DAY_ATMOSPHERE_ENGINE_EVENT } = require("@/lib/todayContract");
    render(<DayAtmosphereBridge />);
    expect(document.documentElement.getAttribute("data-day-mode")).toBe("clarity");

    act(() => {
      window.dispatchEvent(
        new CustomEvent(DAY_ATMOSPHERE_ENGINE_EVENT, {
          detail: {
            visual_mode: "tension",
            intensity: 0.7,
            warmth: 0.3,
            motion: "low",
            contrast: "strong",
            decor_variant: "fracture",
            time_phase: "day",
          },
        }),
      );
    });
    expect(document.documentElement.getAttribute("data-day-mode")).toBe("tension");
    expect(document.documentElement.getAttribute("data-day-decor")).toBe("fracture");

    writeDayModePin("renewal");
    act(() => {
      window.dispatchEvent(
        new StorageEvent("storage", {
          key: DAY_MODE_PIN_STORAGE_KEY,
          newValue: JSON.stringify({ mode: "renewal" }),
        }),
      );
    });
    expect(document.documentElement.getAttribute("data-day-mode")).toBe("renewal");
  });
});
