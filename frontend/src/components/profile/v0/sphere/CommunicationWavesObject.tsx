/** SVG: волны речи — объект «Коммуникация». */
export function CommunicationWavesObject({ size = 72 }: { size?: number }) {
  const s = size;
  const c = s / 2;
  return (
    <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`} aria-hidden>
      <circle cx={c} cy={c} r={34} fill="none" stroke="rgba(100, 130, 180, 0.18)" strokeWidth="1" />
      <path
        d={`M ${c - 24} ${c + 4} Q ${c - 12} ${c - 8} ${c} ${c + 4} T ${c + 24} ${c + 4}`}
        fill="none"
        stroke="rgba(80, 110, 160, 0.45)"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <path
        d={`M ${c - 18} ${c + 14} Q ${c - 6} ${c + 2} ${c + 6} ${c + 14} T ${c + 18} ${c + 14}`}
        fill="none"
        stroke="rgba(80, 110, 160, 0.28)"
        strokeWidth="1.2"
        strokeLinecap="round"
      />
    </svg>
  );
}
