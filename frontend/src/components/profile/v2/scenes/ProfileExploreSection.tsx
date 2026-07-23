"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { NatalChartWheel } from "@/components/natal-chart/NatalChartWheel";
import { ProfileMotionExpand, useProfileMotionInView } from "@/components/foundation/ProfileMotion";
import { ProfileChartSection } from "@/components/profile/ProfileChartSection";
import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";
import type { ProfileQuickMapDeepProps } from "@/components/profile/quickMap/ProfileQuickMapScreen";
import { ProfileAtmosphere } from "@/components/profile/v2/ProfileAtmosphere";
import { PROFILE_V2_COPY } from "@/components/profile/v2/profileV2SystemCopy";
import type { ProgressiveDetailItem } from "@/lib/profilePage/buildProfileProgressiveDetailsProjection";
import { profileV2SphereCardLine } from "@/lib/profilePage/profileV2SpherePresentation";
import type { ProfileQuickMapViewModel } from "@/lib/profilePage/buildProfileQuickMapData";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileExploreSectionProps = {
  open: boolean;
  onToggle: () => void;
  progressiveDetails: ProgressiveDetailItem[];
  model: ProfileQuickMapViewModel;
  lifeSpheres?: ProfileLifeSphere[];
  deep?: ProfileQuickMapDeepProps | null;
  deepExpanded?: boolean;
  /** Optional character kitchen leftover (not used in insight). */
  characterSlot?: ReactNode;
};

function natalWheelProps(preview: NatalChartPreview) {
  return {
    chartPositions: Object.entries(preview.positions || {}).map(([planet, data]) => ({
      body: planet,
      sign: data.sign || "",
      house: data.house,
      degree: data.degree,
      longitude: data.longitude || data.degree || 0,
    })),
    houses: (preview.houses || []).reduce(
      (acc, house) => {
        acc[`house_${house.house}`] = {
          sign: house.sign,
          degree: house.degree,
          cusp_longitude: house.cusp_longitude,
        };
        return acc;
      },
      {} as Record<string, { sign?: string; degree?: number; cusp_longitude?: number }>,
    ),
    ascendant: preview.ascendant?.longitude || preview.ascendant?.degree || 0,
    aspects: preview.aspects?.callouts ?? [],
  };
}

/**
 * Step 6 — natal destination at the bottom of Profile.
 * Always visible; deep chart/details open on demand (reference IA).
 */
