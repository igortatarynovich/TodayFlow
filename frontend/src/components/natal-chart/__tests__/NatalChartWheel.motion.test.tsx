import { act, render, screen, waitFor } from "@testing-library/react";
import { NatalChartWheel } from "@/components/natal-chart/NatalChartWheel";
import { PROFILE_DECODE_PATTERN_WAVE_EVENT } from "@/lib/profile/profileMotionOnce";

const CHART = [
  { body: "Sun", sign: "Aquarius", house: 8, degree: 25.4, longitude: 325.4 },
  { body: "Moon", sign: "Libra", house: 4, degree: 12.1, longitude: 192.1 },
  { body: "Mercury", sign: "Aquarius", house: 8, degree: 28.9, longitude: 328.9 },
  { body: "Venus", sign: "Capricorn", house: 7, degree: 3.2, longitude: 273.2 },
  { body: "Mars", sign: "Capricorn", house: 7, degree: 8.7, longitude: 278.7 },
  { body: "Jupiter", sign: "Cancer", house: 1, degree: 19.5, longitude: 109.5 },
  { body: "Saturn", sign: "Capricorn", house: 7, degree: 14.3, longitude: 284.3 },
];

const HOUSES: Record<string, { sign: string; degree: number; cusp_longitude: number }> = {
  house_1: { sign: "Cancer", degree: 24, cusp_longitude: 114 },
  house_2: { sign: "Leo", degree: 18, cusp_longitude: 138 },
  house_3: { sign: "Virgo", degree: 14, cusp_longitude: 164 },
  house_4: { sign: "Libra", degree: 14, cusp_longitude: 194 },
  house_5: { sign: "Scorpio", degree: 18, cusp_longitude: 228 },
  house_6: { sign: "Sagittarius", degree: 24, cusp_longitude: 264 },
  house_7: { sign: "Capricorn", degree: 24, cusp_longitude: 294 },
  house_8: { sign: "Aquarius", degree: 18, cusp_longitude: 318 },
  house_9: { sign: "Pisces", degree: 14, cusp_longitude: 344 },
  house_10: { sign: "Aries", degree: 14, cusp_longitude: 14 },
  house_11: { sign: "Taurus", degree: 18, cusp_longitude: 48 },
  house_12: { sign: "Gemini", degree: 24, cusp_longitude: 84 },
};

describe("NatalChartWheel motion accents (B)", () => {
  it("plays aspect-wave on the aspect web when Decode fires the once event", async () => {
    render(
      <NatalChartWheel
        chartPositions={CHART}
        houses={HOUSES}
        ascendant={114}
        aspects={[]}
        layout="desktop"
      />,
    );
    expect(screen.getByTestId("natal-aspect-web")).toBeInTheDocument();
    expect(screen.getByTestId("natal-chart-plate")).not.toHaveAttribute("data-motion");

    act(() => {
      window.dispatchEvent(new CustomEvent(PROFILE_DECODE_PATTERN_WAVE_EVENT));
    });

    await waitFor(() => {
      expect(screen.getByTestId("natal-chart-plate")).toHaveAttribute("data-motion", "aspect-wave");
    });
    // Web lives under the waved plate (regression guard: not stranded in layerMid-only CSS).
    expect(
      screen.getByTestId("natal-chart-plate").querySelector('[data-testid="natal-aspect-web"]'),
    ).not.toBeNull();
  });

  it("skips aspect-wave when prefers-reduced-motion", async () => {
    const original = window.matchMedia;
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      configurable: true,
      value: (query: string) => ({
        matches: query.includes("prefers-reduced-motion"),
        media: query,
        onchange: null,
        addEventListener: () => {},
        removeEventListener: () => {},
        addListener: () => {},
        removeListener: () => {},
        dispatchEvent: () => false,
      }),
    });

    render(
      <NatalChartWheel
        chartPositions={CHART}
        houses={HOUSES}
        ascendant={114}
        aspects={[]}
        layout="desktop"
      />,
    );

    act(() => {
      window.dispatchEvent(new CustomEvent(PROFILE_DECODE_PATTERN_WAVE_EVENT));
    });

    await waitFor(() => {
      expect(screen.getByTestId("natal-chart-plate")).toBeInTheDocument();
    });
    expect(screen.getByTestId("natal-chart-plate")).not.toHaveAttribute("data-motion", "aspect-wave");

    Object.defineProperty(window, "matchMedia", {
      writable: true,
      configurable: true,
      value: original,
    });
  });
});
