"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { ProfileMotionExpand, useProfileMotionInView } from "@/components/foundation/ProfileMotion";
import { ProfileChartSection } from "@/components/profile/ProfileChartSection";
import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import type { ProfileQuickMapDeepProps } from "@/components/profile/quickMap/ProfileQuickMapScreen";
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
  /** @deprecated Character materials live on main scroll now. */
  characterSlot?: ReactNode;
  /** Mission already on Character scroll — skip duplicate in Explore. */
  hideMission?: boolean;
};

/**
 * One natal journey card: signature + wheel + one fold.
 * No nested bordered wrappers — only this scene carries a frame.
 */
export function ProfileExploreSection({
  open,
  onToggle,
  progressiveDetails,
  model,
  lifeSpheres,
  deep,
  deepExpanded = false,
  hideMission = false,
}: ProfileExploreSectionProps) {
  const hasNatal = Boolean(deep);
  const hasExtraDetails =
    progressiveDetails.length > 0 ||
    Boolean(lifeSpheres?.length) ||
    (Boolean(model.lifeMission) && !hideMission);
  const motion = useProfileMotionInView<HTMLElement>(60);
  if (!hasNatal && !hasExtraDetails) return null;

  const copy = PROFILE_V2_COPY.zones.explore;

  return (
    <section
      id="profile-v2-explore"
      ref={motion.ref}
      className={`${styles.natalScene} ${motion.className}`.trim()}
      style={motion.style}
      data-testid="profile-v2-explore"
      aria-labelledby="profile-v2-explore-title"
    >
      <header className={styles.natalSceneHeader}>
        <p className={styles.journeyStepIndex}>
          <span className={styles.journeyStepBadge}>{copy.stepBadge}</span>
          <span id="profile-v2-explore-title">{copy.title}</span>
        </p>
      </header>

      <div className={styles.natalSceneBody}>
      {hasNatal && deep ? (
        <div data-testid="profile-v2-natal">
          <div data-testid="profile-v2-natal-deep">
            <ProfileChartSection
              natalPreview={deep.natalPreview}
              coreNumerology={deep.coreNumerology}
              previewError={deep.previewError}
              natalPreviewLoading={deep.natalPreviewLoading}
              onReloadPreview={deep.onReloadPreview}
              lifeMapSections={deep.lifeMapSections}
              fullChartOpen={deepExpanded}
              chartReading={deep.chartReading}
              methodologyNote={deep.methodologyNote}
              unavailableNote={deep.unavailableNote}
              housePersonLines={deep.housePersonLines}
              aspectPersonLines={deep.aspectPersonLines}
              showBirthSignature={false}
            />
          </div>
        </div>
      ) : (
        <p className={styles.zoneLead} data-testid="profile-v2-natal">
          {PROFILE_V2_COPY.zones.sources.lead}
        </p>
      )}

      {hasExtraDetails ? (
        <div className={styles.natalPaperBelow}>
          <button
            type="button"
            className={styles.natalPlainToggle}
            data-testid="profile-v2-open-explore"
            aria-expanded={open}
            aria-controls="profile-v2-explore-body"
            onClick={onToggle}
          >
            {open ? copy.hide : copy.open}
          </button>

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

              {model.lifeMission && !hideMission ? (
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
                        {sphere.turnsOff?.trim() ? (
                          <>
                            <p className={styles.sphereDetailLabel}>Выключает</p>
                            <p className={styles.sphereMeta}>{sphere.turnsOff}</p>
                          </>
                        ) : null}
                        {sphere.helps?.trim() ? (
                          <>
                            <p className={styles.sphereDetailLabel}>Помогает</p>
                            <p className={styles.sphereMeta}>{sphere.helps}</p>
                          </>
                        ) : null}
                        {sphere.practicalTips?.length ? (
                          <>
                            <p className={styles.sphereDetailLabel}>Практические шаги</p>
                            <ul className={styles.sphereTipsList}>
                              {sphere.practicalTips.map((tip) => (
                                <li key={tip} className={styles.sphereMeta}>
                                  {tip}
                                </li>
                              ))}
                            </ul>
                          </>
                        ) : null}
                      </div>
                    </details>
                  ))}
                </div>
              ) : null}

              <p className={styles.zoneLead}>
                {PROFILE_V2_COPY.mapsCtaHint}{" "}
                <Link href="/maps/mood">{PROFILE_V2_COPY.mapsCta}</Link>
              </p>
            </div>
          </ProfileMotionExpand>
        </div>
      ) : (
        <div className={styles.natalPaperBelow}>
          <p className={styles.zoneLead}>
            {PROFILE_V2_COPY.mapsCtaHint}{" "}
            <Link href="/maps/mood">{PROFILE_V2_COPY.mapsCta}</Link>
          </p>
        </div>
      )}
      </div>
    </section>
  );
}
