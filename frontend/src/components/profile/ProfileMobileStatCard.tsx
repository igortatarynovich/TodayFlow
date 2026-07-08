"use client";

import { profileSurfaceStyles } from "@/components/profile/ProfileSurface";

export function ProfileMobileStatCard({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className={profileSurfaceStyles.statCard}>
      <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
        {label}
      </p>
      <div>
        <p className="orbit-heading-3" style={{ margin: "0.25rem 0 0", color: "#1f2937" }}>
          {value}
        </p>
        {hint ? (
          <p className="orbit-body-xs" style={{ margin: "0.3rem 0 0", color: "#475569", lineHeight: 1.5 }}>
            {hint}
          </p>
        ) : null}
      </div>
    </div>
  );
}
