"use client";

import Link from "next/link";

interface PatternObservation {
  axis_id: string;
  name: string;
  count: number; // Сколько раз активировался
}

interface DomainObservation {
  domain: string;
  count: number; // Сколько раз упоминался
}

interface ObservationHistoryProps {
  patternObservations?: PatternObservation[];
  domainObservations?: DomainObservation[];
  isGuest?: boolean;
}

/**
 * Микро-история наблюдений
 * Показывает, сколько раз паттерны и сферы активировались
 * Даёт ощущение накопления смысла
 */
export function ObservationHistory({ 
  patternObservations = [], 
  domainObservations = [],
  isGuest = false 
}: ObservationHistoryProps) {
  if (isGuest) {
    return null;
  }

  // Фильтруем только те, что активировались больше 1 раза
  const activePatterns = patternObservations.filter(p => p.count > 1);
  const activeDomains = domainObservations.filter(d => d.count > 1);

  if (activePatterns.length === 0 && activeDomains.length === 0) {
    return null;
  }

  return (
    <div
      className="orbit-card"
      style={{
        padding: "var(--orbit-space-lg)",
        background: "#faf9f7",
        border: "1px solid #e5e0d8",
        borderRadius: "var(--orbit-radius-md)",
        marginBottom: "var(--orbit-space-xl)"
      }}
    >
      <h3 className="orbit-display-xs" style={{
        marginBottom: "var(--orbit-space-md)",
        color: "#0f172a",
        fontWeight: 500
      }}>
        История наблюдений
      </h3>

      {activePatterns.length > 0 && (
        <div style={{ marginBottom: activeDomains.length > 0 ? "var(--orbit-space-md)" : 0 }}>
          {activePatterns.map((pattern) => (
            <div
              key={pattern.axis_id}
              style={{
                marginBottom: "var(--orbit-space-sm)",
                padding: "var(--orbit-space-sm)",
                background: "#ffffff",
                borderRadius: "var(--orbit-radius-sm)",
                border: "1px solid #e5e0d8"
              }}
            >
              <p className="orbit-body-sm" style={{
                color: "#334155",
                lineHeight: 1.5
              }}>
                Паттерн <strong>{pattern.name}</strong> активировался{" "}
                <strong>{pattern.count}</strong>{" "}
                {pattern.count === 1 ? "раз" : pattern.count < 5 ? "раза" : "раз"} за эту неделю
              </p>
              <Link
                href={`/discover/pattern/${pattern.axis_id}`}
                className="orbit-body-xs orbit-link"
                style={{
                  color: "#b87333",
                  textDecoration: "none",
                  fontWeight: 500
                }}
              >
                → Посмотреть в карте
              </Link>
            </div>
          ))}
        </div>
      )}

      {activeDomains.length > 0 && (
        <div>
          {activeDomains.map((domain) => (
            <div
              key={domain.domain}
              style={{
                marginBottom: "var(--orbit-space-sm)",
                padding: "var(--orbit-space-sm)",
                background: "#ffffff",
                borderRadius: "var(--orbit-radius-sm)",
                border: "1px solid #e5e0d8"
              }}
            >
              <p className="orbit-body-sm" style={{
                color: "#334155",
                lineHeight: 1.5
              }}>
                {domain.count} {domain.count === 1 ? "раз" : domain.count < 5 ? "раза" : "раз"} за неделю ты сталкивался с темой <strong>{domain.domain}</strong>
              </p>
              <Link
                href={`/discover#${domain.domain.toLowerCase().replace(/\s+/g, "-")}`}
                className="orbit-body-xs orbit-link"
                style={{
                  color: "#b87333",
                  textDecoration: "none",
                  fontWeight: 500
                }}
              >
                → Как это устроено у тебя
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

