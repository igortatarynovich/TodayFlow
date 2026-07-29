"use client";

import { useMemo, useState, useCallback, useId, useEffect, useRef, type PointerEvent as ReactPointerEvent } from "react";
import { eclipticLongitudeFromSignAndDegree, zodiacRuName } from "@/lib/zodiacKnowledge";
import { PlanetIcon } from "@/components/visualIdentity/PlanetIcon";
import { resolveNatalAspectRenderStyle, natalAspectLegendItems } from "@/lib/natal/natalWheelMaterial";
import { resolveNatalPlanetLayout } from "@/lib/natal/natalWheelLayout";
import {
  resolveNatalAtmosphereElement,
  sunSignFromPositions,
  type NatalAtmosphereElement,
} from "@/lib/natal/natalAtmosphere";
import { PROFILE_DECODE_PATTERN_WAVE_EVENT } from "@/lib/profile/profileMotionOnce";
import styles from "@/components/natal-chart/natalChartWheel.module.css";

interface Aspect {
  aspect_id: string;
  bodies: string; // e.g., "Sun-Moon"
  label: string;
  keywords: string[];
  description: string;
  tension_level?: string; // "high", "medium", "low"
}

interface NatalChartWheelProps {
  chartPositions: Array<{
    body: string;
    sign: string;
    house?: number;
    degree?: number;
    longitude?: number;
  }>;
  houses?: Record<string, any>;
  ascendant?: number; // ASC degree for proper house positioning
  aspects?: Aspect[]; // Aspect lines to draw
  /**
   * `auto` — matchMedia &lt;640px → mobile layout.
   * Mobile: simplified wheel (aspects only for selection) + structured planet list.
   * Desktop: full aspect web + denser labels.
   */
  layout?: "auto" | "desktop" | "mobile";
  /** Optional Decode-stage atmosphere tint; defaults from Sun sign. */
  atmosphereElement?: NatalAtmosphereElement | null;
}

type WheelSelection =
  | { kind: "planet"; body: string }
  | { kind: "house"; number: number }
  | null;

/** API и fallback отдают bodies как "Sun · Moon", "Солнце — Луна", а не только "Sun-Moon". */
function parseAspectBodyPair(bodies: string | undefined | null): [string, string] | null {
  if (bodies == null || typeof bodies !== "string") return null;
  const t = bodies.trim();
  if (!t) return null;
  const splitters = [/\s*[-–—]\s*/, /\s*·\s*/, /\s*,\s*/, /\s+and\s+/i];
  for (const re of splitters) {
    const parts = t.split(re).map((s) => s.trim()).filter(Boolean);
    if (parts.length >= 2 && parts[0] && parts[1]) return [parts[0], parts[1]];
  }
  const byHyphen = t.split("-").map((s) => s.trim()).filter(Boolean);
  if (byHyphen.length >= 2) return [byHyphen[0], byHyphen[1]];
  return null;
}

const BODY_TOKEN_EN: Record<string, string> = {
  sun: "sun",
  moon: "moon",
  mercury: "mercury",
  venus: "venus",
  mars: "mars",
  jupiter: "jupiter",
  saturn: "saturn",
  uranus: "uranus",
  neptune: "neptune",
  pluto: "pluto",
  солнце: "sun",
  луна: "moon",
  меркурий: "mercury",
  венера: "venus",
  марс: "mars",
  юпитер: "jupiter",
  сатурн: "saturn",
  уран: "uranus",
  нептун: "neptune",
  плутон: "pluto",
};

function canonicalPlanetToken(raw: string): string {
  const k = raw.trim().toLowerCase().replace(/\s+/g, " ");
  return BODY_TOKEN_EN[k] || k.replace(/\s+/g, "");
}

function planetTokensMatch(chartBody: string, aspectToken: string): boolean {
  const a = canonicalPlanetToken(chartBody);
  const b = canonicalPlanetToken(aspectToken);
  if (!a || !b) return false;
  return a === b || a.startsWith(b) || b.startsWith(a);
}

/** RU-подписи тел карты. API/движок отдаёт сырые ключи (sun, south_node, rising, lilith) —
 * в RU-интерфейсе профиля их нельзя показывать как есть. */
const PLANET_RU: Record<string, string> = {
  sun: "Солнце",
  moon: "Луна",
  mercury: "Меркурий",
  venus: "Венера",
  mars: "Марс",
  jupiter: "Юпитер",
  saturn: "Сатурн",
  uranus: "Уран",
  neptune: "Нептун",
  pluto: "Плутон",
  chiron: "Хирон",
  northnode: "Северный узел",
  southnode: "Южный узел",
  rising: "Асцендент",
  ascendant: "Асцендент",
  asc: "Асцендент",
  descendant: "Десцендент",
  dsc: "Десцендент",
  midheaven: "Середина неба",
  mc: "MC",
  ic: "IC",
  lilith: "Лилит",
  partoffortune: "Колесо Фортуны",
};

function planetRuName(body: string): string {
  const key = String(body || "").trim().toLowerCase().replace(/[\s_-]+/g, "");
  return PLANET_RU[key] || body;
}

/** Знак из карты (en «Scorpio» / ru «Скорпион») → русское имя знака. */
const signRuName = zodiacRuName;

/** Короткие ориентиры домов для панели деталей (не заменяют полную трактовку). */
const HOUSE_MEANINGS_RU: Record<number, string> = {
  1: "Я и самоподача — как ты входишь в мир.",
  2: "Ресурсы и деньги — на что опираешься.",
  3: "Общение и ближняя среда.",
  4: "Дом, корни, внутренняя база.",
  5: "Творчество, радость, игра.",
  6: "Быт, порядок, здоровье.",
  7: "Партнёрство и близкие союзы.",
  8: "Глубина, кризисы, общие ресурсы.",
  9: "Смыслы, горизонты, дальние планы.",
  10: "Дело, статус, публичная линия.",
  11: "Круг, единомышленники, будущее.",
  12: "Тишина, внутреннее, невидимое.",
};

