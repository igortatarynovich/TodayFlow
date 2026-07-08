"use client";

import Link from "next/link";
import { REWARD_RINGS_COPY } from "@/lib/rewardRings";

export type ProfilePageHeaderProps = {
  onOpenBirthData: () => void;
};

export function ProfilePageHeader({ onOpenBirthData }: ProfilePageHeaderProps) {
  const c = REWARD_RINGS_COPY;

  return (
    <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: "0.65rem 1rem" }}>
      <h1 className="orbit-display-sm" style={{ margin: 0, color: "#37281a" }}>
        {c.profilePageTitle}
      </h1>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "0.5rem" }}>
        <Link
          href="/help"
          className="orbit-button orbit-button-secondary orbit-button-sm"
          style={{ textDecoration: "none", minWidth: "2.25rem", padding: "0.35rem 0.55rem", justifyContent: "center" }}
          title={c.helpNavLabel}
          aria-label={c.helpNavLabel}
        >
          ?
        </Link>
        <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={onOpenBirthData}>
          {c.profileBirthDataButton}
        </button>
      </div>
    </div>
  );
}
