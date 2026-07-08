/** SVG: пульс энергии — объект «Энергия». */
export function EnergyPulseObject({ size = 72 }: { size?: number }) {
  const s = size;
  const c = s / 2;
  return (
    <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`} aria-hidden>
      <circle cx={c} cy={c} r={34} fill="none" stroke="rgba(200, 160, 80, 0.2)" strokeWidth="1" />
      <path
        d={`M ${c - 26} ${c} L ${c - 10} ${c} L ${c - 4} ${c - 16} L ${c + 2} ${c + 16} L ${c + 8} ${c - 6} L ${c + 14} ${c} L ${c + 26} ${c}`}
        fill="none"
        stroke="rgba(180, 130, 50, 0.55)"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
