"use client";

import { useMemo, useState, useCallback, useId } from "react";
import { eclipticLongitudeFromSignAndDegree, zodiacRuName } from "@/lib/zodiacKnowledge";

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

/**
 * Interactive natal chart wheel visualization
 */
export function NatalChartWheel({ chartPositions, houses = {}, ascendant = 0, aspects: aspectsProp = [] }: NatalChartWheelProps) {
  const size = 720;
  const center = size / 2;
  const outerRadius = size / 2 - 44;
  const zodiacInnerRadius = outerRadius - 42;
  const innerRadius = outerRadius * 0.56;
  const aspectRadius = innerRadius - 18;
  const houseRadius = (outerRadius + innerRadius) / 2;
  const basePlanetRadius = zodiacInnerRadius - 12;
  const planetRadiusVariation = 26;
  const gradientId = useId().replace(/:/g, "");
  const shadowId = `${gradientId}-shadow`;
  const softGlowId = `${gradientId}-glow`;
  const webClipId = `${gradientId}-clip`;
  const planetGlowId = `${gradientId}-planet-glow`;

  const [hoveredPlanet, setHoveredPlanet] = useState<string | null>(null);
  const [hoveredHouse, setHoveredHouse] = useState<number | null>(null);
  const [hoveredAspect, setHoveredAspect] = useState<string | null>(null);

  // Planet symbols (memoized to avoid recreating on every render)
  const planetSymbols: Record<string, string> = useMemo(() => ({
    Sun: "☉",
    sun: "☉",
    Moon: "☽",
    moon: "☽",
    Mercury: "☿",
    mercury: "☿",
    Venus: "♀",
    venus: "♀",
    Mars: "♂",
    mars: "♂",
    Jupiter: "♃",
    jupiter: "♃",
    Saturn: "♄",
    saturn: "♄",
    Uranus: "♅",
    uranus: "♅",
    Neptune: "♆",
    neptune: "♆",
    Pluto: "♇",
    pluto: "♇",
    Chiron: "⚷",
    chiron: "⚷",
    "North Node": "☊",
    north_node: "☊",
    "South Node": "☋",
    south_node: "☋",
    Ascendant: "ASC",
    rising: "ASC",
    MC: "MC",
    IC: "IC",
    DSC: "DSC",
    Lilith: "⚸",
    lilith: "⚸",
    "Part of Fortune": "⊗",
  }), []);

  // Zodiac signs with their glyphs
  const zodiacSigns = useMemo(() => [
    { name: "Aries", glyph: "♈", element: "fire" },
    { name: "Taurus", glyph: "♉", element: "earth" },
    { name: "Gemini", glyph: "♊", element: "air" },
    { name: "Cancer", glyph: "♋", element: "water" },
    { name: "Leo", glyph: "♌", element: "fire" },
    { name: "Virgo", glyph: "♍", element: "earth" },
    { name: "Libra", glyph: "♎", element: "air" },
    { name: "Scorpio", glyph: "♏", element: "water" },
    { name: "Sagittarius", glyph: "♐", element: "fire" },
    { name: "Capricorn", glyph: "♑", element: "earth" },
    { name: "Aquarius", glyph: "♒", element: "air" },
    { name: "Pisces", glyph: "♓", element: "water" },
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
      return { color: "#4a90e2", dash: "none", opacity: 0.72, width: 2.4, label: "Соединение" };
    }
    if (aspectId.includes("opposition")) {
      return { color: "#d9485f", dash: "8 5", opacity: 0.88, width: 2.8, label: "Оппозиция" };
    }
    if (aspectId.includes("square")) {
      return { color: "#f08c2b", dash: "6 5", opacity: 0.84, width: 2.6, label: "Квадрат" };
    }
    if (aspectId.includes("trine")) {
      return { color: "#1f9d74", dash: "none", opacity: 0.7, width: 2.2, label: "Трин" };
    }
    if (aspectId.includes("sextile")) {
      return { color: "#4c87ff", dash: "4 4", opacity: 0.68, width: 2, label: "Секстиль" };
    }
    return { color: "#8b94a7", dash: "3 4", opacity: 0.56, width: 1.7, label: describeAspectKind(aspect) };
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
      
      // If planets are within 10 degrees, offset them (increased threshold)
      const minDistance = Math.min(distToPrev, distToNext);
      if (minDistance < 10) {
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
          if (nextDist < 10) {
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
          if (prevDist < 10) {
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
      { key: "ASC", degree: houseCusps[0], color: "#8b5cf6" },
      { key: "IC", degree: houseCusps[3], color: "#0ea5e9" },
      { key: "DSC", degree: houseCusps[6], color: "#ec4899" },
      { key: "MC", degree: houseCusps[9], color: "#f59e0b" },
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
      planet1: { body: string; position: { x: number; y: number }; anchor: { x: number; y: number } };
      planet2: { body: string; position: { x: number; y: number }; anchor: { x: number; y: number } };
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
      
      if (planet1 && planet2) {
        const style = aspectStyle(aspect);
        const anchor1 = getPosition(planet1.angle, aspectRadius);
        const anchor2 = getPosition(planet2.angle, aspectRadius);
        lines.push({
          key: `${aspect.aspect_id}-${planet1.body}-${planet2.body}`,
          planet1: { body: planet1.body, position: planet1.position, anchor: anchor1 },
          planet2: { body: planet2.body, position: planet2.position, anchor: anchor2 },
          aspect,
          color: style.color,
          dash: style.dash,
          opacity: style.opacity,
          width: style.width,
          label: style.label,
        });
      }
    }

    return lines;
  }, [aspectRadius, aspectStyle, aspectsProp, getPosition, planetsWithPositions]);

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
    <div style={{ 
      width: "100%", 
      maxWidth: size, 
      margin: "0 auto",
      padding: "clamp(0.9rem, 2vw, 1.3rem)",
      background: "radial-gradient(circle at top, rgba(255,255,255,0.96), rgba(244,237,226,0.94) 48%, rgba(236,227,213,0.92) 100%)",
      borderRadius: "28px",
      boxShadow: "0 18px 48px rgba(112, 92, 63, 0.12)",
      border: "1px solid rgba(198, 166, 119, 0.16)",
    }}>
      <svg
        width="100%"
        viewBox={`0 0 ${size} ${size}`}
        style={{ display: "block", aspectRatio: "1 / 1", height: "auto", overflow: "visible" }}
      >
        <defs>
          <radialGradient id={`${gradientId}-chart`} cx="50%" cy="50%">
            <stop offset="0%" stopColor="#fefcf9" stopOpacity="1" />
            <stop offset="62%" stopColor="#f7f0e5" stopOpacity="1" />
            <stop offset="100%" stopColor="#ece1d1" stopOpacity="1" />
          </radialGradient>
          <filter id={shadowId}>
            <feGaussianBlur in="SourceAlpha" stdDeviation="2" />
            <feOffset dx="0" dy="2" result="offsetblur" />
            <feComponentTransfer>
              <feFuncA type="linear" slope="0.3" />
            </feComponentTransfer>
            <feMerge>
              <feMergeNode />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
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
        
        <circle
          cx={center}
          cy={center}
          r={outerRadius + 16}
          fill={`url(#${gradientId}-chart)`}
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
          stroke="#ccb391"
          strokeWidth="2.5"
        />

        <circle
          cx={center}
          cy={center}
          r={zodiacInnerRadius}
          fill="none"
          stroke="#dcc8ae"
          strokeWidth="1.3"
          opacity="0.82"
        />

        <circle
          cx={center}
          cy={center}
          r={innerRadius}
          fill="none"
          stroke="#cdb79a"
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
          const elementColors: Record<string, string> = {
            fire: "rgba(239, 68, 68, 0.12)",
            earth: "rgba(16, 185, 129, 0.12)",
            air: "rgba(59, 130, 246, 0.12)",
            water: "rgba(99, 102, 241, 0.12)",
          };
          const path = [
            `M ${startOuter.x} ${startOuter.y}`,
            `A ${outerRadius} ${outerRadius} 0 ${largeArc} ${sweep} ${endOuter.x} ${endOuter.y}`,
            `L ${endInner.x} ${endInner.y}`,
            `A ${zodiacInnerRadius} ${zodiacInnerRadius} 0 ${largeArc} 1 ${startInner.x} ${startInner.y}`,
            "Z",
          ].join(" ");
          return <path key={`zodiac-sector-${sign.name}`} d={path} fill={elementColors[sign.element] || "rgba(148,163,184,0.1)"} />;
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
                stroke="#c9b8a3"
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
          const isHovered = hoveredHouse === segment.number;
          return (
            <g
              key={`house-${segment.number}`}
              onMouseEnter={() => setHoveredHouse(segment.number)}
              onMouseLeave={() => setHoveredHouse(null)}
              style={{ cursor: "pointer" }}
            >
              <circle
                cx={segment.x}
                cy={segment.y}
                r={isHovered ? 18 : 14}
                fill={isHovered ? "#6f5ef0" : "#fffaf2"}
                stroke={isHovered ? "#6f5ef0" : "#d4c5b0"}
                strokeWidth={isHovered ? "2.5" : "1.5"}
                opacity={isHovered ? 1 : 0.8}
                style={{ transition: "all 0.2s" }}
              />
              <text
                x={segment.x}
                y={segment.y}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize={isHovered ? "16" : "14"}
                fontWeight="700"
                fill={isHovered ? "#ffffff" : "#8b7355"}
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
              stroke="#e5e0d8"
              strokeWidth="1"
              opacity={0.4}
            />
          );
        })}

        {zodiacSigns.map((sign, i) => {
          const signAngle = degreeToAngle(i * 30 + 15);
          const pos = getPosition(signAngle, outerRadius + 10);
          const elementColors: Record<string, string> = {
            fire: "#ef4444",
            earth: "#10b981",
            air: "#3b82f6",
            water: "#6366f1"
          };
          return (
            <g key={sign.name}>
              <circle
                cx={pos.x}
                cy={pos.y}
                r="17"
                fill="#ffffff"
                stroke={elementColors[sign.element] || "#8b7355"}
                strokeWidth="2"
                opacity="0.9"
              />
              <text
                x={pos.x}
                y={pos.y}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="18"
                fill={elementColors[sign.element] || "#8b7355"}
                fontWeight="700"
              >
                {sign.glyph}
              </text>
            </g>
          );
        })}

        <g clipPath={`url(#${webClipId})`}>
          {aspectLines.map((line) => {
            const isHovered = hoveredAspect === line.key;
            const isPlanetLinked = hoveredPlanet === line.planet1.body || hoveredPlanet === line.planet2.body;
            const opacity = isHovered ? 1 : isPlanetLinked ? Math.min(line.opacity + 0.18, 1) : line.opacity;
            const width = isHovered ? line.width + 1 : isPlanetLinked ? line.width + 0.5 : line.width;
            const mid = {
              x: (line.planet1.anchor.x + line.planet2.anchor.x) / 2,
              y: (line.planet1.anchor.y + line.planet2.anchor.y) / 2,
            };
            return (
              <g
                key={line.key}
                onMouseEnter={() => setHoveredAspect(line.key)}
                onMouseLeave={() => setHoveredAspect(null)}
                style={{ cursor: "pointer" }}
              >
                <line
                  x1={line.planet1.anchor.x}
                  y1={line.planet1.anchor.y}
                  x2={line.planet2.anchor.x}
                  y2={line.planet2.anchor.y}
                  stroke={line.color}
                  strokeWidth={width + 4}
                  opacity={Math.max(opacity - 0.45, 0.08)}
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
                {isHovered ? (
                  <g>
                    <circle cx={mid.x} cy={mid.y} r="16" fill="rgba(15,23,42,0.92)" />
                    <text
                      x={mid.x}
                      y={mid.y}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fontSize="9"
                      fill="#ffffff"
                      fontWeight="700"
                    >
                      {line.label}
                    </text>
                  </g>
                ) : null}
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
            <circle cx={marker.outer.x} cy={marker.outer.y} r="12" fill="#fff" stroke={marker.color} strokeWidth="2" />
            <text
              x={marker.outer.x}
              y={marker.outer.y}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize="9"
              fill={marker.color}
              fontWeight="700"
            >
              {marker.key}
            </text>
          </g>
        ))}

        {planetsWithPositions.map((planet, index) => {
          const edgePos = getPosition(planet.angle, outerRadius);
          const isHovered = hoveredPlanet === planet.body;
          return (
            <line
              key={`planet-radial-${planet.body}-${index}`}
              x1={planet.position.x}
              y1={planet.position.y}
              x2={edgePos.x}
              y2={edgePos.y}
              stroke={isHovered ? "#667eea" : "#d4c5b0"}
              strokeWidth={isHovered ? "1.5" : "0.8"}
              opacity={isHovered ? 0.6 : 0.3}
              strokeDasharray="2,4"
              style={{ transition: "all 0.3s ease" }}
            />
          );
        })}

        {planetsWithPositions.map((planet, idx) => {
          const isHovered = hoveredPlanet === planet.body;
          const planetColors: Record<string, string> = {
            Sun: "#fbbf24",
            Moon: "#e5e7eb",
            Mercury: "#9ca3af",
            Venus: "#f472b6",
            Mars: "#ef4444",
            Jupiter: "#f59e0b",
            Saturn: "#8b5cf6",
            Uranus: "#06b6d4",
            Neptune: "#3b82f6",
            Pluto: "#6366f1"
          };
          const planetColor = planetColors[planet.body] || "#667eea";
          
          return (
            <g
              key={`planet-${planet.body}-${idx}`}
              onMouseEnter={() => setHoveredPlanet(planet.body)}
              onMouseLeave={() => setHoveredPlanet(null)}
              style={{ cursor: "pointer" }}
              filter={isHovered ? `url(#${planetGlowId})` : undefined}
            >
              <circle
                cx={planet.position.x}
                cy={planet.position.y}
                r={isHovered ? 20 : 16}
                fill={isHovered ? "#ffffff" : "#fffaf4"}
                stroke={planetColor}
                strokeWidth={isHovered ? "3" : "2"}
                style={{ transition: "all 0.3s ease" }}
              />
              <text
                x={planet.position.x}
                y={planet.position.y}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize={isHovered ? "20" : "18"}
                fill={planetColor}
                fontWeight="700"
                style={{ transition: "all 0.3s ease" }}
              >
                {planet.symbol}
              </text>
              <text
                x={planet.position.x}
                y={planet.position.y + 26}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="10"
                fill="#8b7355"
                fontWeight="600"
                opacity={isHovered ? 1 : 0.8}
              >
                {signRuName(planet.sign).substring(0, 3) || ""}
              </text>

              {isHovered && (
                <g>
                  <rect
                    x={planet.position.x - 60}
                    y={planet.position.y - 50}
                    width="120"
                    height="40"
                    fill="#0f172a"
                    fillOpacity="0.95"
                    rx="8"
                    filter={`url(#${shadowId})`}
                  />
                  <text
                    x={planet.position.x}
                    y={planet.position.y - 32}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize="12"
                    fill="#ffffff"
                    fontWeight="700"
                  >
                    {planetRuName(planet.body)}
                  </text>
                  <text
                    x={planet.position.x}
                    y={planet.position.y - 18}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize="10"
                    fill="#cbd5e1"
                  >
                    {signRuName(planet.sign)} • {planet.house || "?"} дом
                    {planet.degree !== undefined && ` • ${Math.floor(planet.degree)}°`}
                  </text>
                </g>
              )}
            </g>
          );
        })}

        <circle
          cx={center}
          cy={center}
          r="35"
          fill={`url(#${gradientId}-chart)`}
          stroke="#d4c5b0"
          strokeWidth="2.5"
        />
        <circle
          cx={center}
          cy={center}
          r="25"
          fill="#ffffff"
          stroke="#667eea"
          strokeWidth="2"
          opacity="0.9"
        />
        <text
          x={center}
          y={center}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="11"
          fill="#667eea"
          fontWeight="700"
        >
          TF
        </text>
      </svg>

      <div style={{ 
        marginTop: "var(--orbit-space-lg)", 
        padding: "var(--orbit-space-lg)", 
        background: "linear-gradient(135deg, #ffffff 0%, #faf9f7 100%)",
        borderRadius: "var(--orbit-radius-md)", 
        border: "1px solid #e5e0d8",
        boxShadow: "0 2px 8px rgba(0,0,0,0.04)"
      }}>
        <div style={{ display: "grid", gap: "0.85rem", marginBottom: "var(--orbit-space-lg)" }}>
          <div>
            <div style={{ 
              fontSize: "0.875rem", 
              fontWeight: 700, 
              marginBottom: "0.45rem", 
              color: "#0f172a",
              textTransform: "uppercase",
              letterSpacing: "0.05em"
            }}>
              Сетка аспектов
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem 0.85rem" }}>
              {[
                { label: "Соединение", color: "#4a90e2", dash: "none" },
                { label: "Трин", color: "#1f9d74", dash: "none" },
                { label: "Секстиль", color: "#4c87ff", dash: "4 4" },
                { label: "Квадрат", color: "#f08c2b", dash: "6 5" },
                { label: "Оппозиция", color: "#d9485f", dash: "8 5" },
              ].map((item) => {
                const count = aspectSummary.find((entry) => entry.label === item.label)?.count || 0;
                return (
                  <div key={item.label} style={{ display: "flex", alignItems: "center", gap: "0.45rem", color: "#5f4930", fontSize: "0.78rem", fontWeight: 600 }}>
                    <svg width="28" height="10" viewBox="0 0 28 10" aria-hidden="true">
                      <line x1="1" y1="5" x2="27" y2="5" stroke={item.color} strokeWidth="2.4" strokeDasharray={item.dash} strokeLinecap="round" />
                    </svg>
                    <span>{item.label}{count ? ` · ${count}` : ""}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
        <div style={{ 
          fontSize: "0.875rem", 
          fontWeight: 700, 
          marginBottom: "var(--orbit-space-md)", 
          color: "#0f172a",
          textTransform: "uppercase",
          letterSpacing: "0.05em"
        }}>
          Планеты в карте
        </div>
        <div style={{ 
          display: "grid", 
          gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", 
          gap: "var(--orbit-space-sm)",
        }}>
          {planetsWithPositions.map((planet) => {
            const planetColors: Record<string, string> = {
              Sun: "#fbbf24",
              Moon: "#e5e7eb",
              Mercury: "#9ca3af",
              Venus: "#f472b6",
              Mars: "#ef4444",
              Jupiter: "#f59e0b",
              Saturn: "#8b5cf6",
              Uranus: "#06b6d4",
              Neptune: "#3b82f6",
              Pluto: "#6366f1"
            };
            const planetColor = planetColors[planet.body] || "#667eea";
            
            return (
              <div 
                key={planet.body} 
                style={{ 
                  display: "flex", 
                  alignItems: "center", 
                  gap: "0.5rem",
                  padding: "0.5rem",
                  borderRadius: "6px",
                  background: "#faf9f7",
                  transition: "all 0.2s"
                }}
              >
                <span style={{ fontSize: "1.25rem", color: planetColor }}>{planet.symbol}</span>
                <div>
                  <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "#0f172a" }}>
                    {planetRuName(planet.body)}
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "#64748b" }}>
                    {signRuName(planet.sign)} • {planet.house} дом
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
