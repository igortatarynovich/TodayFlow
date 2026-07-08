/** SVG: стрела пути — визуальный объект «Как двигаться». */
export function MovementPathObject({ size = 96 }: { size?: number }) {
  const s = size;
  const c = s / 2;
  return (
    <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`} aria-hidden>
      <circle cx={c} cy={c} r={38} fill="none" stroke="rgba(120, 140, 90, 0.2)" strokeWidth="1" />
      <circle cx={c} cy={c} r={26} fill="none" stroke="rgba(120, 140, 90, 0.28)" strokeWidth="1" />
      <path
        d={`M ${c - 22} ${c + 8} Q ${c} ${c - 18} ${c + 22} ${c + 8}`}
        fill="none"
        stroke="rgba(91, 110, 70, 0.45)"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <path
        d={`M ${c + 14} ${c + 2} L ${c + 24} ${c + 8} L ${c + 14} ${c + 14}`}
        fill="none"
        stroke="rgba(91, 110, 70, 0.55)"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx={c - 18} cy={c + 10} r={4} fill="rgba(120, 140, 90, 0.35)" />
      <circle cx={c} cy={c - 4} r={4} fill="rgba(120, 140, 90, 0.5)" />
    </svg>
  );
}