/** Cream plate with cooler aspect web + warm/cool aspect strokes (see natalWheelMaterial). */
const INK = {
  parchment0: "#fefcf9",
  parchment1: "#f3ebe0",
  parchment2: "#e5d8c4",
  creamFill: "#fffaf2",
  creamSoft: "#fffaf4",
  ringOuter: "#b89a72",
  ringMid: "#c9b396",
  ringInner: "#b9a082",
  ringSoft: "#c4b29a",
  gold: "#8b6a3e",
  goldBright: "#c9a96e",
  goldMuted: "#c6a677",
  umber: "#53402a",
  ink: "#5f4930",
  inkDeep: "#3d3228",
  silver: "#9a9590",
  white: "#ffffff",
  aspectWell: "rgba(72, 64, 56, 0.07)",
  aspectWellStroke: "rgba(74, 93, 115, 0.22)",
  aspect: {
    /** Legend mirrors natalAspectLegendItems / resolveNatalAspectRenderStyle. */
    conjunction: { color: "#3d3228", dash: "none", opacity: 0.92, width: 3.0 },
    opposition: { color: "#4a5d73", dash: "8 5", opacity: 0.9, width: 2.95 },
    square: { color: "#5a6878", dash: "6 5", opacity: 0.88, width: 2.8 },
    trine: { color: "#c4782a", dash: "none", opacity: 0.78, width: 2.15 },
    sextile: { color: "#b0892e", dash: "4 4", opacity: 0.7, width: 1.85 },
    other: { color: "#7a6e5c", dash: "3 5", opacity: 0.5, width: 1.35 },
  },
  elementFill: {
    fire: "rgba(196, 120, 42, 0.14)",
    earth: "rgba(83, 64, 42, 0.12)",
    air: "rgba(74, 93, 115, 0.1)",
    water: "rgba(90, 104, 120, 0.11)",
  } as Record<string, string>,
  elementStroke: {
    fire: "#c4782a",
    earth: "#53402a",
    air: "#4a5d73",
    water: "#5a6878",
  } as Record<string, string>,
  angle: {
    ASC: "#8b6a3e",
    IC: "#5a6878",
    DSC: "#7a6e5c",
    MC: "#c4782a",
  } as Record<string, string>,
  planet: {
    Sun: "#c4782a",
    Moon: "#5a6878",
    Mercury: "#8b7355",
    Venus: "#b0892e",
    Mars: "#8b6a3e",
    Jupiter: "#c4782a",
    Saturn: "#3d3228",
    Uranus: "#4a5d73",
    Neptune: "#5a6878",
    Pluto: "#3d3228",
  } as Record<string, string>,
} as const;

/**
 * Interactive natal chart wheel.
 *
 * Selection is click/tap-driven (touch-first): tapping a planet or house opens a
 * detail panel under the plate; hover only pre-highlights on pointer devices.
 * The old hover-only SVG tooltips were unreachable on mobile.
 */
