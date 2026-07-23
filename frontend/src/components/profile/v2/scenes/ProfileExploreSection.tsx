"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { ProfileMotionExpand, useProfileMotionInView } from "@/components/foundation/ProfileMotion";
import { ProfileChartSection } from "@/components/profile/ProfileChartSection";
import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import { ProfilePortalDeepSection } from "@/components/profile/ProfilePortalDeepSection";
import type { ProfileQuickMapDeepProps } from "@/components/profile/quickMap/ProfileQuickMapScreen";
import { ProfileV2SkySection } from "@/components/profile/v2/ProfileV2SkySection";
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
  const hasDetails = progressiveDetails.length > 0 || Boolean(characterSlot) || Boolean(lifeSpheres?.length);
  const motion = useProfileMotionInView<HTMLElement>(60);
  if (!hasNatal && !hasDetails && !model.lifeMission) return null;

  return (
    <section
      id="profile-v2-explore"
      ref={motion.ref}
      className={`${styles.zone} ${styles.journeyScene} ${styles.exploreScene} ${motion.className}`.trim()}
      style={motion.style}
      data-testid="profile-v2-explore"
      aria-labelledby="profile-v2-explore-title"
    >
      <header className={styles.zoneHeader}>
        <div>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>{PROFILE_V2_COPY.zones.explore.stepBadge}</span>
            <span id="profile-v2-explore-title">{PROFILE_V2_COPY.zones.explore.title}</span>
          </p>
          <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.explore.lead}</p>
        </div>
      </header>

      <div className={styles.exploreTeaser}>
        <div className={styles.exploreTeaserVisual} aria-hidden>
          {/* eslint-disable-next-line @next/next/no-img-element -- static public WebP */}
          <img src="/images/cosmic/observe.webp" alt="" className={styles.exploreTeaserImage} />
        </div>
        <div className={styles.exploreTeaserCopy}>
          <p className={styles.exploreTeaserTitle}>{PROFILE_V2_COPY.zones.explore.natalTitle}</p>
          <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.sources.lead}</p>
          <button
            type="button"
            className={styles.secondaryCta}
            data-testid="profile-v2-open-explore"
            aria-expanded={open}
            aria-controls="profile-v2-explore-body"
            onClick={onToggle}
          >
            {open ? PROFILE_V2_COPY.zones.explore.hide : PROFILE_V2_COPY.zones.explore.open}
            <span aria-hidden> {open ? "↑" : "→"}</span>
          </button>
        </div>
      </div>

      <ProfileMotionExpand open={open}>
        <div id="profile-v2-explore-body" data-testid="profile-v2-explore-body">
          {progressiveDetails.length ? (
            <div className={styles.exploreDetails} data-testid="profile-v2-progressive-details">
              <p className={styles.zoneLabel}>{PROFILE_V2_COPY.zones.explore.detailsTitle}</p>
              {progressiveDetails.map((item) => (
                <article key={item.id} className={styles.exploreDetailCard} data-testid={`profile-v2-detail-${item.id}`}>
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

          <p className={styles.zoneLead}>
            {PROFILE_V2_COPY.mapsCtaHint}{" "}
            <Link href="/maps/mood">{PROFILE_V2_COPY.mapsCta}</Link>
          </p>

          {deep ? (
            <section
              id="profile-v2-natal"
              className={`${styles.zone} ${styles.skyZone}`.trim()}
              aria-labelledby="profile-v2-natal-title"
              data-testid="profile-v2-natal"
            >
              <div className={styles.skyZoneAtmosphere} aria-hidden>
                {/* eslint-disable-next-line @next/next/no-img-element -- static public WebP */}
                <img src="/images/cosmic/nebula.webp" alt="" className={styles.skyZoneAtmosphereImage} />
              </div>
              <header className={styles.zoneHeader}>
                <div>
                  <p id="profile-v2-natal-title" className={styles.zoneLabel}>
                    {PROFILE_V2_COPY.zones.explore.natalTitle}
                  </p>
                  <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.sources.lead}</p>
                </div>
              </header>
              <div className={styles.skyContent}>
                <ProfileV2SkySection
                  natalPreview={deep.natalPreview}
                  previewError={deep.previewError}
                  onReloadPreview={deep.onReloadPreview}
                  frameworkAnchors={model.frameworkAnchors}
                  frameworkCards={model.frameworkCards}
                />
                <ProfilePortalDeepSection defaultOpen={false}>
                  <p className={styles.zoneLead} style={{ marginBottom: "0.75rem" }}>
                    {PROFILE_V2_COPY.zones.explore.exploreHint}
                  </p>
                  <ProfileChartSection
                    natalPreview={deep.natalPreview}
                    coreNumerology={deep.coreNumerology}
                    previewError={deep.previewError}
                    onReloadPreview={deep.onReloadPreview}
                    lifeMapSections={deep.lifeMapSections}
                    fullChartOpen={deepExpanded}
                  />
                </ProfilePortalDeepSection>
              </div>
              <p className={styles.zoneLead} style={{ marginTop: "1rem" }}>
                {PROFILE_V2_COPY.zones.explore.updatedNote}
              </p>
            </section>
          ) : null}
        </div>
      </ProfileMotionExpand>
    </section>
  );
}
