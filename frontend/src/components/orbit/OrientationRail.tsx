import { type ReactNode } from "react";

type OrientationRailProps = {
  sectionLabel: string;
  metaLabel?: string;
  stepLabel?: string;
  statusLabel?: string;
  mantra?: string; // e.g. "Pause · Sense · Integrate"
  action?: ReactNode;
  className?: string;
};

export function OrientationRail({ 
  sectionLabel, 
  metaLabel, 
  stepLabel, 
  statusLabel, 
  mantra,
  action,
  className 
}: OrientationRailProps) {
  return (
    <div className={`orbit-rail ${className || ""}`}>
      <div className="orbit-rail__info">
        <span className="orbit-rail__section">{sectionLabel}</span>
        {metaLabel && <span className="orbit-rail__meta">{metaLabel}</span>}
        {statusLabel && <span className="orbit-rail__status">{statusLabel}</span>}
      </div>
      <div className="orbit-rail__actions">
        {stepLabel && <span className="orbit-rail__step">{stepLabel}</span>}
        {mantra && <span className="orbit-rail__mantra">{mantra}</span>}
        {action}
      </div>
    </div>
  );
}
