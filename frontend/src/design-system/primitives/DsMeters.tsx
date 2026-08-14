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
