"use client";

import { useMemo, useState, useCallback, useId } from "react";
import { eclipticLongitudeFromSignAndDegree, zodiacRuName } from "@/lib/zodiacKnowledge";
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

/** Cream / gold engraving palette — no blues, purples, or acid accents. */
const INK = {
  parchment0: "#fefcf9",
  parchment1: "#f7f0e5",
  parchment2: "#ece1d1",
  creamFill: "#fffaf2",
  creamSoft: "#fffaf4",
  ringOuter: "#ccb391",
  ringMid: "#dcc8ae",
  ringInner: "#cdb79a",
  ringSoft: "#d4c5b0",
  gold: "#8b6a3e",
  goldBright: "#c9a96e",
  goldMuted: "#c6a677",
  umber: "#53402a",
  ink: "#5f4930",
  inkDeep: "#3d3228",
  silver: "#9a9590",
  white: "#ffffff",
  aspect: {
    conjunction: { color: "#8b6a3e", dash: "none", opacity: 0.78, width: 2.2 },
    opposition: { color: "#6b5340", dash: "8 5", opacity: 0.72, width: 2.4 },
    square: { color: "#a67c52", dash: "6 5", opacity: 0.7, width: 2.2 },
    trine: { color: "#c9a96e", dash: "none", opacity: 0.62, width: 1.9 },
    sextile: { color: "#b8956a", dash: "4 4", opacity: 0.58, width: 1.7 },
    other: { color: "#9a8b78", dash: "3 4", opacity: 0.5, width: 1.5 },
  },
  elementFill: {
    fire: "rgba(139, 106, 62, 0.1)",
    earth: "rgba(83, 64, 42, 0.08)",
    air: "rgba(201, 169, 110, 0.1)",
    water: "rgba(154, 149, 144, 0.1)",
  } as Record<string, string>,
  elementStroke: {
    fire: "#8b6a3e",
    earth: "#53402a",
    air: "#c9a96e",
    water: "#7a7570",
  } as Record<string, string>,
  angle: {
    ASC: "#8b6a3e",
    IC: "#7a7570",
    DSC: "#9a8b78",
    MC: "#c9a96e",
  } as Record<string, string>,
  planet: {
    Sun: "#c9a96e",
    Moon: "#9a9590",
    Mercury: "#8b7355",
    Venus: "#b8956a",
    Mars: "#8b6a3e",
    Jupiter: "#c9a96e",
    Saturn: "#53402a",
    Uranus: "#8b7355",
    Neptune: "#7a7570",
    Pluto: "#5f4930",
  } as Record<string, string>,
} as const;

/**
 * Interactive natal chart wheel.
 *
 * Selection is click/tap-driven (touch-first): tapping a planet or house opens a
 * detail panel under the plate; hover only pre-highlights on pointer devices.
 * The old hover-only SVG tooltips were unreachable on mobile.
 */
