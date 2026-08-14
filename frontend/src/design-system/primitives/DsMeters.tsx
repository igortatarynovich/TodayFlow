import { useId } from "react";
import { joinClass } from "@/design-system/utils/joinClass";
import fk from "@/design-system/primitives/dsFormKit.module.css";

type DsRadialMeterProps = {
  /** 0–100 */
  value: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
  className?: string;
  testId?: string;
};

export function DsRadialMeter({
  value,
  size = 88,
  strokeWidth = 8,
  label,
  className,
  testId,
}: DsRadialMeterProps) {
  const clamped = Math.max(0, Math.min(100, value));
  const r = (size - strokeWidth) / 2;
  const c = 2 * Math.PI * r;
  const offset = c - (clamped / 100) * c;
  const text = label ?? `${Math.round(clamped)}%`;
  return (
    <div className={joinClass(fk.radialWrap, className)} style={{ width: size, height: size }} data-testid={testId}>
      <svg className={fk.radialSvg} width={size} height={size} aria-hidden>
        <circle
          className={fk.radialTrack}
          cx={size / 2}
          cy={size / 2}
          r={r}
          strokeWidth={strokeWidth}
        />
        <circle
          className={fk.radialValue}
          cx={size / 2}
          cy={size / 2}
          r={r}
          strokeWidth={strokeWidth}
          strokeDasharray={c}
          strokeDashoffset={offset}
        />
      </svg>
      <span className={fk.radialLabel}>{text}</span>
    </div>
  );
}

type DsDotMeterProps = {
  total?: number;
  value: number;
  className?: string;
  testId?: string;
};

export function DsDotMeter({ total = 5, value, className, testId }: DsDotMeterProps) {
  const on = Math.max(0, Math.min(total, Math.round(value)));
  return (
    <div className={joinClass(fk.dotMeter, className)} data-testid={testId} role="img" aria-label={`${on} of ${total}`}>
      {Array.from({ length: total }, (_, i) => (
        <span key={i} className={joinClass(fk.dot, i < on ? fk.dotOn : null)} />
      ))}
    </div>
  );
}

type DsSpectrumProps = {
  /** 0–1 */
  value: number;
  lowLabel?: string;
  highLabel?: string;
  className?: string;
  testId?: string;
};

export function DsSpectrum({
  value,
  lowLabel = "Low",
  highLabel = "High",
  className,
  testId,
}: DsSpectrumProps) {
  const pct = Math.max(0, Math.min(1, value)) * 100;
  return (
    <div className={joinClass(fk.spectrum, className)} data-testid={testId}>
      <div className={fk.spectrumTrack}>
        <span className={fk.spectrumThumb} style={{ left: `${pct}%` }} />
      </div>
      <div className={fk.spectrumLabels}>
        <span>{lowLabel}</span>
        <span>{highLabel}</span>
      </div>
    </div>
  );
}

type DsMetricProps = {
  value: string;
  label?: string;
  className?: string;
  testId?: string;
};

export function DsMetric({ value, label, className, testId }: DsMetricProps) {
  return (
    <div className={className} data-testid={testId}>
      <p className={fk.metricValue}>{value}</p>
      {label ? <p className={fk.metricLabel}>{label}</p> : null}
    </div>
  );
}

type DsLinearProgressProps = {
  /** 0–100 */
  value: number;
  className?: string;
  testId?: string;
  label?: string;
};

/** Linear progress track — fill width encodes value. */
export function DsLinearProgress({ value, className, testId, label }: DsLinearProgressProps) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div
      className={joinClass(fk.linearProgress, className)}
      data-testid={testId}
      role="progressbar"
      aria-valuenow={Math.round(clamped)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label}
    >
      <span className={fk.linearProgressFill} style={{ width: `${clamped}%` }} />
    </div>
  );
}

const WAVE_W = 120;
const WAVE_H = 36;
const WAVE_CYCLES = 2.5;

/**
 * Semantic wave meter: amplitude and filled width both encode `value` (0–100).
 * Not a decorative wave — geometry changes with the input.
 */
export function DsWaveMeter({
  value,
  className,
  testId,
  label,
  showLabel = false,
}: {
  value: number;
  className?: string;
  testId?: string;
  label?: string;
  showLabel?: boolean;
}) {
  const reactId = useId().replace(/:/g, "");
  const clamped = Math.max(0, Math.min(100, value));
  const t = clamped / 100;
  const amp = 2 + t * (WAVE_H * 0.38);
  const mid = WAVE_H / 2;
  const fillW = Math.max(0.5, (clamped / 100) * WAVE_W);

  const points: string[] = [];
  for (let x = 0; x <= WAVE_W; x += 2) {
    const y = mid - Math.sin((x / WAVE_W) * Math.PI * 2 * WAVE_CYCLES) * amp;
    points.push(`${x},${y.toFixed(2)}`);
  }
  const topPath = `M 0,${mid} L ${points.join(" L ")}`;
  const areaPath = `${topPath} L ${WAVE_W},${WAVE_H} L 0,${WAVE_H} Z`;
  const filledClipId = `ds-wave-fill-${reactId}`;

  return (
    <div
      className={joinClass(fk.waveMeter, className)}
      data-testid={testId}
      role="img"
      aria-label={label ?? `${Math.round(clamped)} percent`}
    >
      <svg
        className={fk.waveMeterSvg}
        viewBox={`0 0 ${WAVE_W} ${WAVE_H}`}
        preserveAspectRatio="none"
        aria-hidden
      >
        <defs>
          <clipPath id={filledClipId}>
            <rect x="0" y="0" width={fillW} height={WAVE_H} />
          </clipPath>
        </defs>
        <path className={fk.waveMeterTrack} d={areaPath} />
        <path className={fk.waveMeterValue} d={areaPath} clipPath={`url(#${filledClipId})`} />
        <path
          d={topPath}
          fill="none"
          stroke="var(--day-decor-color, var(--tf-accent-gold))"
          strokeWidth="1.5"
          strokeLinejoin="round"
          opacity={0.85}
        />
      </svg>
      {showLabel ? <p className={fk.waveMeterLabel}>{label ?? `${Math.round(clamped)}%`}</p> : null}
    </div>
  );
}
