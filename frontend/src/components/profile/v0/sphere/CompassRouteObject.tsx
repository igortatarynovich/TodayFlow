/** Compass route — визуальный объект «Как двигаться» (маршрут, не иконка). */
export function CompassRouteObject({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 240 240" fill="none" aria-hidden>
      <path
        d="M 36 172 Q 88 52 204 128"
        stroke="rgba(91, 110, 70, 0.22)"
        strokeWidth="1.5"
        strokeDasharray="4 6"
      />
      <path
        d="M 48 158 Q 112 72 188 138"
        stroke="rgba(91, 110, 70, 0.55)"
        strokeWidth="2.25"
        strokeLinecap="round"
      />
      <path
        d="M 178 132 L 196 138 L 184 148"
        stroke="rgba(91, 110, 70, 0.65)"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      <circle cx="52" cy="152" r="7" fill="#fffefb" stroke="rgba(120, 140, 90, 0.45)" strokeWidth="2" />
      <circle cx="52" cy="152" r="2.5" fill="rgba(120, 140, 90, 0.55)" />

      <circle cx="118" cy="88" r="7" fill="#fffefb" stroke="rgba(120, 140, 90, 0.55)" strokeWidth="2" />
      <circle cx="118" cy="88" r="2.5" fill="rgba(120, 140, 90, 0.65)" />

      <circle cx="184" cy="136" r="9" fill="rgba(120, 140, 90, 0.18)" stroke="rgba(91, 110, 70, 0.7)" strokeWidth="2.5" />
      <circle cx="184" cy="136" r="3.5" fill="rgba(91, 110, 70, 0.75)" />

      <g transform="translate(52 52)">
        <circle cx="68" cy="68" r="34" stroke="rgba(107, 83, 68, 0.18)" strokeWidth="1.25" />
        <path d="M 68 44 L 72 60 L 68 56 L 64 60 Z" fill="rgba(91, 110, 70, 0.55)" />
        <line x1="68" y1="56" x2="68" y2="92" stroke="rgba(107, 83, 68, 0.25)" strokeWidth="1" />
        <line x1="44" y1="68" x2="92" y2="68" stroke="rgba(107, 83, 68, 0.25)" strokeWidth="1" />
        <text
          x="68"
          y="38"
          textAnchor="middle"
          fill="rgba(107, 83, 68, 0.45)"
          fontSize="9"
          fontWeight="700"
          letterSpacing="0.08em"
        >
          N
        </text>
      </g>
    </svg>
  );
}
