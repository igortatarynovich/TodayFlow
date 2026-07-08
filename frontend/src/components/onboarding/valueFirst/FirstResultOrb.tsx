"use client";

type Props = {
  element?: string | null;
  className?: string;
};

/** Decorative abstract ring — not interactive chart data. */
export function FirstResultOrb({ element, className }: Props) {
  const accent =
    element === "Огонь"
      ? "#c97a52"
      : element === "Земля"
        ? "#8a9a6e"
        : element === "Воздух"
          ? "#7ba3c9"
          : element === "Вода"
            ? "#6e94b8"
            : "#c9a873";

  return (
    <div className={className} aria-hidden data-testid="first-result-orb">
      <svg viewBox="0 0 220 220" role="presentation">
        <defs>
          <radialGradient id="orbGlow" cx="50%" cy="45%" r="55%">
            <stop offset="0%" stopColor={accent} stopOpacity="0.18" />
            <stop offset="100%" stopColor={accent} stopOpacity="0" />
          </radialGradient>
        </defs>
        <circle cx="110" cy="110" r="98" fill="url(#orbGlow)" />
        <circle cx="110" cy="110" r="88" fill="none" stroke={accent} strokeOpacity="0.22" strokeWidth="1" />
        <circle cx="110" cy="110" r="68" fill="none" stroke={accent} strokeOpacity="0.35" strokeWidth="1.2" />
        <circle cx="110" cy="110" r="48" fill="none" stroke={accent} strokeOpacity="0.5" strokeWidth="1.4" />
        <ellipse cx="110" cy="110" rx="88" ry="34" fill="none" stroke={accent} strokeOpacity="0.16" strokeWidth="1" transform="rotate(24 110 110)" />
        <ellipse cx="110" cy="110" rx="88" ry="34" fill="none" stroke={accent} strokeOpacity="0.12" strokeWidth="1" transform="rotate(-32 110 110)" />
        {[0, 60, 120, 180, 240, 300].map((deg) => {
          const rad = (deg * Math.PI) / 180;
          const x = 110 + Math.cos(rad) * 68;
          const y = 110 + Math.sin(rad) * 68;
          return <circle key={deg} cx={x} cy={y} r="3.5" fill={accent} fillOpacity="0.55" />;
        })}
        <circle cx="110" cy="110" r="6" fill={accent} fillOpacity="0.75" />
      </svg>
    </div>
  );
}
