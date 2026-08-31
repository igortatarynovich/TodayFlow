"use client";

import { useState } from "react";
import { NatalChartWheel } from "@/components/natal-chart/NatalChartWheel";

/**
 * Dev-only harness for the natal wheel (touch selection, dark theme, narrow widths).
 * Live natal data needs a server narrative round-trip, which makes visual QA of the wheel itself
 * slow and flaky — this renders it directly from a fixed chart.
 */

const CHART_POSITIONS = [
  { body: "Sun", sign: "Aquarius", house: 8, degree: 25.4, longitude: 325.4 },
  { body: "Moon", sign: "Libra", house: 4, degree: 12.1, longitude: 192.1 },
  { body: "Mercury", sign: "Aquarius", house: 8, degree: 28.9, longitude: 328.9 },
  { body: "Venus", sign: "Capricorn", house: 7, degree: 3.2, longitude: 273.2 },
  { body: "Mars", sign: "Capricorn", house: 7, degree: 8.7, longitude: 278.7 },
  { body: "Jupiter", sign: "Cancer", house: 1, degree: 19.5, longitude: 109.5 },
  { body: "Saturn", sign: "Capricorn", house: 7, degree: 14.3, longitude: 284.3 },
  { body: "Uranus", sign: "Capricorn", house: 6, degree: 16.8, longitude: 286.8 },
  { body: "Neptune", sign: "Capricorn", house: 6, degree: 18.2, longitude: 288.2 },
  { body: "Pluto", sign: "Scorpio", house: 5, degree: 21.6, longitude: 231.6 },
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

const ASPECTS = [
  { aspect_id: "sun_moon_square", bodies: "Sun-Moon", label: "Квадрат", keywords: [], description: "" },
  { aspect_id: "sun_mercury_conjunction", bodies: "Sun-Mercury", label: "Соединение", keywords: [], description: "" },
  { aspect_id: "moon_venus_trine", bodies: "Moon-Venus", label: "Трин", keywords: [], description: "" },
  { aspect_id: "mars_saturn_conjunction", bodies: "Mars-Saturn", label: "Соединение", keywords: [], description: "" },
  { aspect_id: "jupiter_saturn_opposition", bodies: "Jupiter-Saturn", label: "Оппозиция", keywords: [], description: "" },
  { aspect_id: "venus_pluto_sextile", bodies: "Venus-Pluto", label: "Секстиль", keywords: [], description: "" },
  { aspect_id: "sun_jupiter_opposition", bodies: "Sun-Jupiter", label: "Оппозиция", keywords: [], description: "" },
];

export default function NatalWheelPreviewPage() {
  const [dark, setDark] = useState(false);
  const isDev = process.env.NODE_ENV !== "production";

  if (!isDev) {
    return (
      <main style={{ padding: "2rem", fontFamily: "system-ui" }}>
        <p>Preview available only outside production builds.</p>
      </main>
    );
  }

  return (
    <main
      data-theme={dark ? "dark" : "light"}
      data-testid="natal-wheel-preview"
      style={{
        minHeight: "100vh",
        background: dark ? "#121018" : "#f7f4ee",
        color: dark ? "#f5f0e8" : "#2a2520",
        padding: "1.25rem clamp(0.75rem, 3vw, 2rem) 3rem",
      }}
    >
      <button
        type="button"
        onClick={() => setDark((v) => !v)}
        data-testid="toggle-theme"
        style={{ marginBottom: "1rem", padding: "0.5rem 0.9rem", borderRadius: 999, cursor: "pointer" }}
      >
        {dark ? "Светлая тема" : "Тёмная тема"}
      </button>
      <NatalChartWheel
        chartPositions={CHART_POSITIONS}
        houses={HOUSES}
        ascendant={114}
        aspects={ASPECTS}
      />
    </main>
  );
}
