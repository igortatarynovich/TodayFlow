"use client";

import { useMemo, useState, useCallback } from "react";

interface BirthChartVisualizationProps {
  houses?: Record<string, any>;
  chartPositions?: Array<{
    body: string;
    sign: string;
    house?: number;
    degree?: number;
  }>;
  className?: string;
}

/**
 * Компонент для визуализации астрологической карты рождения.
 * Отображает 12 домов, планеты в знаках и домах.
 */
export function BirthChartVisualization({
  houses = {},
  chartPositions = [],
  className = "",
}: BirthChartVisualizationProps) {
  const size = 400; // Размер SVG
  const center = size / 2;
  const outerRadius = size / 2 - 20;
  const innerRadius = outerRadius * 0.65;
  const houseRadius = outerRadius * 0.85;

  // Планетные символы (мемоизированы, чтобы не пересоздавались на каждом рендере)
  const planetSymbols = useMemo<Record<string, string>>(() => ({
    Sun: "☉",
    Moon: "☽",
    Mercury: "☿",
    Venus: "♀",
    Mars: "♂",
    Jupiter: "♃",
    Saturn: "♄",
    Uranus: "♅",
    Neptune: "♆",
    Pluto: "♇",
    Ascendant: "ASC",
    Midheaven: "MC",
  }), []);

  // Знаки зодиака
  const zodiacSigns = [
    "Овен", "Телец", "Близнецы", "Рак",
    "Лев", "Дева", "Весы", "Скорпион",
    "Стрелец", "Козерог", "Водолей", "Рыбы"
  ];

  const zodiacAbbr = [
    "♈", "♉", "♊", "♋",
    "♌", "♍", "♎", "♏",
    "♐", "♑", "♒", "♓"
  ];

  const [hoveredPlanet, setHoveredPlanet] = useState<string | null>(null);
  const [hoveredHouse, setHoveredHouse] = useState<number | null>(null);

  // Создаем данные о всех планетах (не только в домах)
  const allPlanets = useMemo(() => {
    return chartPositions.map((p) => ({
      ...p,
      symbol: planetSymbols[p.body] || p.body,
    }));
  }, [chartPositions, planetSymbols]);

  // Планеты в домах для отображения на карте
  const planetsInHouses = useMemo(() => {
    return chartPositions
      .filter((p) => p.house !== undefined && p.house !== null)
      .map((p) => ({
        ...p,
        symbol: planetSymbols[p.body] || p.body,
      }));
  }, [chartPositions, planetSymbols]);

  // Получаем знак дома из данных houses
  const getHouseSign = (houseNumber: number): string | null => {
    const houseKey = `house_${houseNumber}`;
    const houseData = houses[houseKey];
    if (typeof houseData === 'object' && houseData?.sign) {
      return houseData.sign;
    }
    return null;
  };

  // Функция для расчета позиции на круге
  const getPositionOnCircle = useCallback((angle: number, radius: number) => {
    const rad = (angle - 90) * (Math.PI / 180); // -90 чтобы начать сверху
    return {
      x: center + radius * Math.cos(rad),
      y: center + radius * Math.sin(rad),
    };
  }, [center]);

  // Создаем сегменты для 12 домов
  const houseSegments = useMemo(() => {
    const segments = [];
    const anglePerHouse = 360 / 12;

    // Предполагаем, что ASC находится в начале первого дома (обычно это 0 градусов)
    // В реальной карте это может быть по-другому, но для базовой визуализации достаточно
    const ascendantAngle = 0; // Можно вычислить из данных, если доступно

    for (let i = 0; i < 12; i++) {
      const startAngle = ascendantAngle + i * anglePerHouse;
      const endAngle = startAngle + anglePerHouse;
      const midAngle = startAngle + anglePerHouse / 2;

      segments.push({
        houseNumber: i + 1,
        startAngle,
        endAngle,
        midAngle,
        ...getPositionOnCircle(midAngle, houseRadius),
      });
    }

    return segments;
  }, [houseRadius, getPositionOnCircle]);

  // Если нет данных о позициях планет, показываем сообщение
  if (!chartPositions || chartPositions.length === 0) {
    return (
      <div className={`birth-chart-visualization ${className}`} style={{ width: "100%", maxWidth: size, margin: "0 auto", textAlign: "center", padding: "var(--orbit-space-xl)" }}>
        <p className="orbit-body-sm orbit-text-muted" style={{ lineHeight: 1.6 }}>
          Для отображения карты рождения нужны данные о позициях планет.
          {!chartPositions && " Данные пока не загружены."}
        </p>
      </div>
    );
  }

  return (
    <div className={`birth-chart-visualization ${className}`} style={{ width: "100%", maxWidth: size, margin: "0 auto" }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ overflow: "visible" }}>
        {/* Внешний круг (граница карты) */}
        <circle
          cx={center}
          cy={center}
          r={outerRadius}
          fill="none"
          stroke="#e5e0d8"
          strokeWidth="2"
        />

        {/* Внутренний круг (граница домов) */}
        <circle
          cx={center}
          cy={center}
          r={innerRadius}
          fill="none"
          stroke="#e5e0d8"
          strokeWidth="1"
        />

        {/* Линии домов (куспиды) */}
        {houseSegments.map((segment, index) => {
          const houseSign = getHouseSign(segment.houseNumber);
          const isHovered = hoveredHouse === segment.houseNumber;
          
          return (
            <g 
              key={`house-${segment.houseNumber}`}
              onMouseEnter={() => setHoveredHouse(segment.houseNumber)}
              onMouseLeave={() => setHoveredHouse(null)}
              style={{ cursor: "pointer" }}
            >
              {/* Линия куспида */}
              <line
                x1={center}
                y1={center}
                x2={getPositionOnCircle(segment.startAngle, outerRadius).x}
                y2={getPositionOnCircle(segment.startAngle, outerRadius).y}
                stroke={isHovered ? "#b87333" : "#d4c5b0"}
                strokeWidth={isHovered ? "2" : "1"}
              />
              {/* Номер дома */}
              <text
                x={segment.x}
                y={segment.y}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="14"
                fill={isHovered ? "#b87333" : "#6b5b4d"}
                fontWeight="600"
                style={{ userSelect: "none" }}
              >
                {segment.houseNumber}
              </text>
              {/* Знак дома (если есть) */}
              {houseSign && (
                <text
                  x={segment.x}
                  y={segment.y + 15}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fontSize="10"
                  fill="#8b7355"
                  style={{ userSelect: "none" }}
                >
                  {houseSign.substring(0, 3)}
                </text>
              )}
              {/* Tooltip для дома */}
              {isHovered && (
                <g>
                  <rect
                    x={segment.x - 40}
                    y={segment.y - 30}
                    width="80"
                    height="20"
                    fill="#0f172a"
                    fillOpacity="0.9"
                    rx="4"
                  />
                  <text
                    x={segment.x}
                    y={segment.y - 15}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize="10"
                    fill="#ffffff"
                  >
                    {segment.houseNumber} дом{houseSign ? ` (${houseSign})` : ""}
                  </text>
                </g>
              )}
            </g>
          );
        })}

        {/* Планеты в домах */}
        {planetsInHouses.map((planet, index) => {
          const segment = houseSegments[planet.house! - 1];
          if (!segment) return null;

          // Размещаем планеты на кольце между innerRadius и outerRadius
          const planetRadius = (innerRadius + outerRadius) / 2;
          const planetAngle = segment.midAngle;
          const position = getPositionOnCircle(planetAngle, planetRadius);
          const isHovered = hoveredPlanet === planet.body;

          return (
            <g 
              key={`planet-${planet.body}-${index}`}
              onMouseEnter={() => setHoveredPlanet(planet.body)}
              onMouseLeave={() => setHoveredPlanet(null)}
              style={{ cursor: "pointer" }}
            >
              {/* Круг вокруг планеты */}
              <circle
                cx={position.x}
                cy={position.y}
                r={isHovered ? "18" : "14"}
                fill={isHovered ? "#fefcf9" : "#ffffff"}
                stroke={isHovered ? "#b87333" : "#b87333"}
                strokeWidth={isHovered ? "2.5" : "1.5"}
                style={{ transition: "all 0.2s ease" }}
              />
              {/* Символ планеты */}
              <text
                x={position.x}
                y={position.y}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize={isHovered ? "18" : "16"}
                fill={isHovered ? "#b87333" : "#6b5b4d"}
                fontWeight="600"
                style={{ userSelect: "none" }}
              >
                {planet.symbol}
              </text>
              {/* Подпись (знак зодиака) */}
              <text
                x={position.x}
                y={position.y + 20}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="10"
                fill="#8b7355"
                style={{ userSelect: "none" }}
              >
                {planet.sign?.substring(0, 3)}
              </text>
              {/* Tooltip для планеты */}
              {isHovered && (
                <g>
                  <rect
                    x={position.x - 50}
                    y={position.y - 40}
                    width="100"
                    height="30"
                    fill="#0f172a"
                    fillOpacity="0.9"
                    rx="4"
                  />
                  <text
                    x={position.x}
                    y={position.y - 25}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize="10"
                    fill="#ffffff"
                    fontWeight="600"
                  >
                    {planet.body}
                  </text>
                  <text
                    x={position.x}
                    y={position.y - 12}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize="9"
                    fill="#e5e0d8"
                  >
                    {planet.sign} • {planet.house} дом
                  </text>
                </g>
              )}
            </g>
          );
        })}

        {/* Центральный круг */}
        <circle
          cx={center}
          cy={center}
          r="30"
          fill="#ffffff"
          stroke="#d4c5b0"
          strokeWidth="2"
        />
        <text
          x={center}
          y={center}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="12"
          fill="#6b5b4d"
          fontWeight="600"
          style={{ userSelect: "none" }}
        >
          Земля
        </text>
      </svg>

      {/* Легенда - все планеты */}
      {allPlanets.length > 0 && (
        <div style={{ marginTop: "var(--orbit-space-md)", padding: "var(--orbit-space-md)", background: "#fefcf9", borderRadius: "var(--orbit-radius-sm)", border: "1px solid #e5e0d8" }}>
          <h4 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-sm)", fontSize: "0.875rem", color: "#0f172a" }}>
            Планеты в карте
          </h4>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "var(--orbit-space-sm)", fontSize: "0.75rem" }}>
            {allPlanets.map((planet) => (
              <div 
                key={planet.body} 
                style={{ 
                  display: "flex", 
                  alignItems: "center", 
                  gap: "var(--orbit-space-xs)",
                  padding: "var(--orbit-space-xs)",
                  borderRadius: "var(--orbit-radius-sm)",
                  background: hoveredPlanet === planet.body ? "#f5f5f0" : "transparent",
                  transition: "background 0.2s ease",
                  cursor: "pointer",
                }}
                onMouseEnter={() => setHoveredPlanet(planet.body)}
                onMouseLeave={() => setHoveredPlanet(null)}
              >
                <span style={{ fontSize: "1.2rem", minWidth: "20px", textAlign: "center" }}>{planet.symbol}</span>
                <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                  <span style={{ color: "#0f172a", fontWeight: 500 }}>
                    {planet.body === "Ascendant" ? "Асцендент" : planet.body === "Midheaven" ? "МС" : planet.body}
                  </span>
                  <span style={{ color: "#6b5b4d", fontSize: "0.7rem" }}>
                    {planet.sign}{planet.house ? ` • ${planet.house} дом` : ""}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