export function ProfileExploreSection({
  open,
  onToggle,
  progressiveDetails,
  model,
  lifeSpheres,
  deep,
  deepExpanded = false,
  characterSlot,
}: ProfileExploreSectionProps) {
  const hasNatal = Boolean(deep);
  const hasDetails =
    progressiveDetails.length > 0 ||
    Boolean(characterSlot) ||
    Boolean(lifeSpheres?.length) ||
    Boolean(model.lifeMission);
  const motion = useProfileMotionInView<HTMLElement>(60);
  if (!hasNatal && !hasDetails) return null;

  const natalPreview = deep?.natalPreview ?? null;
  const hasWheel = Boolean(natalPreview && Object.keys(natalPreview.positions || {}).length);
  const copy = PROFILE_V2_COPY.zones.explore;

  return (
    <section
      id="profile-v2-explore"
      ref={motion.ref}
      className={`${styles.zone} ${styles.journeyScene} ${styles.exploreScene} ${motion.className}`.trim()}
      style={motion.style}
      data-testid="profile-v2-explore"
      aria-labelledby="profile-v2-explore-title"
    >
      <ProfileAtmosphere motif="natal" />

      <header className={styles.zoneHeader}>
        <div>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>{copy.stepBadge}</span>
            <span id="profile-v2-explore-title">{copy.title}</span>
          </p>
          <p className={styles.zoneLead}>{copy.lead}</p>
        </div>
      </header>

      <div className={styles.natalDestination} data-testid="profile-v2-natal">
        <div className={styles.natalDestinationVisual} aria-hidden={!hasWheel}>
          {hasWheel && natalPreview ? (
            <div className={styles.natalDestinationWheel}>
              <NatalChartWheel {...natalWheelProps(natalPreview)} />
            </div>
          ) : (
            // eslint-disable-next-line @next/next/no-img-element -- static wash plate
            <img
              src="/images/cosmic/celestial_wash.webp"
              alt=""
              className={styles.natalDestinationWash}
            />
          )}
        </div>

        <div className={styles.natalDestinationCopy}>
          <p className={styles.exploreTeaserTitle} id="profile-v2-natal-title">
            {copy.natalTitle}
          </p>
          <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.sources.lead}</p>
          <ul className={styles.natalBenefitList}>
            {copy.benefits.map((line) => (
              <li key={line} className={styles.natalBenefitItem}>
                <span className={styles.natalBenefitMark} aria-hidden>
                  ✓
                </span>
                {line}
              </li>
            ))}
          </ul>
          <button
            type="button"
            className={styles.secondaryCta}
            data-testid="profile-v2-open-explore"
            aria-expanded={open}
            aria-controls="profile-v2-explore-body"
            onClick={onToggle}
          >
            {open ? copy.hide : copy.open}
            <span aria-hidden> {open ? "↑" : "→"}</span>
          </button>
        </div>
      </div>

      <ProfileMotionExpand open={open}>
        <div id="profile-v2-explore-body" data-testid="profile-v2-explore-body">
          {progressiveDetails.length ? (
            <div className={styles.exploreDetails} data-testid="profile-v2-progressive-details">
              <p className={styles.zoneLabel}>{copy.detailsTitle}</p>
              {progressiveDetails.map((item) => (
                <article
                  key={item.id}
                  className={styles.exploreDetailCard}
                  data-testid={`profile-v2-detail-${item.id}`}
                >
                  <p className={styles.traitLabel}>{item.label}</p>
                  {item.lines.map((line) => (
                    <p key={line} className={styles.traitLine}>
                      {line}
                    </p>
                  ))}
                </article>
              ))}
            </div>
          ) : null}

          {characterSlot}

          {model.lifeMission ? (
            <article className={styles.missionCard} data-testid="profile-v2-explore-mission">
              <p className={styles.factLabel}>{PROFILE_V2_COPY.zones.direction.missionLabel}</p>
              <p className={styles.missionText}>{model.lifeMission}</p>
            </article>
          ) : null}

          {lifeSpheres?.length ? (
            <div className={styles.sphereGrid} data-testid="profile-v2-explore-spheres">
              {lifeSpheres.map((sphere) => (
                <details key={sphere.id} className={styles.sphereCard}>
                  <summary className={styles.sphereSummary}>
                    <div className={styles.sphereSummaryMain}>
                      <p className={styles.sphereTitle}>{sphere.title}</p>
                      <p className={styles.sphereNeedLine}>{profileV2SphereCardLine(sphere)}</p>
                    </div>
                    <span className={styles.sphereChevron} aria-hidden>
                      ›
                    </span>
                  </summary>
                  <div className={styles.sphereDetails}>
                    <p className={styles.sphereDetailLabel}>Как проявляется</p>
                    <p className={styles.sphereBody}>{sphere.how}</p>
                    <p className={styles.sphereDetailLabel}>Нужно</p>
                    <p className={styles.sphereMeta}>{sphere.need}</p>
                    <p className={styles.sphereDetailLabel}>Риск</p>
                    <p className={styles.sphereMeta}>{sphere.risk}</p>
                    <p className={styles.sphereDetailLabel}>Включает</p>
                    <p className={styles.sphereMeta}>{sphere.turnsOn}</p>
                  </div>
                </details>
              ))}
            </div>
          ) : null}

          {deep ? (
            <div className={styles.skyContent} data-testid="profile-v2-natal-deep">
              <p className={styles.zoneLead} style={{ marginBottom: "0.75rem" }}>
                {copy.exploreHint}
              </p>
              <ProfileChartSection
                natalPreview={deep.natalPreview}
                coreNumerology={deep.coreNumerology}
                previewError={deep.previewError}
                onReloadPreview={deep.onReloadPreview}
                lifeMapSections={deep.lifeMapSections}
                fullChartOpen={deepExpanded}
                signatureDefaultOpen={false}
              />
              <p className={styles.zoneLead} style={{ marginTop: "1rem" }}>
                {copy.updatedNote}
              </p>
            </div>
          ) : null}

          <p className={styles.zoneLead}>
            {PROFILE_V2_COPY.mapsCtaHint}{" "}
            <Link href="/maps/mood">{PROFILE_V2_COPY.mapsCta}</Link>
          </p>
        </div>
      </ProfileMotionExpand>
    </section>
  );
}
