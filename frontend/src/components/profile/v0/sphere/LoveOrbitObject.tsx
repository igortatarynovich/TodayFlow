/** SVG: мягкие двойные орбиты — визуальный объект Love (не текст). */
export function LoveOrbitObject({ size = 96 }: { size?: number }) {
  const s = size;
  const c = s / 2;
  return (
    <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`} aria-hidden>
      <circle cx={c - 14} cy={c} r={28} fill="none" stroke="rgba(200, 130, 150, 0.35)" strokeWidth="1.5" />
      <circle cx={c + 14} cy={c} r={28} fill="none" stroke="rgba(200, 130, 150, 0.35)" strokeWidth="1.5" />
      <ellipse cx={c} cy={c} rx={18} ry={22} fill="rgba(240, 190, 200, 0.25)" />
      <circle cx={c} cy={c} r={6} fill="rgba(180, 100, 120, 0.45)" />
    </svg>
  );
}
