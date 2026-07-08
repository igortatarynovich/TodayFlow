/** SVG: структурный ромб + направление — визуальный объект Money (не текст). */
export function MoneyStructureObject({ size = 96 }: { size?: number }) {
  const s = size;
  const c = s / 2;
  return (
    <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`} aria-hidden>
      <path
        d={`M ${c} 12 L ${s - 16} ${c} L ${c} ${s - 12} L 16 ${c} Z`}
        fill="none"
        stroke="rgba(107, 83, 68, 0.35)"
        strokeWidth="1.5"
      />
      <path
        d={`M ${c} 28 L ${c} ${s - 28}`}
        stroke="rgba(107, 83, 68, 0.5)"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d={`M ${c - 12} ${c - 8} L ${c} ${c - 22} L ${c + 12} ${c - 8}`}
        fill="none"
        stroke="rgba(143, 107, 58, 0.65)"
        strokeWidth="2"
        strokeLinejoin="round"
      />
    </svg>
  );
}
