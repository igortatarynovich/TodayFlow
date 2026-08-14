"use client";

import { useMemo, useState, useCallback, useId, useEffect, useRef } from "react";
import { eclipticLongitudeFromSignAndDegree, zodiacRuName } from "@/lib/zodiacKnowledge";
import { PlanetIcon } from "@/components/visualIdentity/PlanetIcon";
import { ElementIcon } from "@/components/visualIdentity/ElementIcon";
import {
  resolveNatalAspectRenderStyle,
  natalAspectLegendItems,
  isMajorNatalAspect,
  deriveMajorAspectCalloutsFromLongitudes,
  NATAL_ASPECT_HALO,
} from "@/lib/natal/natalWheelMaterial";
import {
  resolvePlanetSlug,
  chartAngleAssetPath,
  zodiacOrbAssetPath,
  planetHasPhotoAsset,
  planetPhotoPath,
  type ChartAngleSlug,
  type ZodiacSlug,
} from "@/lib/visualIdentity/registry";
import { resolveNatalPlanetLayout } from "@/lib/natal/natalWheelLayout";
import {
  resolveNatalAtmosphereElement,
  resolveNatalPlanetJewel,
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

/** Chord between two planet discs — ends at disc edges so the stroke reads as a link, not a hub spoke. */
function aspectChordEnds(
  a: { x: number; y: number },
  b: { x: number; y: number },
  padA: number,
  padB: number,
): { x1: number; y1: number; x2: number; y2: number } {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const len = Math.hypot(dx, dy) || 1;
  const ux = dx / len;
  const uy = dy / len;
  return {
    x1: a.x + ux * padA,
    y1: a.y + uy * padA,
    x2: b.x - ux * padB,
    y2: b.y - uy * padB,
  };
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
    conjunction: { color: "#3d3228", dash: "none", opacity: 0.95, width: 3.35 },
    opposition: { color: "#3f5878", dash: "8 5", opacity: 0.94, width: 3.2 },
    square: { color: "#4f6478", dash: "6 5", opacity: 0.92, width: 3.1 },
    trine: { color: "#c4782a", dash: "none", opacity: 0.9, width: 2.65 },
    sextile: { color: "#b0892e", dash: "4 4", opacity: 0.84, width: 2.35 },
    other: { color: "#7a6e5c", dash: "3 5", opacity: 0.5, width: 1.35 },
  },
  elementFill: {
    fire: "rgba(196, 120, 42, 0.14)",
    earth: "rgba(139, 106, 62, 0.14)",
    air: "rgba(106, 132, 158, 0.14)",
    water: "rgba(90, 122, 140, 0.15)",
  } as Record<string, string>,
  /** Same family as planet jewels — all four elements must read on cream markers. */
  elementStroke: {
    fire: "#c4782a",
    earth: "#8b6a3e",
    air: "#6a849e",
    water: "#5a7a8c",
  } as Record<string, string>,
  elementWash: {
    fire: "rgba(255, 186, 110, 0.28)",
    earth: "rgba(210, 180, 130, 0.28)",
    air: "rgba(170, 198, 220, 0.3)",
    water: "rgba(130, 175, 200, 0.3)",
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
  /**
   * Kit principle: zodiac chips sit fully inside the outer ring (not clipped),
   * house digits share the band on the inner side, planets fill their discs.
   */
  const outerRadius = size / 2 - 28;
  const zodiacBand = 52;
  const zodiacInnerRadius = outerRadius - zodiacBand;
  const zodiacMarkerR = isMobile ? 11 : 13;
  /** Outer half of band — keeps orbs clear of the rim stroke. */
  const zodiacBandRadius = outerRadius - zodiacMarkerR - 4;
  /** Inner half of band — house chips don't sit under zodiac orbs. */
  const houseLabelRadius = zodiacInnerRadius + Math.min(12, zodiacBand * 0.28);
  const innerRadius = outerRadius * 0.22;
  const aspectRadius = innerRadius - 4;
  /** Hub hole so opposition/square chords do not read as spokes from the center. */
  const aspectHubRadius = Math.max(34, innerRadius * 0.48);
  const planetDisc = isMobile ? 15 : 18;
  const planetRadiusMax = zodiacInnerRadius - planetDisc - 10;
  const planetRadiusMin = innerRadius + planetDisc + 6;
  const basePlanetRadius = (planetRadiusMin + planetRadiusMax) / 2;
  const houseRadius = houseLabelRadius;
  const gradientId = useId().replace(/:/g, "");
  const softGlowId = `${gradientId}-glow`;
  const planetGlowId = `${gradientId}-planet-glow`;
  const planetLitId = `${gradientId}-planet-lit`;
  const planetLitSelectedId = `${gradientId}-planet-lit-sel`;
  const planetShadowId = `${gradientId}-planet-shadow`;
  const centerVignetteId = `${gradientId}-center-vig`;

  const [selected, setSelected] = useState<WheelSelection>(null);
  const [hoveredPlanet, setHoveredPlanet] = useState<string | null>(null);
  const [aspectWave, setAspectWave] = useState(false);
  const reduceMotionRef = useRef(false);

  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const apply = () => {
      reduceMotionRef.current = mq.matches;
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
    { name: "Aries", slug: "aries" as ZodiacSlug, glyph: "♈︎", element: "fire" },
    { name: "Taurus", slug: "taurus" as ZodiacSlug, glyph: "♉︎", element: "earth" },
    { name: "Gemini", slug: "gemini" as ZodiacSlug, glyph: "♊︎", element: "air" },
    { name: "Cancer", slug: "cancer" as ZodiacSlug, glyph: "♋︎", element: "water" },
    { name: "Leo", slug: "leo" as ZodiacSlug, glyph: "♌︎", element: "fire" },
    { name: "Virgo", slug: "virgo" as ZodiacSlug, glyph: "♍︎", element: "earth" },
    { name: "Libra", slug: "libra" as ZodiacSlug, glyph: "♎︎", element: "air" },
    { name: "Scorpio", slug: "scorpio" as ZodiacSlug, glyph: "♏︎", element: "water" },
    { name: "Sagittarius", slug: "sagittarius" as ZodiacSlug, glyph: "♐︎", element: "fire" },
    { name: "Capricorn", slug: "capricorn" as ZodiacSlug, glyph: "♑︎", element: "earth" },
    { name: "Aquarius", slug: "aquarius" as ZodiacSlug, glyph: "♒︎", element: "air" },
    { name: "Pisces", slug: "pisces" as ZodiacSlug, glyph: "♓︎", element: "water" },
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
    const markers: Array<{ key: string; slug: ChartAngleSlug; degree: number; color: string }> = [
      { key: "ASC", slug: "asc", degree: houseCusps[0], color: INK.angle.ASC },
      { key: "IC", slug: "ic", degree: houseCusps[3], color: INK.angle.IC },
      { key: "DSC", slug: "dsc", degree: houseCusps[6], color: INK.angle.DSC },
      { key: "MC", slug: "mc", degree: houseCusps[9], color: INK.angle.MC },
    ];
    return markers.map((marker) => {
      const angle = degreeToAngle(marker.degree);
      return {
        ...marker,
        angle,
        outer: getPosition(angle, outerRadius - 14),
        inner: getPosition(angle, zodiacInnerRadius + 2),
      };
    });
  }, [degreeToAngle, getPosition, houseCusps, outerRadius, zodiacInnerRadius]);

  const aspectLines = useMemo(() => {
    type Line = {
      key: string;
      planet1: { body: string; x: number; y: number; disc: number };
      planet2: { body: string; x: number; y: number; disc: number };
      aspect: Aspect;
      color: string;
      dash: string;
      opacity: number;
      width: number;
      label: string;
      stack: number;
      weight: string;
    };

    const buildFromCallouts = (callouts: Aspect[]): Line[] => {
      const lines: Line[] = [];
      for (const aspect of callouts) {
        const pair = parseAspectBodyPair(aspect.bodies);
        if (!pair) continue;
        const [body1, body2] = pair;
        const planet1 = planetsWithPositions.find((p) => planetTokensMatch(String(p.body || ""), body1));
        const planet2 = planetsWithPositions.find((p) => planetTokensMatch(String(p.body || ""), body2));
        if (!planet1 || !planet2) continue;
        const style = aspectStyle(aspect);
        if (!isMajorNatalAspect(style.kind)) continue;
        const disc1 = planetDisc * (planet1.discScale ?? 1);
        const disc2 = planetDisc * (planet2.discScale ?? 1);
        lines.push({
          key: `${aspect.aspect_id}-${planet1.body}-${planet2.body}`,
          planet1: { body: planet1.body, x: planet1.position.x, y: planet1.position.y, disc: disc1 },
          planet2: { body: planet2.body, x: planet2.position.x, y: planet2.position.y, disc: disc2 },
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
      lines.sort((a, b) => a.stack - b.stack);
      return lines;
    };

    // Kitchen SoT for the painted web: majors from longitudes (full 10-planet graph).
    // API callouts stay editorial/list SoT elsewhere; they are too sparse (BODY_PAIRS)
    // and used to be anchored only in the shrunk center well.
    const derived = deriveMajorAspectCalloutsFromLongitudes(
      planetsWithPositions.map((p) => ({ body: String(p.body), longitude: Number(p.longitude) })),
    ).map((c) => ({
      aspect_id: c.aspect_id,
      bodies: c.bodies,
      label: c.label,
      keywords: [] as string[],
      description: "",
      tension_level: c.tension_level,
    }));
    const fromLongitudes = buildFromCallouts(derived);
    if (fromLongitudes.length > 0) return fromLongitudes;

    return buildFromCallouts(aspectsProp ?? []);
  }, [aspectStyle, aspectsProp, planetDisc, planetsWithPositions]);

  const aspectSummary = useMemo(() => {
    const counter = new Map<string, number>();
    for (const line of aspectLines) {
      counter.set(line.label, (counter.get(line.label) || 0) + 1);
    }
    return Array.from(counter.entries()).map(([label, count]) => ({ label, count }));
  }, [aspectLines]);

  /** Selection (or desktop hover) organizes the wheel: only this planet’s major links light up. */
  const focusPlanet = selectedPlanet ?? (isMobile ? null : hoveredPlanet);

  const focusBodies = useMemo(() => {
    if (!focusPlanet) return null;
    const set = new Set<string>([focusPlanet]);
    for (const line of aspectLines) {
      if (line.planet1.body === focusPlanet || line.planet2.body === focusPlanet) {
        set.add(line.planet1.body);
        set.add(line.planet2.body);
      }
    }
    return set;
  }, [aspectLines, focusPlanet]);

  const visibleAspectLines = aspectLines;

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
        </defs>

        {/* Background circle doubles as the tap-to-deselect surface */}
        <circle
          cx={center}
          cy={center}
          r={outerRadius + 4}
          fill={`url(#${gradientId}-chart)`}
          onClick={() => setSelected(null)}
        />

        {/* Layer back: rings / zodiac / houses */}
        <g className={styles.layerBack}>
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
          strokeWidth="1"
          opacity="0.35"
        />

        <circle
          cx={center}
          cy={center}
          r={aspectRadius}
          fill={INK.aspectWell}
          stroke="none"
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
                strokeWidth="1"
                opacity={focusPlanet ? 0.14 : 0.28}
              />
            </g>
          );
        })}

        {houseSegments.map((segment, index) => {
          const nextSegment = houseSegments[(index + 1) % houseSegments.length];
          const labelRadius = houseLabelRadius;
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
                r={isActive ? 11 : 9.5}
                fill={isActive ? INK.gold : "rgba(255,250,242,0.88)"}
                stroke={isActive ? INK.gold : INK.ringSoft}
                strokeWidth={isActive ? "2" : "1.15"}
                opacity={isActive ? 1 : 0.88}
                style={{ transition: "all 0.2s" }}
              />
              <text
                x={segment.x}
                y={segment.y}
                textAnchor="middle"
                dominantBaseline="central"
                fontSize="10"
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
          const pos = getPosition(signAngle, zodiacBandRadius);
          const size = zodiacMarkerR * 2;
          return (
            <image
              key={sign.name}
              href={zodiacOrbAssetPath(sign.slug)}
              x={pos.x - size / 2}
              y={pos.y - size / 2}
              width={size}
              height={size}
              preserveAspectRatio="xMidYMid meet"
              opacity="0.96"
              style={{ pointerEvents: "none" }}
            />
          );
        })}
        </g>

        {/* Layer mid: angle markers only — aspect chords live under planets (not in the old hub well). */}
        <g className={styles.layerMid}>
        {angleMarkers.map((marker) => {
          const size = 22;
          return (
            <g key={marker.key} opacity={focusPlanet ? 0.45 : 0.85}>
              <line
                x1={marker.inner.x}
                y1={marker.inner.y}
                x2={marker.outer.x}
                y2={marker.outer.y}
                stroke={marker.color}
                strokeWidth="1.8"
                opacity="0.7"
              />
              <image
                href={chartAngleAssetPath(marker.slug)}
                x={marker.outer.x - size / 2}
                y={marker.outer.y - size / 2}
                width={size}
                height={size}
                preserveAspectRatio="xMidYMid meet"
                style={{ pointerEvents: "none" }}
              />
            </g>
          );
        })}
        </g>

        {/* Layer front: major chords → hub → lit discs */}
        <g className={styles.layerFront}>
        {/* Major aspect chords: disc-to-disc across the plate (halo + legend color). */}
        <g data-testid="natal-aspect-web" style={{ pointerEvents: "none" }}>
          {visibleAspectLines.map((line) => {
            const isLinked =
              !focusPlanet ||
              line.planet1.body === focusPlanet ||
              line.planet2.body === focusPlanet;
            const opacity = !focusPlanet
              ? Math.min(line.opacity * 0.92, 0.96)
              : isLinked
                ? Math.min(line.opacity + 0.08, 1)
                : 0.1;
            const width = !focusPlanet
              ? line.width
              : isLinked
                ? line.width + 1.1
                : Math.max(line.width - 0.45, 1);
            const chord = aspectChordEnds(
              { x: line.planet1.x, y: line.planet1.y },
              { x: line.planet2.x, y: line.planet2.y },
              line.planet1.disc * 0.88,
              line.planet2.disc * 0.88,
            );
            return (
              <g
                key={line.key}
                data-testid={focusPlanet && isLinked ? "natal-aspect-focus" : "natal-aspect-line"}
              >
                <line
                  x1={chord.x1}
                  y1={chord.y1}
                  x2={chord.x2}
                  y2={chord.y2}
                  stroke={NATAL_ASPECT_HALO}
                  strokeWidth={width + (isLinked && focusPlanet ? 4.2 : 3.2)}
                  opacity={isLinked || !focusPlanet ? 0.88 : 0.2}
                  strokeLinecap="round"
                />
                {isLinked && focusPlanet ? (
                  <line
                    x1={chord.x1}
                    y1={chord.y1}
                    x2={chord.x2}
                    y2={chord.y2}
                    stroke={line.color}
                    strokeWidth={width + (line.weight === "strong" ? 4.5 : 3.2)}
                    opacity={Math.max(opacity - 0.42, 0.06)}
                    strokeLinecap="round"
                    filter={`url(#${softGlowId})`}
                  />
                ) : null}
                <line
                  x1={chord.x1}
                  y1={chord.y1}
                  x2={chord.x2}
                  y2={chord.y2}
                  stroke={line.color}
                  strokeWidth={width}
                  opacity={opacity}
                  strokeDasharray={line.dash === "none" ? undefined : line.dash}
                  strokeLinecap="round"
                />
              </g>
            );
          })}
        </g>

        {/* Element hub — one badge; sits above chord crossings, under planet discs. */}
        <g
          data-wheel-hit
          onClick={() => setSelected(null)}
          style={{ cursor: "pointer" }}
        >
          <circle
            cx={center}
            cy={center}
            r={Math.max(aspectHubRadius * 0.78, 36)}
            fill="rgba(255, 252, 246, 0.92)"
            stroke={INK.gold}
            strokeWidth="1.25"
          />
          <foreignObject
            x={center - Math.max(aspectHubRadius * 0.78, 36)}
            y={center - Math.max(aspectHubRadius * 0.78, 36)}
            width={Math.max(aspectHubRadius * 0.78, 36) * 2}
            height={Math.max(aspectHubRadius * 0.78, 36) * 2}
            style={{ pointerEvents: "none", overflow: "visible" }}
          >
            <div
              data-testid="natal-chart-element-hub"
              style={{
                width: "100%",
                height: "100%",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                gap: "0.15rem",
                fontFamily: "var(--tf-font-display, Georgia, serif)",
              }}
            >
              <ElementIcon element={stageElement} size={20} stroke={INK.gold} />
              <span
                style={{
                  fontSize: "0.9rem",
                  fontWeight: 600,
                  letterSpacing: "0.06em",
                  color: INK.inkDeep,
                  lineHeight: 1.1,
                }}
              >
                {stageElement === "fire"
                  ? "Огонь"
                  : stageElement === "water"
                    ? "Вода"
                    : stageElement === "air"
                      ? "Воздух"
                      : "Земля"}
              </span>
            </div>
          </foreignObject>
        </g>

        {planetsWithPositions.map((planet, idx) => {
          const isSelected = selectedPlanet === planet.body;
          const isActive = activePlanet === planet.body;
          const inFocus = !focusBodies || focusBodies.has(planet.body);
          const planetColors = INK.planet;
          const planetColor = planetColors[planet.body as keyof typeof planetColors] || INK.gold;
          const jewel = resolveNatalPlanetJewel(planet.sign);
          const rimColor = jewel?.stroke || planetColor;
          const disc = planetDisc * (planet.discScale ?? 1);
          const discR = isActive ? disc + 2 : disc;
          const slug = resolvePlanetSlug(planet.body);
          const photoSlug = slug && planetHasPhotoAsset(slug) ? slug : null;
          const clipId = `${gradientId}-planet-clip-${idx}`;

          return (
            <g
              key={`planet-${planet.body}-${idx}`}
              data-wheel-hit
              data-element={jewel?.element || undefined}
              onClick={() => togglePlanet(planet.body)}
              onMouseEnter={() => setHoveredPlanet(planet.body)}
              onMouseLeave={() => setHoveredPlanet(null)}
              filter={`url(#${planetShadowId})`}
              opacity={inFocus ? 1 : 0.28}
              style={{ transition: "opacity 0.25s ease" }}
            >
              <g filter={isActive ? `url(#${planetGlowId})` : undefined}>
                <circle cx={planet.position.x} cy={planet.position.y} r={disc + 10} fill="transparent" />
                {/* Soft element bloom — mood glow around the sphere */}
                {jewel ? (
                  <circle
                    cx={planet.position.x}
                    cy={planet.position.y}
                    r={disc + (isActive ? 7 : 5.5)}
                    fill={jewel.glow}
                    opacity={isSelected ? 0.85 : isActive ? 0.7 : 0.5}
                    style={{ pointerEvents: "none", transition: "all 0.3s ease" }}
                  />
                ) : null}
                {photoSlug ? (
                  <>
                    <clipPath id={clipId}>
                      <circle cx={planet.position.x} cy={planet.position.y} r={discR} />
                    </clipPath>
                    {/* Full-sphere photo fill (kit principle: texture covers the disc). */}
                    <image
                      href={planetPhotoPath(photoSlug)}
                      x={planet.position.x - discR}
                      y={planet.position.y - discR}
                      width={discR * 2}
                      height={discR * 2}
                      preserveAspectRatio="xMidYMid slice"
                      clipPath={`url(#${clipId})`}
                      style={{ pointerEvents: "none" }}
                    />
                    <circle
                      cx={planet.position.x}
                      cy={planet.position.y}
                      r={discR}
                      fill="none"
                      stroke={rimColor}
                      strokeWidth={isActive ? "2.4" : "1.75"}
                      style={{ transition: "all 0.3s ease" }}
                    />
                    {jewel ? (
                      <circle
                        cx={planet.position.x}
                        cy={planet.position.y}
                        r={discR - 0.8}
                        fill="none"
                        stroke={jewel.wash}
                        strokeWidth="1.6"
                        opacity={0.4}
                        style={{ pointerEvents: "none" }}
                      />
                    ) : null}
                    {/* Soft rim light — volume without covering the texture */}
                    <circle
                      cx={planet.position.x - discR * 0.32}
                      cy={planet.position.y - discR * 0.36}
                      r={discR * 0.22}
                      fill="#ffffff"
                      opacity={isSelected ? 0.28 : 0.18}
                      style={{ pointerEvents: "none", transition: "all 0.3s ease" }}
                    />
                  </>
                ) : (
                  <>
                    <circle
                      cx={planet.position.x}
                      cy={planet.position.y}
                      r={discR}
                      fill={isSelected ? `url(#${planetLitSelectedId})` : `url(#${planetLitId})`}
                      stroke={rimColor}
                      strokeWidth={isActive ? "2.4" : "1.75"}
                      style={{ transition: "all 0.3s ease" }}
                    />
                    {jewel ? (
                      <circle
                        cx={planet.position.x}
                        cy={planet.position.y}
                        r={discR - 0.6}
                        fill="none"
                        stroke={jewel.wash}
                        strokeWidth="2.2"
                        opacity={0.55}
                        style={{ pointerEvents: "none" }}
                      />
                    ) : null}
                    <circle
                      cx={planet.position.x - disc * 0.28}
                      cy={planet.position.y - disc * 0.32}
                      r={disc * 0.28}
                      fill="#ffffff"
                      opacity={isSelected ? 0.55 : 0.42}
                      style={{ pointerEvents: "none", transition: "all 0.3s ease" }}
                    />
                    {slug ? (
                      <foreignObject
                        x={planet.position.x - disc * 0.72}
                        y={planet.position.y - disc * 0.72}
                        width={disc * 1.44}
                        height={disc * 1.44}
                        style={{ pointerEvents: "none", overflow: "visible" }}
                      >
                        <div
                          style={{
                            width: "100%",
                            height: "100%",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          <PlanetIcon
                            planet={planet.body}
                            size={Math.max(13, Math.round(disc * 1.22))}
                            stroke={isSelected ? INK.inkDeep : rimColor}
                          />
                        </div>
                      </foreignObject>
                    ) : (
                      <text
                        x={planet.position.x}
                        y={planet.position.y}
                        textAnchor="middle"
                        dominantBaseline="central"
                        fontSize={isMobile ? (isActive ? "15" : "13") : isActive ? "17" : "15"}
                        fill={isSelected ? INK.inkDeep : rimColor}
                        fontWeight="700"
                        style={{ transition: "all 0.3s ease", pointerEvents: "none" }}
                      >
                        {planet.symbol}
                      </text>
                    )}
                  </>
                )}
              </g>
            </g>
          );
        })}
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
                      <PlanetIcon planet={planet.body} size={17} fit="cover" />
                    </span>
                    {planetRuName(planet.body)}
                  </button>
                );
              })}
            </div>
          </div>
          {!isMobile || selectedPlanet ? (
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
                <PlanetIcon planet={selectedPlanetData.body} size={24} fit="cover" />
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
            Выбери планету — между дисками загорятся её мажорные связи (цвета как в легенде), ниже — знак, дом и список.
          </p>
        )}
      </div>
      </div>
    </div>
  );
}