function useIsMobileLayout(layout: "auto" | "desktop" | "mobile"): boolean {
  const [mobile, setMobile] = useState(layout === "mobile");
  useEffect(() => {
    if (layout === "mobile") {
      setMobile(true);
      return;
    }
    if (layout === "desktop") {
      setMobile(false);
      return;
    }
    if (typeof window === "undefined" || !window.matchMedia) return;
    const mq = window.matchMedia("(max-width: 39.99rem)");
    const apply = () => setMobile(mq.matches);
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, [layout]);
  return mobile;
}

export function NatalChartWheel({
  chartPositions,
  houses = {},
  ascendant = 0,
  aspects: aspectsProp = [],
  layout = "auto",
  atmosphereElement = null,
}: NatalChartWheelProps) {
  const isMobile = useIsMobileLayout(layout);
  const size = 720;
  const center = size / 2;
  /* More of the SVG for planets; house labels sit outside this band. */
  const outerRadius = size / 2 - 40;
  const zodiacInnerRadius = outerRadius - 34;
  const innerRadius = outerRadius * 0.28;
  const aspectRadius = innerRadius - 4;
  /** House number chips — outside the planet collision band. */
  const houseLabelRadius = zodiacInnerRadius - 12;
  const planetDisc = isMobile ? 13 : 15;
  const planetRadiusMax = houseLabelRadius - planetDisc - 10;
  const planetRadiusMin = innerRadius + planetDisc + 6;
  const basePlanetRadius = (planetRadiusMin + planetRadiusMax) / 2;
  const houseRadius = houseLabelRadius;
  const gradientId = useId().replace(/:/g, "");
  const softGlowId = `${gradientId}-glow`;
  const webClipId = `${gradientId}-clip`;
  const planetGlowId = `${gradientId}-planet-glow`;
  const planetLitId = `${gradientId}-planet-lit`;
  const planetLitSelectedId = `${gradientId}-planet-lit-sel`;
  const planetShadowId = `${gradientId}-planet-shadow`;
  const centerVignetteId = `${gradientId}-center-vig`;

  const [selected, setSelected] = useState<WheelSelection>(null);
  const [hoveredPlanet, setHoveredPlanet] = useState<string | null>(null);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const [aspectWave, setAspectWave] = useState(false);
  const reduceMotionRef = useRef(false);

  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const apply = () => {
      reduceMotionRef.current = mq.matches;
      if (mq.matches) setTilt({ x: 0, y: 0 });
    };
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    let timer: number | undefined;
    const onWave = () => {
      if (reduceMotionRef.current) return;
      setAspectWave(true);
      window.clearTimeout(timer);
      timer = window.setTimeout(() => setAspectWave(false), 1200);
    };
    window.addEventListener(PROFILE_DECODE_PATTERN_WAVE_EVENT, onWave);
    return () => {
      window.removeEventListener(PROFILE_DECODE_PATTERN_WAVE_EVENT, onWave);
      window.clearTimeout(timer);
    };
  }, []);

  const onPlatePointerMove = useCallback((e: ReactPointerEvent<HTMLDivElement>) => {
    if (reduceMotionRef.current) return;
    if (e.pointerType === "touch") return; // keep mobile stable; depth from material only
    const rect = e.currentTarget.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    const nx = (e.clientX - rect.left) / rect.width - 0.5;
    const ny = (e.clientY - rect.top) / rect.height - 0.5;
    setTilt({ x: Math.max(-1, Math.min(1, ny)) * -5.5, y: Math.max(-1, Math.min(1, nx)) * 5.5 });
  }, []);

  const onPlatePointerLeave = useCallback(() => {
    setTilt({ x: 0, y: 0 });
  }, []);

  const selectedPlanet = selected?.kind === "planet" ? selected.body : null;
  const selectedHouse = selected?.kind === "house" ? selected.number : null;
  const activePlanet = selectedPlanet ?? hoveredPlanet;

  const stageElement = useMemo(() => {
    if (atmosphereElement) return atmosphereElement;
    return resolveNatalAtmosphereElement(sunSignFromPositions(chartPositions));
  }, [atmosphereElement, chartPositions]);

  const togglePlanet = useCallback((body: string) => {
    setSelected((prev) => (prev?.kind === "planet" && prev.body === body ? null : { kind: "planet", body }));
  }, []);

  const toggleHouse = useCallback((number: number) => {
    setSelected((prev) => (prev?.kind === "house" && prev.number === number ? null : { kind: "house", number }));
  }, []);

  // Planet symbols (memoized to avoid recreating on every render).
  // U+FE0E after each glyph forces text presentation — without it Chrome/Safari
  // substitute colored emoji for zodiac/planet glyphs, breaking the engraving look.
  const planetSymbols: Record<string, string> = useMemo(() => ({
    Sun: "☉︎",
    sun: "☉︎",
    Moon: "☽︎",
    moon: "☽︎",
    Mercury: "☿︎",
    mercury: "☿︎",
    Venus: "♀︎",
    venus: "♀︎",
    Mars: "♂︎",
    mars: "♂︎",
    Jupiter: "♃︎",
    jupiter: "♃︎",
    Saturn: "♄︎",
    saturn: "♄︎",
    Uranus: "♅︎",
    uranus: "♅︎",
    Neptune: "♆︎",
    neptune: "♆︎",
    Pluto: "♇︎",
    pluto: "♇︎",
    Chiron: "⚷︎",
    chiron: "⚷︎",
    "North Node": "☊︎",
    north_node: "☊︎",
    "South Node": "☋︎",
    south_node: "☋︎",
    Ascendant: "ASC",
    rising: "ASC",
    MC: "MC",
    IC: "IC",
    DSC: "DSC",
    Lilith: "⚸︎",
    lilith: "⚸︎",
    "Part of Fortune": "⊗︎",
  }), []);

  // Zodiac signs with their glyphs (U+FE0E: text presentation, not emoji)
  const zodiacSigns = useMemo(() => [
    { name: "Aries", glyph: "♈︎", element: "fire" },
    { name: "Taurus", glyph: "♉︎", element: "earth" },
    { name: "Gemini", glyph: "♊︎", element: "air" },
    { name: "Cancer", glyph: "♋︎", element: "water" },
    { name: "Leo", glyph: "♌︎", element: "fire" },
    { name: "Virgo", glyph: "♍︎", element: "earth" },
    { name: "Libra", glyph: "♎︎", element: "air" },
    { name: "Scorpio", glyph: "♏︎", element: "water" },
    { name: "Sagittarius", glyph: "♐︎", element: "fire" },
    { name: "Capricorn", glyph: "♑︎", element: "earth" },
    { name: "Aquarius", glyph: "♒︎", element: "air" },
    { name: "Pisces", glyph: "♓︎", element: "water" },
  ], []);

  const degreeToAngle = useCallback((degree: number): number => {
    return (270 - degree + 360) % 360;
  }, []);

  // Get position on circle (memoized with useCallback)
  const getPosition = useCallback((angle: number, radius: number) => {
    const rad = (angle * Math.PI) / 180;
    return {
      x: center + radius * Math.cos(rad),
      y: center + radius * Math.sin(rad),
    };
  }, [center]);

  // Calculate house cusps from actual house data or ASC
  const houseCusps = useMemo(() => {
    // Try to get real house cusps from houses data first
    if (houses && typeof houses === 'object') {
      const cusps: number[] = [];
      for (let i = 1; i <= 12; i++) {
        const houseKey = `house_${i}`;
        const houseData = houses[houseKey];
        if (houseData && typeof houseData === 'object') {
          // Используем cusp_longitude если есть, иначе вычисляем из sign + degree
          if (houseData.cusp_longitude !== undefined) {
            cusps.push(houseData.cusp_longitude);
          } else if (houseData.sign && houseData.degree !== undefined) {
            const degree = typeof houseData.degree === "number" ? houseData.degree : 0;
            const lon = eclipticLongitudeFromSignAndDegree(String(houseData.sign), degree) ?? 0;
            cusps.push(lon);
          } else {
            // Fallback to equal houses if no data
            const ascDegree = ascendant || 0;
            cusps.push((ascDegree + (i - 1) * 30) % 360);
          }
        } else {
          // Fallback to equal houses if no data
          const ascDegree = ascendant || 0;
          cusps.push((ascDegree + (i - 1) * 30) % 360);
        }
      }
      if (cusps.length === 12) {
        return cusps;
      }
    }

    // Fallback to equal houses if no house data available
    const ascDegree = ascendant || 0;
    const cusps: number[] = [];
    for (let i = 0; i < 12; i++) {
      cusps.push((ascDegree + i * 30) % 360);
    }
    return cusps;
  }, [ascendant, houses]);

  const aspectStyle = useCallback((aspect: Aspect) => {
    return resolveNatalAspectRenderStyle({
      aspect_id: aspect.aspect_id,
      label: aspect.label,
      tension_level: aspect.tension_level,
    });
  }, []);

  const houseSegments = useMemo(() => {
    return houseCusps.map((cusp, i) => {
      const startAngle = degreeToAngle(cusp);
      const nextCusp = houseCusps[(i + 1) % 12];
      const endAngle = degreeToAngle(nextCusp);
      const midAngle = (startAngle + (endAngle < startAngle ? endAngle + 360 : endAngle)) / 2;

      return {
        number: i + 1,
        cusp,
        startAngle,
        endAngle,
        midAngle: midAngle % 360,
        ...getPosition(midAngle, houseRadius),
      };
    });
  }, [degreeToAngle, getPosition, houseCusps, houseRadius]);

  // Planets with positions
  const planetsWithPositions = useMemo(() => {
    const filtered = chartPositions.filter((p) => p.body && String(p.body).trim() !== "");

    if (filtered.length === 0) {
      return [];
    }

    const planetsWithAngles = filtered.map((p) => {
      let degree = p.longitude;
      if (degree === undefined || degree === null) {
        if (p.sign && p.degree !== undefined) {
          const computed = eclipticLongitudeFromSignAndDegree(p.sign, p.degree);
          degree = computed !== null ? computed : p.degree ?? 0;
        } else {
          degree = p.degree ?? 0;
        }
      }
      const angle = degreeToAngle(degree);
      return { ...p, degree, angle, longitude: degree };
    });

    const layout = resolveNatalPlanetLayout(
      planetsWithAngles.map((p) => ({ angle: p.angle })),
      {
        baseRadius: basePlanetRadius,
        minRadius: planetRadiusMin,
        maxRadius: planetRadiusMax,
        discRadius: planetDisc,
        gap: isMobile ? 7 : 9,
      },
    );

    return planetsWithAngles.map((p, index) => {
      const place = layout[index];
      const position = getPosition(place.paintAngle, place.radius);
      const trueTick = getPosition(place.trueAngle, basePlanetRadius);

      const planetHouse =
        houseCusps.findIndex((cusp, i) => {
          const nextCusp = houseCusps[(i + 1) % 12];
          const normalizedDegree = p.degree % 360;
          const normalizedCusp = cusp % 360;
          const normalizedNext = nextCusp % 360;

          if (normalizedNext > normalizedCusp) {
            return normalizedDegree >= normalizedCusp && normalizedDegree < normalizedNext;
          }
          return normalizedDegree >= normalizedCusp || normalizedDegree < normalizedNext;
        }) + 1;

      return {
        ...p,
        position,
        trueTick,
        house: p.house ?? planetHouse,
        symbol: planetSymbols[p.body] || p.body.substring(0, 3),
        radius: place.radius,
        angleOffset: place.angleOffset,
        radiusOffset: place.radiusOffset,
        paintAngle: place.paintAngle,
        leader: place.leader,
        discScale: place.discScale,
      };
    });
  }, [
    basePlanetRadius,
    chartPositions,
    degreeToAngle,
    getPosition,
    houseCusps,
    isMobile,
    planetDisc,
    planetRadiusMax,
    planetRadiusMin,
    planetSymbols,
  ]);

  const angleMarkers = useMemo(() => {
    const markers = [
      { key: "ASC", degree: houseCusps[0], color: INK.angle.ASC },
      { key: "IC", degree: houseCusps[3], color: INK.angle.IC },
      { key: "DSC", degree: houseCusps[6], color: INK.angle.DSC },
      { key: "MC", degree: houseCusps[9], color: INK.angle.MC },
    ];
    return markers.map((marker) => {
      const angle = degreeToAngle(marker.degree);
      return {
        ...marker,
        angle,
        outer: getPosition(angle, outerRadius - 2),
        inner: getPosition(angle, zodiacInnerRadius + 2),
      };
    });
  }, [degreeToAngle, getPosition, houseCusps, outerRadius, zodiacInnerRadius]);

  const aspectSummary = useMemo(() => {
    const counter = new Map<string, number>();
    for (const aspect of aspectsProp) {
      const key = aspectStyle(aspect).label;
      counter.set(key, (counter.get(key) || 0) + 1);
    }
    return Array.from(counter.entries()).map(([label, count]) => ({ label, count }));
  }, [aspectStyle, aspectsProp]);

  const aspectLines = useMemo(() => {
    if (!aspectsProp || aspectsProp.length === 0) {
      return [];
    }

    const lines: Array<{
      key: string;
      planet1: { body: string; anchor: { x: number; y: number } };
      planet2: { body: string; anchor: { x: number; y: number } };
      aspect: Aspect;
      color: string;
      dash: string;
      opacity: number;
      width: number;
      label: string;
      stack: number;
      weight: string;
    }> = [];

    for (const aspect of aspectsProp) {
      const pair = parseAspectBodyPair(aspect.bodies);
      if (!pair) {
        continue;
      }
      const [body1, body2] = pair;

      const planet1 = planetsWithPositions.find((p) => planetTokensMatch(String(p.body || ""), body1));
      const planet2 = planetsWithPositions.find((p) => planetTokensMatch(String(p.body || ""), body2));

      if (!planet1 || !planet2) {
        continue;
      }

      const style = aspectStyle(aspect);
      const anchor1 = getPosition(planet1.angle, aspectRadius);
      const anchor2 = getPosition(planet2.angle, aspectRadius);
      lines.push({
        key: `${aspect.aspect_id}-${planet1.body}-${planet2.body}`,
        planet1: { body: planet1.body, anchor: anchor1 },
        planet2: { body: planet2.body, anchor: anchor2 },
        aspect,
        color: style.color,
        dash: style.dash,
        opacity: style.opacity,
        width: style.width,
        label: style.label,
        stack: style.stack,
        weight: style.weight,
      });
    }

    // Soft aspects farther (paint first); strong closer to front.
    lines.sort((a, b) => a.stack - b.stack);
    return lines;
  }, [aspectRadius, aspectStyle, aspectsProp, getPosition, planetsWithPositions]);

  const selectedPlanetData = useMemo(
    () => (selectedPlanet ? planetsWithPositions.find((p) => p.body === selectedPlanet) ?? null : null),
    [planetsWithPositions, selectedPlanet],
  );

  const selectedPlanetAspects = useMemo(() => {
    if (!selectedPlanet) return [];
    return aspectLines
      .filter((l) => l.planet1.body === selectedPlanet || l.planet2.body === selectedPlanet)
      .map((l) => ({
        key: l.key,
        other: l.planet1.body === selectedPlanet ? l.planet2.body : l.planet1.body,
        label: l.label,
        color: l.color,
        dash: l.dash,
      }));
  }, [aspectLines, selectedPlanet]);

  const selectedHouseData = useMemo(() => {
    if (selectedHouse == null) return null;
    const cusp = houseCusps[selectedHouse - 1] ?? 0;
    const signIndex = Math.floor(((cusp % 360) + 360) % 360 / 30);
    const signName = zodiacSigns[signIndex]?.name ?? "";
    const inhabitants = planetsWithPositions.filter((p) => p.house === selectedHouse);
    return { number: selectedHouse, signName, inhabitants };
  }, [houseCusps, planetsWithPositions, selectedHouse, zodiacSigns]);

  if (!chartPositions || chartPositions.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "var(--orbit-space-xl)", color: "var(--orbit-color-text-secondary)" }}>
        <p>No chart data available</p>
        <p style={{ fontSize: "0.8em", marginTop: "0.5em" }}>Please ensure your birth data is entered correctly.</p>
      </div>
    );
  }

  if (planetsWithPositions.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "var(--orbit-space-xl)", color: "var(--orbit-color-text-secondary)" }}>
        <p>Unable to render chart: no valid planet positions found</p>
        <p style={{ fontSize: "0.8em", marginTop: "0.5em" }}>
          Received {chartPositions.length} positions, but none were valid.
        </p>
      </div>
    );
  }

  return (
    <div
      className={styles.root}
      data-testid="natal-chart-wheel"
      data-layout={isMobile ? "mobile" : "desktop"}
    >
      <div className={styles.stage} data-element={stageElement} data-testid="natal-chart-stage">
        <div className={styles.stageAura} aria-hidden />
        <div
          className={[styles.plate, aspectWave ? styles.aspectWave : ""].filter(Boolean).join(" ")}
          data-testid="natal-chart-plate"
          data-motion={aspectWave ? "aspect-wave" : undefined}
          onPointerMove={onPlatePointerMove}
          onPointerLeave={onPlatePointerLeave}
          style={{
            transform: `perspective(920px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
          }}
        >
        <svg
          className={styles.svg}
          viewBox={`0 0 ${size} ${size}`}
          role="img"
          aria-label="Натальная карта"
        >
        <defs>
          <radialGradient id={`${gradientId}-chart`} cx="50%" cy="50%">
            <stop offset="0%" stopColor={INK.parchment0} stopOpacity="1" />
            <stop offset="55%" stopColor={INK.parchment1} stopOpacity="1" />
            <stop offset="100%" stopColor={INK.parchment2} stopOpacity="1" />
          </radialGradient>
          <radialGradient id={centerVignetteId} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#2c2620" stopOpacity="0.22" />
            <stop offset="42%" stopColor="#3d3228" stopOpacity="0.1" />
            <stop offset="78%" stopColor="#3d3228" stopOpacity="0.02" />
            <stop offset="100%" stopColor="#3d3228" stopOpacity="0" />
          </radialGradient>
          <radialGradient id={planetLitId} cx="32%" cy="28%" r="68%">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.98" />
            <stop offset="42%" stopColor="#fff8ef" stopOpacity="1" />
            <stop offset="78%" stopColor="#f0e2cb" stopOpacity="1" />
            <stop offset="100%" stopColor="#d8c4a4" stopOpacity="1" />
          </radialGradient>
          <radialGradient id={planetLitSelectedId} cx="34%" cy="30%" r="70%">
            <stop offset="0%" stopColor="#fffdf8" stopOpacity="1" />
            <stop offset="35%" stopColor="#f5e6c8" stopOpacity="1" />
            <stop offset="100%" stopColor="#c9a96e" stopOpacity="1" />
          </radialGradient>
          <filter id={softGlowId} x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="5" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id={planetGlowId} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3.5" result="planetBlur" />
            <feMerge>
              <feMergeNode in="planetBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id={planetShadowId} x="-60%" y="-60%" width="220%" height="220%">
            <feDropShadow dx="1.4" dy="2.6" stdDeviation="2.1" floodColor="#3d3228" floodOpacity="0.32" />
          </filter>
          <clipPath id={webClipId}>
            <circle cx={center} cy={center} r={innerRadius - 2} />
          </clipPath>
        </defs>

        {/* Background circle doubles as the tap-to-deselect surface */}
        <circle
          cx={center}
          cy={center}
          r={outerRadius + 4}
          fill={`url(#${gradientId}-chart)`}
          onClick={() => setSelected(null)}
        />

        {/* Layer back: rings / zodiac / houses — slight counter-parallax */}
        <g
          className={styles.layerBack}
          style={{
            transform: `translate(${tilt.y * 0.55}px, ${-tilt.x * 0.55}px)`,
          }}
        >
        <circle
          cx={center}
          cy={center}
          r={outerRadius + 2}
          fill="none"
          stroke="rgba(255,255,255,0.7)"
          strokeWidth="10"
        />

        <circle
          cx={center}
          cy={center}
          r={outerRadius}
          fill="none"
          stroke={INK.ringOuter}
          strokeWidth="2.5"
        />

        <circle
          cx={center}
          cy={center}
          r={zodiacInnerRadius}
          fill="none"
          stroke={INK.ringMid}
          strokeWidth="1.3"
          opacity="0.82"
        />

        <circle
          cx={center}
          cy={center}
          r={innerRadius}
          fill="none"
          stroke={INK.ringInner}
          strokeWidth="1.5"
          opacity="0.84"
        />

        <circle
          cx={center}
          cy={center}
          r={aspectRadius}
          fill={INK.aspectWell}
          stroke={INK.aspectWellStroke}
          strokeWidth="1.25"
          onClick={() => setSelected(null)}
        />
        <circle
          cx={center}
          cy={center}
          r={aspectRadius}
          fill={`url(#${centerVignetteId})`}
          style={{ pointerEvents: "none" }}
        />

        {zodiacSigns.map((sign, i) => {
          const start = degreeToAngle(i * 30);
          const end = degreeToAngle((i + 1) * 30);
          const startOuter = getPosition(start, outerRadius);
          const endOuter = getPosition(end, outerRadius);
          const startInner = getPosition(start, zodiacInnerRadius);
          const endInner = getPosition(end, zodiacInnerRadius);
          const largeArc = 0;
          const sweep = 0;
          const elementColors = INK.elementFill;
          const path = [
            `M ${startOuter.x} ${startOuter.y}`,
            `A ${outerRadius} ${outerRadius} 0 ${largeArc} ${sweep} ${endOuter.x} ${endOuter.y}`,
            `L ${endInner.x} ${endInner.y}`,
            `A ${zodiacInnerRadius} ${zodiacInnerRadius} 0 ${largeArc} 1 ${startInner.x} ${startInner.y}`,
            "Z",
          ].join(" ");
          return <path key={`zodiac-sector-${sign.name}`} d={path} fill={elementColors[sign.element] || "rgba(154,149,144,0.08)"} />;
        })}

        {houseCusps.map((cusp, i) => {
          const angle = degreeToAngle(cusp);
          const outerPos = getPosition(angle, outerRadius);
          const innerPos = getPosition(angle, innerRadius);
          return (
            <g key={`cusp-${i}`}>
              <line
                x1={innerPos.x}
                y1={innerPos.y}
                x2={outerPos.x}
                y2={outerPos.y}
                stroke={INK.ringSoft}
                strokeWidth="1.5"
                opacity={0.7}
              />
            </g>
          );
        })}

        {houseSegments.map((segment, index) => {
          const nextSegment = houseSegments[(index + 1) % houseSegments.length];
          const labelRadius = zodiacInnerRadius - 18;
          const start = getPosition(segment.startAngle, labelRadius);
          const end = getPosition(nextSegment.startAngle, labelRadius);
          return (
            <path
              key={`house-arc-${segment.number}`}
              d={`M ${start.x} ${start.y} A ${labelRadius} ${labelRadius} 0 0 0 ${end.x} ${end.y}`}
              fill="none"
              stroke="rgba(198, 166, 119, 0.18)"
              strokeWidth="9"
              strokeLinecap="round"
            />
          );
        })}

        {houseSegments.map((segment) => {
          const isActive = selectedHouse === segment.number;
          return (
            <g
              key={`house-${segment.number}`}
              data-wheel-hit
              onClick={() => toggleHouse(segment.number)}
            >
              <circle
                cx={segment.x}
                cy={segment.y}
                r={isActive ? 13 : 11}
                fill={isActive ? INK.gold : "rgba(255,250,242,0.92)"}
                stroke={isActive ? INK.gold : INK.ringSoft}
                strokeWidth={isActive ? "2" : "1.25"}
                opacity={isActive ? 1 : 0.9}
                style={{ transition: "all 0.2s" }}
              />
              <text
                x={segment.x}
                y={segment.y}
                textAnchor="middle"
                dominantBaseline="central"
                fontSize="12"
                fontWeight="700"
                fill={isActive ? INK.white : INK.gold}
                style={{ transition: "all 0.2s", pointerEvents: "none" }}
              >
                {segment.number}
              </text>
            </g>
          );
        })}

        {zodiacSigns.map((sign, i) => {
          const signStartAngle = degreeToAngle(i * 30);
          const signStartPos = getPosition(signStartAngle, zodiacInnerRadius);
          const signEndPos = getPosition(signStartAngle, outerRadius);
          return (
            <line
              key={`sign-boundary-${sign.name}`}
              x1={signStartPos.x}
              y1={signStartPos.y}
              x2={signEndPos.x}
              y2={signEndPos.y}
              stroke={INK.ringSoft}
              strokeWidth="1"
              opacity={0.4}
            />
          );
        })}

        {zodiacSigns.map((sign, i) => {
          const signAngle = degreeToAngle(i * 30 + 15);
          const bandRadius = (outerRadius + zodiacInnerRadius) / 2;
          const pos = getPosition(signAngle, bandRadius);
          const elementColors = INK.elementStroke;
          const markerR = isMobile ? 13 : 16;
          return (
            <g key={sign.name}>
              <circle
                cx={pos.x}
                cy={pos.y}
                r={markerR}
                fill={INK.white}
                stroke={elementColors[sign.element] || INK.gold}
                strokeWidth="1.5"
                opacity="0.92"
              />
              <text
                x={pos.x}
                y={pos.y}
                textAnchor="middle"
                dominantBaseline="central"
                fontSize={isMobile ? "14" : "17"}
                fill={elementColors[sign.element] || INK.gold}
                fontWeight="700"
              >
                {sign.glyph}
              </text>
            </g>
          );
        })}
        </g>

        {/* Layer mid: aspect web + angles */}
        <g
          className={styles.layerMid}
          style={{
            transform: `translate(${tilt.y * 0.22}px, ${-tilt.x * 0.22}px)`,
          }}
        >
        <g clipPath={`url(#${webClipId})`}>
          {(isMobile
            ? aspectLines.filter(
                (line) =>
                  selectedPlanet != null &&
                  (line.planet1.body === selectedPlanet || line.planet2.body === selectedPlanet),
              )
            : aspectLines
          ).map((line) => {
            const isLinked =
              activePlanet != null &&
              (line.planet1.body === activePlanet || line.planet2.body === activePlanet);
            // Mobile: only the selected planet's aspects. Desktop: full web with focus fade.
            const opacity = isMobile
              ? Math.min(line.opacity + 0.2, 1)
              : activePlanet == null
                ? line.opacity
                : isLinked
                  ? Math.min(line.opacity + 0.22, 1)
                  : 0.1;
            const width = isLinked || isMobile ? line.width + 0.7 : line.width;
            const soft = line.weight === "soft";
            return (
              <g key={line.key} opacity={soft && activePlanet == null && !isMobile ? 0.92 : 1}>
                <line
                  x1={line.planet1.anchor.x}
                  y1={line.planet1.anchor.y}
                  x2={line.planet2.anchor.x}
                  y2={line.planet2.anchor.y}
                  stroke={line.color}
                  strokeWidth={width + (line.weight === "strong" ? 5 : 4)}
                  opacity={Math.max(opacity - (line.weight === "strong" ? 0.38 : 0.5), 0.03)}
                  strokeLinecap="round"
                  filter={`url(#${softGlowId})`}
                />
                <line
                  x1={line.planet1.anchor.x}
                  y1={line.planet1.anchor.y}
                  x2={line.planet2.anchor.x}
                  y2={line.planet2.anchor.y}
                  stroke={line.color}
                  strokeWidth={width}
                  opacity={opacity}
                  strokeDasharray={line.dash}
                  strokeLinecap="round"
                />
              </g>
            );
          })}

          <circle
            cx={center}
            cy={center}
            r={Math.max(aspectRadius * 0.42, 28)}
            fill="rgba(44, 38, 32, 0.06)"
            stroke="rgba(74, 93, 115, 0.12)"
            strokeWidth="1"
            onClick={() => setSelected(null)}
          />
        </g>

        {angleMarkers.map((marker) => (
          <g key={marker.key}>
            <line
              x1={marker.inner.x}
              y1={marker.inner.y}
              x2={marker.outer.x}
              y2={marker.outer.y}
              stroke={marker.color}
              strokeWidth="1.8"
              opacity="0.7"
            />
            <circle cx={marker.outer.x} cy={marker.outer.y} r="13" fill={INK.white} stroke={marker.color} strokeWidth="2" />
            <text
              x={marker.outer.x}
              y={marker.outer.y}
              textAnchor="middle"
              dominantBaseline="central"
              fontSize="10"
              fill={marker.color}
              fontWeight="700"
            >
              {marker.key}
            </text>
          </g>
        ))}

        {planetsWithPositions.map((planet, index) => {
          if (!planet.leader) return null;
          // Whisker on the planet belt only — never from the chart center / aspect well.
          return (
            <g key={`planet-leader-${planet.body}-${index}`} style={{ pointerEvents: "none" }}>
              <circle
                cx={planet.trueTick.x}
                cy={planet.trueTick.y}
                r="2.2"
                fill={INK.ink}
                opacity={0.45}
              />
              <line
                x1={planet.trueTick.x}
                y1={planet.trueTick.y}
                x2={planet.position.x}
                y2={planet.position.y}
                stroke={INK.ink}
                strokeWidth="1"
                opacity={0.28}
                strokeDasharray="2,3"
              />
            </g>
          );
        })}
        </g>

        {/* Layer front: lit planet spheres */}
        <g
          className={styles.layerFront}
          style={{
            transform: `translate(${tilt.y * -0.4}px, ${-tilt.x * -0.4}px)`,
          }}
        >
        {planetsWithPositions.map((planet, idx) => {
          const isSelected = selectedPlanet === planet.body;
          const isActive = activePlanet === planet.body;
          const planetColors = INK.planet;
          const planetColor = planetColors[planet.body as keyof typeof planetColors] || INK.gold;
          const disc = planetDisc * (planet.discScale ?? 1);

          return (
            <g
              key={`planet-${planet.body}-${idx}`}
              data-wheel-hit
              onClick={() => togglePlanet(planet.body)}
              onMouseEnter={() => setHoveredPlanet(planet.body)}
              onMouseLeave={() => setHoveredPlanet(null)}
              filter={`url(#${planetShadowId})`}
            >
              <g filter={isActive ? `url(#${planetGlowId})` : undefined}>
                <circle cx={planet.position.x} cy={planet.position.y} r={disc + 10} fill="transparent" />
                <circle
                  cx={planet.position.x}
                  cy={planet.position.y}
                  r={isActive ? disc + 2 : disc}
                  fill={isSelected ? `url(#${planetLitSelectedId})` : `url(#${planetLitId})`}
                  stroke={planetColor}
                  strokeWidth={isActive ? "2.35" : "1.7"}
                  style={{ transition: "all 0.3s ease" }}
                />
                {/* Specular highlight */}
                <circle
                  cx={planet.position.x - disc * 0.28}
                  cy={planet.position.y - disc * 0.32}
                  r={disc * 0.28}
                  fill="#ffffff"
                  opacity={isSelected ? 0.55 : 0.42}
                  style={{ pointerEvents: "none", transition: "all 0.3s ease" }}
                />
                <text
                  x={planet.position.x}
                  y={planet.position.y}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fontSize={isMobile ? (isActive ? "15" : "13") : isActive ? "17" : "15"}
                  fill={isSelected ? INK.inkDeep : planetColor}
                  fontWeight="700"
                  style={{ transition: "all 0.3s ease", pointerEvents: "none" }}
                >
                  {planet.symbol}
                </text>
              </g>
            </g>
          );
        })}

        <circle
          cx={center}
          cy={center}
          r={Math.max(aspectRadius * 0.55, 36)}
          fill={`url(#${centerVignetteId})`}
          stroke={INK.ringSoft}
          strokeWidth="1.1"
          onClick={() => setSelected(null)}
        />
        <circle
          cx={center}
          cy={center}
          r="16"
          fill={`url(#${planetLitId})`}
          stroke={INK.gold}
          strokeWidth="1.25"
          opacity="0.94"
          filter={`url(#${planetShadowId})`}
          onClick={() => setSelected(null)}
        />
        <text
          x={center}
          y={center}
          textAnchor="middle"
          dominantBaseline="central"
          fontSize="11"
          fontWeight="700"
          fill={INK.inkDeep}
          opacity="0.78"
          style={{ pointerEvents: "none", letterSpacing: "0.04em" }}
        >
          {stageElement === "fire"
            ? "Огонь"
            : stageElement === "air"
              ? "Воздух"
              : stageElement === "water"
                ? "Вода"
                : "Земля"}
        </text>
        </g>
        </svg>
      </div>

        <div className={styles.dock} data-testid="natal-chart-dock">
          <p className={styles.dockLabel}>Планеты</p>
          <div className={styles.chipRailWrap}>
            <div className={styles.chipRail} data-testid="natal-chart-planet-rail">
              {planetsWithPositions.map((planet) => {
                const isActive = selectedPlanet === planet.body;
                return (
                  <button
                    key={planet.body}
                    type="button"
                    className={`${styles.chip} ${isActive ? styles.chipActive : ""}`.trim()}
                    onClick={() => togglePlanet(planet.body)}
                    aria-pressed={isActive}
                  >
                    <span className={styles.chipGlyph} aria-hidden>
                      <PlanetIcon planet={planet.body} size={15} />
                    </span>
                    {planetRuName(planet.body)}
                  </button>
                );
              })}
            </div>
          </div>
          {!isMobile ? (
            <div className={styles.legend} aria-label="Типы аспектов">
              {natalAspectLegendItems().map((item) => {
                const count = aspectSummary.find((entry) => entry.label === item.label)?.count || 0;
                return (
                  <div key={item.label} className={styles.legendItem}>
                    <svg width="32" height="12" viewBox="0 0 32 12" aria-hidden="true">
                      <line
                        x1="1"
                        y1="6"
                        x2="31"
                        y2="6"
                        stroke={item.color}
                        strokeWidth="2.8"
                        strokeDasharray={item.dash === "none" ? undefined : item.dash}
                        strokeLinecap="round"
                      />
                    </svg>
                    <span>
                      {item.label}
                      {count ? ` · ${count}` : ""}
                    </span>
                  </div>
                );
              })}
            </div>
          ) : null}
        </div>
      </div>

      <div className={styles.readingSheet} data-testid="natal-chart-reading">
      <div className={styles.panel} data-testid="natal-chart-detail" aria-live="polite">
        {selectedPlanetData ? (
          <>
            <div className={styles.panelHeader}>
              <span className={styles.panelGlyph} aria-hidden>
                <PlanetIcon planet={selectedPlanetData.body} size={22} />
              </span>
              <h3 className={styles.panelTitle}>{planetRuName(selectedPlanetData.body)}</h3>
              <p className={styles.panelMeta}>
                {signRuName(selectedPlanetData.sign)}
                {selectedPlanetData.house ? ` · ${selectedPlanetData.house} дом` : ""}
                {selectedPlanetData.degree !== undefined
                  ? ` · ${Math.floor(((selectedPlanetData.degree % 30) + 30) % 30)}°`
                  : ""}
              </p>
            </div>
            {selectedPlanetAspects.length > 0 ? (
              <ul className={styles.aspectList}>
                {selectedPlanetAspects.map((a) => (
                  <li key={a.key} className={styles.aspectRow}>
                    <svg className={styles.aspectSwatch} viewBox="0 0 26 10" aria-hidden>
                      <line x1="1" y1="5" x2="25" y2="5" stroke={a.color} strokeWidth="2.4" strokeDasharray={a.dash} strokeLinecap="round" />
                    </svg>
                    <span className={styles.aspectKind}>{a.label} с</span>
                    <button type="button" className={styles.aspectOther} onClick={() => togglePlanet(a.other)}>
                      {planetRuName(a.other)}
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className={styles.panelBody}>Мажорных аспектов к этой точке в карте нет — она действует самостоятельно.</p>
            )}
          </>
        ) : selectedHouseData ? (
          <>
            <div className={styles.panelHeader}>
              <h3 className={styles.panelTitle}>{selectedHouseData.number} дом</h3>
              {selectedHouseData.signName ? (
                <p className={styles.panelMeta}>куспид в {signRuName(selectedHouseData.signName)}</p>
              ) : null}
            </div>
            <p className={styles.panelBody}>{HOUSE_MEANINGS_RU[selectedHouseData.number] ?? ""}</p>
            {selectedHouseData.inhabitants.length > 0 ? (
              <p className={styles.panelBody}>
                Здесь: {selectedHouseData.inhabitants.map((p) => planetRuName(p.body)).join(", ")}
              </p>
            ) : null}
          </>
        ) : (
          <p className={styles.panelHint}>
            Выбери планету на кольце или в панели карты — откроются знак, дом и связи.
          </p>
        )}
      </div>
      </div>
    </div>
  );
}
