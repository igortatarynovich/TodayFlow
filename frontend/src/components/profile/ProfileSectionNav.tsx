"use client";

import Link from "next/link";
import type { ProfileSectionId } from "@/components/profile/profileSections";
import { PROFILE_SECTION_IDS, PROFILE_SECTION_META } from "@/components/profile/profileSections";
import { profileSurfaceStyles } from "@/components/profile/ProfileSurface";
import { REWARD_RINGS_COPY } from "@/lib/rewardRings";

type ProfileSectionNavProps = {
  active: ProfileSectionId;
  onChange: (id: ProfileSectionId) => void;
};

export function ProfileSectionNav({ active, onChange }: ProfileSectionNavProps) {
  const c = REWARD_RINGS_COPY;
  return (
    <nav aria-label="Разделы профиля" className={profileSurfaceStyles.nav}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.5rem", flexWrap: "wrap" }}>
        <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49", letterSpacing: "0.06em", textTransform: "uppercase" }}>
          Разделы
        </p>
        <Link
          href="/help#profile-sections"
          style={{
            color: "#94a3b8",
            fontWeight: 600,
            fontSize: "0.85rem",
            textDecoration: "none",
            padding: "0.2rem 0.35rem",
          }}
          title={c.helpHubLinkLabel}
          aria-label={c.helpHubLinkLabel}
        >
          ?
        </Link>
      </div>
      <div
        style={{
          display: "flex",
          gap: "0.4rem",
          flexWrap: "wrap",
          alignItems: "stretch",
          marginTop: "0.5rem",
        }}
      >
        {PROFILE_SECTION_IDS.map((id) => {
          const isActive = active === id;
          const meta = PROFILE_SECTION_META[id];
          return (
            <button
              key={id}
              type="button"
              onClick={() => onChange(id)}
              title={meta.description}
              className={isActive ? "orbit-button orbit-button-primary orbit-button-sm" : "orbit-button orbit-button-secondary orbit-button-sm"}
              style={{
                borderRadius: "999px",
                fontWeight: 700,
                opacity: isActive ? 1 : 0.92,
              }}
            >
              {meta.label}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
