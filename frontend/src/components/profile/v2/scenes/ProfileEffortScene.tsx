"use client";

import { useState } from "react";
import {
  profileMotionStaggerDelay,
  profileMotionStyles,
  useProfileMotionInView,
} from "@/components/foundation/ProfileMotion";
import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import { ProfileAtmosphere } from "@/components/profile/v2/ProfileAtmosphere";
import { PROFILE_V2_COPY, PROFILE_V2_DEPTH_NAV } from "@/components/profile/v2/profileV2SystemCopy";
import styles from "@/components/profile/v2/profileV2System.module.css";
import { ElementIcon } from "@/components/visualIdentity/ElementIcon";
import { PlanetIcon } from "@/components/visualIdentity/PlanetIcon";
import type { ElementSlug, PlanetSlug } from "@/lib/visualIdentity/registry";

export type ProfileEffortSceneProps = {
  effortVector: string;
  lifeSpheres?: ProfileLifeSphere[];
};

/** Swipe rail upper bound — density via snap, not a hard 2-card Forms hack. */
const MAX_ACT4_SPHERES = 8;

const effortNav = PROFILE_V2_DEPTH_NAV.find((s) => s.id === "effort") ?? PROFILE_V2_DEPTH_NAV[3];

type SphereMotif =
  | { kind: "planet"; slug: PlanetSlug }
  | { kind: "element"; slug: ElementSlug };

const SPHERE_MOTIF: Record<string, SphereMotif> = {
  love: { kind: "planet", slug: "venus" },
  sex: { kind: "planet", slug: "mars" },
  money: { kind: "planet", slug: "jupiter" },
  work: { kind: "planet", slug: "saturn" },
  career: { kind: "planet", slug: "sun" },
  family: { kind: "planet", slug: "moon" },
  kids: { kind: "element", slug: "water" },
  body: { kind: "element", slug: "earth" },
  friends: { kind: "planet", slug: "mercury" },
  decisions: { kind: "planet", slug: "saturn" },
  mission: { kind: "planet", slug: "sun" },
  growth: { kind: "element", slug: "fire" },
};

function SphereMotifGlyph({ sphereId }: { sphereId: string }) {
  const motif = SPHERE_MOTIF[sphereId] ?? { kind: "element" as const, slug: "air" as ElementSlug };
  if (motif.kind === "planet") {
    return <PlanetIcon planet={motif.slug} size={22} stroke="currentColor" />;
  }
  return <ElementIcon element={motif.slug} size={22} stroke="currentColor" />;
}