export function NatalChartWheel({ chartPositions, houses = {}, ascendant = 0, aspects: aspectsProp = [] }: NatalChartWheelProps) {
  const size = 720;
  const center = size / 2;
  const outerRadius = size / 2 - 44;
  const zodiacInnerRadius = outerRadius - 42;
  const innerRadius = outerRadius * 0.56;
  const aspectRadius = innerRadius - 18;
  const houseRadius = (outerRadius + innerRadius) / 2;
  const basePlanetRadius = zodiacInnerRadius - 14;
  const planetRadiusVariation = 34;
  const gradientId = useId().replace(/:/g, "");
  const softGlowId = `${gradientId}-glow`;
  const webClipId = `${gradientId}-clip`;
  const planetGlowId = `${gradientId}-planet-glow`;

  const [selected, setSelected] = useState<WheelSelection>(null);
  const [hoveredPlanet, setHoveredPlanet] = useState<string | null>(null);

  const selectedPlanet = selected?.kind === "planet" ? selected.body : null;
  const selectedHouse = selected?.kind === "house" ? selected.number : null;
  const activePlanet = selectedPlanet ?? hoveredPlanet;

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

  const describeAspectKind = useCallback((aspect: Aspect) => {
    const aspectId = aspect.aspect_id?.toLowerCase() || "";
    if (aspectId.includes("conjunction")) return "Соединение";
    if (aspectId.includes("opposition")) return "Оппозиция";
    if (aspectId.includes("square")) return "Квадрат";
    if (aspectId.includes("trine")) return "Трин";
    if (aspectId.includes("sextile")) return "Секстиль";
    return aspect.label || "Связь";
  }, []);

  const aspectStyle = useCallback((aspect: Aspect) => {
    const aspectId = aspect.aspect_id?.toLowerCase() || "";
    if (aspectId.includes("conjunction")) {
      return { ...INK.aspect.conjunction, label: "Соединение" };
    }
    if (aspectId.includes("opposition")) {
      return { ...INK.aspect.opposition, label: "Оппозиция" };
    }
    if (aspectId.includes("square")) {
      return { ...INK.aspect.square, label: "Квадрат" };
    }
    if (aspectId.includes("trine")) {
      return { ...INK.aspect.trine, label: "Трин" };
    }
    if (aspectId.includes("sextile")) {
      return { ...INK.aspect.sextile, label: "Секстиль" };
    }
    return { ...INK.aspect.other, label: describeAspectKind(aspect) };
  }, [describeAspectKind]);

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

    // First pass: calculate all planet angles using longitude (точное позиционирование)
    const planetsWithAngles = filtered.map((p) => {
      // Используем longitude для точного позиционирования, если нет - вычисляем из sign + degree
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

    // Second pass: distribute planets on different radii to avoid overlap
    // Sort planets by angle
    const sortedPlanets = [...planetsWithAngles].sort((a, b) => a.angle - b.angle);

    // Assign radius offsets based on proximity to other planets
    const planetsWithOffsets = sortedPlanets.map((planet, index) => {
      let radiusOffset = 0;

      // Check proximity to previous and next planets
      const prevPlanet = sortedPlanets[index > 0 ? index - 1 : sortedPlanets.length - 1];
      const nextPlanet = sortedPlanets[(index + 1) % sortedPlanets.length];

      // Calculate angular distance to neighbors
      const distToPrev = Math.min(
        Math.abs(planet.angle - prevPlanet.angle),
        360 - Math.abs(planet.angle - prevPlanet.angle)
      );
      const distToNext = Math.min(
        Math.abs(nextPlanet.angle - planet.angle),
        360 - Math.abs(nextPlanet.angle - planet.angle)
      );

      // If planets are within 12 degrees, offset them across radii
      const minDistance = Math.min(distToPrev, distToNext);
      if (minDistance < 12) {
        // Use a spiral pattern to distribute planets
        // Calculate how many planets are in this cluster
        let clusterSize = 1;
        let checkIndex = index;

        // Count consecutive close planets
        while (checkIndex < sortedPlanets.length - 1) {
          const nextDist = Math.min(
            Math.abs(sortedPlanets[checkIndex + 1].angle - sortedPlanets[checkIndex].angle),
            360 - Math.abs(sortedPlanets[checkIndex + 1].angle - sortedPlanets[checkIndex].angle)
          );
          if (nextDist < 12) {
            clusterSize++;
            checkIndex++;
          } else {
            break;
          }
        }

        // Find position within cluster
        let positionInCluster = 0;
        for (let i = index; i > 0; i--) {
          const prevDist = Math.min(
            Math.abs(sortedPlanets[i].angle - sortedPlanets[i - 1].angle),
            360 - Math.abs(sortedPlanets[i].angle - sortedPlanets[i - 1].angle)
          );
          if (prevDist < 12) {
            positionInCluster++;
          } else {
            break;
          }
        }

        // Distribute evenly around base radius
        const clusterOffset = (positionInCluster - (clusterSize - 1) / 2) * planetRadiusVariation;
        radiusOffset = clusterOffset;
      }

      return { ...planet, radiusOffset };
    });

    // Calculate final positions
    return planetsWithOffsets.map((p) => {
      const finalRadius = basePlanetRadius + p.radiusOffset;
      const position = getPosition(p.angle, finalRadius);

      // Find which house this planet is in
      const planetHouse = houseCusps.findIndex((cusp, i) => {
        const nextCusp = houseCusps[(i + 1) % 12];
        const normalizedDegree = p.degree % 360;
        const normalizedCusp = cusp % 360;
        const normalizedNext = nextCusp % 360;

        if (normalizedNext > normalizedCusp) {
          return normalizedDegree >= normalizedCusp && normalizedDegree < normalizedNext;
        } else {
          return normalizedDegree >= normalizedCusp || normalizedDegree < normalizedNext;
        }
      }) + 1;

      return {
        ...p,
        position,
        house: p.house ?? planetHouse,
        symbol: planetSymbols[p.body] || p.body.substring(0, 3),
        radius: finalRadius,
      };
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chartPositions, houseCusps, basePlanetRadius, planetRadiusVariation, getPosition, planetSymbols]);

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
        outer: getPosition(angle, outerRadius + 24),
        inner: getPosition(angle, zodiacInnerRadius - 8),
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
      });
    }

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
    <div className={styles.root} data-testid="natal-chart-wheel">
      <div className={styles.plate}>
        <svg
          className={styles.svg}
          viewBox={`0 0 ${size} ${size}`}
          role="img"
          aria-label="Натальная карта"
        >
        <defs>
          <radialGradient id={`${gradientId}-chart`} cx="50%" cy="50%">
            <stop offset="0%" stopColor={INK.parchment0} stopOpacity="1" />
            <stop offset="62%" stopColor={INK.parchment1} stopOpacity="1" />
            <stop offset="100%" stopColor={INK.parchment2} stopOpacity="1" />
          </radialGradient>
          <filter id={softGlowId}>
            <feGaussianBlur stdDeviation="5" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id={planetGlowId}>
            <feGaussianBlur stdDeviation="3.5" result="planetBlur" />
            <feMerge>
              <feMergeNode in="planetBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <clipPath id={webClipId}>
            <circle cx={center} cy={center} r={innerRadius - 2} />
          </clipPath>
        </defs>

        {/* Background circle doubles as the tap-to-deselect surface */}
        <circle
          cx={center}
          cy={center}
          r={outerRadius + 16}
          fill={`url(#${gradientId}-chart)`}
          onClick={() => setSelected(null)}
        />

        <circle
          cx={center}
          cy={center}
          r={outerRadius + 8}
          fill="none"
          stroke="rgba(255,255,255,0.74)"
          strokeWidth="18"
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
          fill="rgba(255,255,255,0.42)"
          stroke="rgba(198, 166, 119, 0.18)"
          strokeWidth="1"
          onClick={() => setSelected(null)}
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
                r={isActive ? 19 : 15}
                fill={isActive ? INK.gold : INK.creamFill}
                stroke={isActive ? INK.gold : INK.ringSoft}
                strokeWidth={isActive ? "2.5" : "1.5"}
                opacity={isActive ? 1 : 0.85}
                style={{ transition: "all 0.2s" }}
              />
              <text
                x={segment.x}
                y={segment.y}
                textAnchor="middle"
                dominantBaseline="central"
                fontSize="15"
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
          const pos = getPosition(signAngle, outerRadius + 10);
          const elementColors = INK.elementStroke;
          return (
            <g key={sign.name}>
              <circle
                cx={pos.x}
                cy={pos.y}
                r="19"
                fill={INK.white}
                stroke={elementColors[sign.element] || INK.gold}
                strokeWidth="2"
                opacity="0.9"
              />
              <text
                x={pos.x}
                y={pos.y}
                textAnchor="middle"
                dominantBaseline="central"
                fontSize="20"
                fill={elementColors[sign.element] || INK.gold}
                fontWeight="700"
              >
                {sign.glyph}
              </text>
            </g>
          );
        })}

        <g clipPath={`url(#${webClipId})`}>
          {aspectLines.map((line) => {
            const isLinked =
              activePlanet != null &&
              (line.planet1.body === activePlanet || line.planet2.body === activePlanet);
            // With a planet active, its web comes forward and the rest recedes.
            const opacity = activePlanet == null ? line.opacity : isLinked ? Math.min(line.opacity + 0.22, 1) : 0.1;
            const width = isLinked ? line.width + 0.7 : line.width;
            return (
              <g key={line.key}>
                <line
                  x1={line.planet1.anchor.x}
                  y1={line.planet1.anchor.y}
                  x2={line.planet2.anchor.x}
                  y2={line.planet2.anchor.y}
                  stroke={line.color}
                  strokeWidth={width + 4}
                  opacity={Math.max(opacity - 0.45, 0.04)}
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
            r={aspectRadius - 44}
            fill="rgba(255,255,255,0.45)"
            stroke="rgba(198, 166, 119, 0.12)"
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
          const edgePos = getPosition(planet.angle, outerRadius);
          const isActive = activePlanet === planet.body;
          return (
            <line
              key={`planet-radial-${planet.body}-${index}`}
              x1={planet.position.x}
              y1={planet.position.y}
              x2={edgePos.x}
              y2={edgePos.y}
              stroke={isActive ? INK.goldBright : INK.ringSoft}
              strokeWidth={isActive ? "1.5" : "0.8"}
              opacity={isActive ? 0.6 : 0.3}
              strokeDasharray="2,4"
              style={{ transition: "all 0.3s ease" }}
            />
          );
        })}

        {planetsWithPositions.map((planet, idx) => {
          const isSelected = selectedPlanet === planet.body;
          const isActive = activePlanet === planet.body;
          const planetColors = INK.planet;
          const planetColor = planetColors[planet.body as keyof typeof planetColors] || INK.gold;

          return (
            <g
              key={`planet-${planet.body}-${idx}`}
              data-wheel-hit
              onClick={() => togglePlanet(planet.body)}
              onMouseEnter={() => setHoveredPlanet(planet.body)}
              onMouseLeave={() => setHoveredPlanet(null)}
              filter={isActive ? `url(#${planetGlowId})` : undefined}
            >
              {/* Generous invisible hit area for touch */}
              <circle cx={planet.position.x} cy={planet.position.y} r={30} fill="transparent" />
              <circle
                cx={planet.position.x}
                cy={planet.position.y}
                r={isActive ? 24 : 20}
                fill={isSelected ? planetColor : isActive ? "#ffffff" : "#fffaf4"}
                stroke={planetColor}
                strokeWidth={isActive ? "3" : "2"}
                style={{ transition: "all 0.3s ease" }}
              />
              <text
                x={planet.position.x}
                y={planet.position.y}
                textAnchor="middle"
                dominantBaseline="central"
                fontSize={isActive ? "24" : "22"}
                fill={isSelected ? INK.white : planetColor}
                fontWeight="700"
                style={{ transition: "all 0.3s ease", pointerEvents: "none" }}
              >
                {planet.symbol}
              </text>
            </g>
          );
        })}

        <circle
          cx={center}
          cy={center}
          r="35"
          fill={`url(#${gradientId}-chart)`}
          stroke={INK.ringSoft}
          strokeWidth="2.5"
          onClick={() => setSelected(null)}
        />
        <circle
          cx={center}
          cy={center}
          r="25"
          fill={INK.white}
          stroke={INK.gold}
          strokeWidth="2"
          opacity="0.9"
          onClick={() => setSelected(null)}
        />
        <text
          x={center}
          y={center}
          textAnchor="middle"
          dominantBaseline="central"
          fontSize="11"
          fill={INK.gold}
          fontWeight="700"
          style={{ pointerEvents: "none" }}
        >
          TF
        </text>
        </svg>
      </div>

      {/* Detail panel — selection target for both tap (mobile) and click (desktop) */}
      <div className={styles.panel} data-testid="natal-chart-detail" aria-live="polite">
        {selectedPlanetData ? (
          <>
            <div className={styles.panelHeader}>
              <span className={styles.panelGlyph} aria-hidden>
                {selectedPlanetData.symbol}
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
            Нажми на планету или номер дома — здесь откроются её знак, дом, градус и все связи в карте.
          </p>
        )}
      </div>

      {/* Planet rail — same selection, reachable without aiming at the wheel */}
      <div className={styles.chipRail} data-testid="natal-chart-planet-rail">
        {planetsWithPositions.map((planet) => {
          const planetColors = INK.planet;
          const planetColor = planetColors[planet.body as keyof typeof planetColors] || INK.gold;
          const isActive = selectedPlanet === planet.body;
          return (
            <button
              key={planet.body}
              type="button"
              className={`${styles.chip} ${isActive ? styles.chipActive : ""}`.trim()}
              onClick={() => togglePlanet(planet.body)}
              aria-pressed={isActive}
            >
              <span className={styles.chipGlyph} style={isActive ? undefined : { color: planetColor }} aria-hidden>
                {planet.symbol}
              </span>
              {planetRuName(planet.body)}
            </button>
          );
        })}
      </div>

      <div className={styles.legend} aria-label="Типы аспектов">
        {[
          { label: "Соединение", color: INK.aspect.conjunction.color, dash: INK.aspect.conjunction.dash },
          { label: "Трин", color: INK.aspect.trine.color, dash: INK.aspect.trine.dash },
          { label: "Секстиль", color: INK.aspect.sextile.color, dash: INK.aspect.sextile.dash },
          { label: "Квадрат", color: INK.aspect.square.color, dash: INK.aspect.square.dash },
          { label: "Оппозиция", color: INK.aspect.opposition.color, dash: INK.aspect.opposition.dash },
        ].map((item) => {
          const count = aspectSummary.find((entry) => entry.label === item.label)?.count || 0;
          return (
            <div key={item.label} className={styles.legendItem}>
              <svg width="28" height="10" viewBox="0 0 28 10" aria-hidden="true">
                <line x1="1" y1="5" x2="27" y2="5" stroke={item.color} strokeWidth="2.4" strokeDasharray={item.dash} strokeLinecap="round" />
              </svg>
              <span>{item.label}{count ? ` · ${count}` : ""}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