function SphereSwipeCard({
  sphere,
  index,
  open,
  onToggle,
}: {
  sphere: ProfileLifeSphere;
  index: number;
  open: boolean;
  onToggle: () => void;
}) {
  const copy = PROFILE_V2_COPY.zones.effort;
  const teaser = sphere.need?.trim() || sphere.how?.trim() || "";
  const how = sphere.how?.trim() || "";
  const need = sphere.need?.trim() || "";
  const risk = sphere.risk?.trim() || "";
  const turnsOn = sphere.turnsOn?.trim() || "";
  const helps = sphere.helps?.trim() || "";
  const tips = sphere.practicalTips?.filter((t) => t?.trim()) ?? [];
  const hasDetail = Boolean(how || need || risk || turnsOn || helps || tips.length);

  return (
    <li
      className={[
        styles.effortSphereSnapCard,
        profileMotionStyles.staggerItem,
        open ? styles.effortSphereSnapCardExpanded : "",
      ]
        .filter(Boolean)
        .join(" ")}
      style={profileMotionStaggerDelay(index, 70)}
      data-testid={`profile-v2-effort-sphere-${sphere.id}`}
      data-expanded={open ? "true" : "false"}
    >
      <button
        type="button"
        className={styles.effortSphereSnapHit}
        onClick={onToggle}
        aria-expanded={open}
        data-testid={`profile-v2-effort-sphere-toggle-${sphere.id}`}
        disabled={!hasDetail}
      >
        <p className={styles.effortSphereTitle}>
          <span className={styles.effortSphereMotif} aria-hidden>
            <SphereMotifGlyph sphereId={sphere.id} />
          </span>
          <span className={styles.effortSphereTitleText}>{sphere.title}</span>
          <span
            className={styles.effortSphereDot}
            style={sphere.accent ? { background: sphere.accent } : undefined}
            aria-hidden
          />
        </p>

        {!open && teaser ? <p className={styles.effortSphereTeaser}>{teaser}</p> : null}

        {open ? (
          <div
            className={styles.effortSphereDetail}
            data-testid={`profile-v2-effort-sphere-detail-${sphere.id}`}
          >
            {how ? (
              <p className={styles.effortSphereHow}>
                <span className={styles.effortSphereMetaLabel}>{copy.sphereHow}</span>
                {how}
              </p>
            ) : null}
            {need ? (
              <p className={styles.effortSphereNeedFull}>
                <span className={styles.effortSphereMetaLabel}>{copy.sphereNeed}</span>
                {need}
              </p>
            ) : null}
            {risk ? (
              <p className={styles.effortSphereRisk}>
                <span className={styles.effortSphereMetaLabel}>{copy.sphereRisk}</span>
                {risk}
              </p>
            ) : null}
            {turnsOn ? (
              <p className={styles.effortSphereNeedFull}>
                <span className={styles.effortSphereMetaLabel}>{copy.sphereTurnsOn}</span>
                {turnsOn}
              </p>
            ) : null}
            {helps ? (
              <p className={styles.effortSphereNeedFull}>
                <span className={styles.effortSphereMetaLabel}>{copy.sphereHelps}</span>
                {helps}
              </p>
            ) : null}
            {tips.length ? (
              <div className={styles.effortSphereTips}>
                <p className={styles.effortSphereMetaLabel}>Практические шаги</p>
                <ul className={styles.effortSphereTipsList}>
                  {tips.map((tip) => (
                    <li key={tip}>{tip}</li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        ) : hasDetail ? (
          <p className={styles.effortSphereExpandHint}>{copy.sphereExpandHint}</p>
        ) : null}
      </button>
    </li>
  );
}

/**
 * Visual Modes #4 — Act 4 direction: one vector + optional where-spheres.
 * Forms Шаг 4: effort_vector + swipe cards (tap to expand).
 */
export function ProfileEffortScene({ effortVector, lifeSpheres = [] }: ProfileEffortSceneProps) {
  const spheres = lifeSpheres
    .filter((s) => s.title?.trim() && (s.need?.trim() || s.how?.trim() || s.risk?.trim()))
    .slice(0, MAX_ACT4_SPHERES);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const motion = useProfileMotionInView<HTMLElement>(80);
  const copy = PROFILE_V2_COPY.zones.effort;

  return (
    <section
      id="profile-v2-effort"
      ref={motion.ref}
      className={`${styles.journeyScene} ${styles.journeySceneModeEffort} ${motion.className}`}
      style={motion.style}
      aria-labelledby="profile-v2-effort-title"
      data-testid="profile-v2-effort"
      data-visual-mode="effort-direction"
    >
      <ProfileAtmosphere motif="effort" />
      <header className={styles.zoneHeader}>
        <div>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>{effortNav.step.replace(/^0/, "")}</span>
            <span id="profile-v2-effort-title">{copy.title}</span>
          </p>
          {copy.lead ? <p className={styles.zoneLead}>{copy.lead}</p> : null}
        </div>
      </header>

      <div className={styles.effortLayout}>
        <div className={styles.effortFocus}>
          {copy.focusLabel ? <p className={styles.effortFocusLabel}>{copy.focusLabel}</p> : null}
          <div className={styles.effortFocusCard} data-testid="profile-v2-effort-direction">
            <span className={styles.effortDirectionMark} aria-hidden>
              <svg width="36" height="20" viewBox="0 0 36 20" fill="none">
                <path
                  d="M1 10h28M22 3l10 7-10 7"
                  stroke="currentColor"
                  strokeWidth="1.75"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </span>
            <p className={styles.effortVector} data-testid="profile-v2-effort-vector">
              {effortVector}
            </p>
          </div>
        </div>

        {spheres.length ? (
          <div className={styles.effortSpheres} data-testid="profile-v2-effort-spheres">
            <p className={styles.effortSpheresLabel}>{copy.spheresLabel}</p>
            <ul className={styles.effortSphereRail} data-testid="profile-v2-effort-sphere-rail">
              {spheres.map((sphere, index) => (
                <SphereSwipeCard
                  key={sphere.id}
                  sphere={sphere}
                  index={index}
                  open={expandedId === sphere.id}
                  onToggle={() =>
                    setExpandedId((prev) => (prev === sphere.id ? null : sphere.id))
                  }
                />
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </section>
  );
}
