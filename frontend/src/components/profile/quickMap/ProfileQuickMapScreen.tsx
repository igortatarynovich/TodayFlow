"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { HeroLarge, heroLargeStyles } from "@/components/foundation/HeroLarge";
import { ProfileWebMyDays } from "@/components/product-ui/ProfileWebMyDays";
import { ProfileMotionStagger } from "@/components/foundation/ProfileMotion";
import { ProfileChartSection } from "@/components/profile/ProfileChartSection";
import { ProfilePortalDeepSection } from "@/components/profile/ProfilePortalDeepSection";
import type { LifeMapSection, NatalChartPreview } from "@/components/profile/profilePanelTypes";
import type { CoreProfile } from "@/lib/types";
import type { ProfileQuickMapViewModel } from "@/lib/profilePage/buildProfileQuickMapData";
import { ProfilePortraitSection } from "@/components/profile/ProfilePortraitSection";
import { PROFILE_CHART_SECTION_ID, PROFILE_LIFE_SPHERES_SECTION_ID } from "@/lib/profileRoutes";
import { PROFILE_QUICK_MAP_COPY as copy } from "./profileQuickMapCopy";
import { ProfileRelationshipInsightsBlock } from "@/components/profile/ProfileRelationshipInsightsBlock";
import { ProfileLifeSection } from "@/components/profile/ProfileLifeSection";
import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import { ProfileLivingMapsSection } from "@/components/profile/ProfileLivingMapsSection";
import { ProfileCumInsightsBlock } from "@/components/profile/ProfileCumInsightsBlock";
import type { CompactUserModel } from "@/lib/types";
import styles from "./profileQuickMap.module.css";

export type ProfileQuickMapDeepProps = {
  natalPreview: NatalChartPreview | null;
  coreNumerology?: CoreProfile["numerology"] | null;
  previewError: string | null;
  onReloadPreview: () => void;
  lifeMapSections: LifeMapSection[];
  chartReading?: string | null;
  methodologyNote?: string | null;
  unavailableNote?: string | null;
};

export type ProfileQuickMapScreenProps = {
  model: ProfileQuickMapViewModel;
  onOpenBirthData: () => void;
  lifeSpheres?: ProfileLifeSphere[];
  deepExpanded?: boolean;
  deep?: ProfileQuickMapDeepProps | null;
  livingObservation?: string | null;
  cum?: CompactUserModel | null;
  /** Setup / first-today notices rendered above hero (Product shell). */
  notices?: ReactNode;
};

function QuickMapList({ items }: { items: string[] }) {
  if (!items.length) return null;
  return (
    <ul className={styles.quickMapBullets}>
      {items.map((item) => (
        <li key={item} className={styles.quickMapBullet}>
          {item}
        </li>
      ))}
    </ul>
  );
}

function QuickMapTags({ items }: { items: string[] }) {
  if (!items.length) return null;
  return (
    <div className={styles.quickMapTags}>
      {items.map((item) => (
        <p key={item} className={styles.quickMapTag}>
          {item}
        </p>
      ))}
    </div>
  );
}

export function ProfileQuickMapScreen({
  model,
  onOpenBirthData,
  lifeSpheres,
  deepExpanded = false,
  deep,
  livingObservation,
  cum,
  notices,
}: ProfileQuickMapScreenProps) {
  const heroChips = model.frameworkAnchors.slice(0, 4);
  const hasResumePair = model.strengthens.length > 0 || model.drains.length > 0;
  const shapeAudit = process.env.NEXT_PUBLIC_PROFILE_SHAPE_AUDIT === "1";

  return (
    <div
      className={[styles.quickMapShell, shapeAudit ? styles.quickMapShapeAudit : ""].filter(Boolean).join(" ")}
      data-testid="profile-quick-map"
    >
      <div className={styles.quickMapStack}>
        {notices}
        <ProfilePortraitSection variant="quickMap">
        <HeroLarge
          symbolSeed={model.archetype}
          kicker={copy.pageKicker}
          sectionLabel={copy.whoTitle}
          title={model.archetype}
          digest={model.identitySummary}
          pillars={heroChips.map((chip, index) => ({
            id: chip.id,
            label: chip.label,
            accent: index === 0,
          }))}
          topAction={
            <button type="button" className={heroLargeStyles.topAction} onClick={onOpenBirthData}>
              {copy.birthData}
            </button>
          }
          ariaLabel={copy.whoTitle}
        />

        <ProfileMotionStagger baseDelayMs={120}>
        {hasResumePair ? (
          <div className={styles.quickMapResumeGrid}>
            {model.strengthens.length ? (
              <section className={`${styles.quickMapPanel} ${styles.quickMapPanelPositive}`} aria-labelledby="profile-strengthens">
                <p id="profile-strengthens" className={styles.quickMapSectionLabel}>
                  {copy.strengthensTitle}
                </p>
                <QuickMapList items={model.strengthens} />
              </section>
            ) : null}

            {model.drains.length ? (
              <section className={`${styles.quickMapPanel} ${styles.quickMapPanelNegative}`} aria-labelledby="profile-drains">
                <p id="profile-drains" className={styles.quickMapSectionLabel}>
                  {copy.drainsTitle}
                </p>
                <QuickMapList items={model.drains} />
              </section>
            ) : null}
          </div>
        ) : null}

        {model.decisionStyle ? (
          <section className={`${styles.quickMapPanel} ${styles.quickMapPanelAccent}`} aria-labelledby="profile-decisions">
            <p id="profile-decisions" className={styles.quickMapSectionLabel}>
              {copy.decisionsTitle}
            </p>
            <p className={styles.quickMapSectionLead}>{model.decisionStyle}</p>
          </section>
        ) : null}

        {model.perceivedAs.length ? (
          <section className={styles.quickMapSection} aria-labelledby="profile-perceived">
            <p id="profile-perceived" className={styles.quickMapSectionLabel}>
              {copy.perceivedTitle}
            </p>
            <QuickMapTags items={model.perceivedAs} />
          </section>
        ) : null}

        {model.thriveAreas.length ? (
          <section className={styles.quickMapSection} aria-labelledby="profile-thrive">
            <p id="profile-thrive" className={styles.quickMapSectionLabel}>
              {copy.thriveTitle}
            </p>
            <QuickMapTags items={model.thriveAreas} />
          </section>
        ) : null}

        {model.lifeMission ? (
          <section className={styles.quickMapSection} aria-labelledby="profile-mission">
            <p id="profile-mission" className={styles.quickMapSectionLabel}>
              {copy.missionTitle}
            </p>
            <p className={styles.quickMapMission}>{model.lifeMission}</p>
          </section>
        ) : null}

        {model.frameworkCards.length ? (
          <section className={styles.quickMapSection} aria-labelledby="profile-framework">
            <p id="profile-framework" className={styles.quickMapSectionLabel}>
              {model.frameworkTitle}
            </p>
            {model.frameworkLead ? <p className={styles.quickMapSectionLead}>{model.frameworkLead}</p> : null}

            <div className={styles.quickMapFramework}>
              {model.frameworkAnchors.length ? (
                <div>
                  <p className={styles.quickMapSectionLabel}>{copy.frameworkAnchorsLead}</p>
                  <div className={styles.quickMapAnchors}>
                    {model.frameworkAnchors.map((anchor) => (
                      <p key={anchor.id} className={styles.quickMapAnchor}>
                        {anchor.label}
                      </p>
                    ))}
                  </div>
                </div>
              ) : null}

              <div className={styles.quickMapCards}>
                {model.frameworkCards.map((card) => (
                  <article key={card.id} className={styles.quickMapCard}>
                    <p className={styles.quickMapCardTitle}>{card.title}</p>
                    {card.anchor ? <p className={styles.quickMapCardAnchor}>{card.anchor}</p> : null}
                    <p className={styles.quickMapCardBody}>{card.body}</p>
                  </article>
                ))}
              </div>
            </div>
          </section>
        ) : null}

        </ProfileMotionStagger>

        </ProfilePortraitSection>

        {lifeSpheres?.length ? (
          <div id={PROFILE_LIFE_SPHERES_SECTION_ID}>
            <ProfileLifeSection spheres={lifeSpheres} />
          </div>
        ) : null}

        <ProfileWebMyDays />

        <ProfileRelationshipInsightsBlock cum={cum} />

        <ProfileCumInsightsBlock cum={cum} />

        <ProfileLivingMapsSection variant="quickMap" livingObservation={livingObservation} />

        {deep ? (
          <div className={styles.quickMapDeepWrap} id={PROFILE_CHART_SECTION_ID}>
            <ProfilePortalDeepSection defaultOpen={deepExpanded}>
              <ProfileChartSection
                natalPreview={deep.natalPreview}
                coreNumerology={deep.coreNumerology}
                previewError={deep.previewError}
                onReloadPreview={deep.onReloadPreview}
                lifeMapSections={deep.lifeMapSections}
                fullChartOpen={deepExpanded}
                chartReading={deep.chartReading}
                methodologyNote={deep.methodologyNote}
                unavailableNote={deep.unavailableNote}
              />
            </ProfilePortalDeepSection>
          </div>
        ) : null}

        <Link href="/today" className={`orbit-button orbit-button-primary ${styles.quickMapTodayCta}`}>
          {copy.todayLink}
        </Link>
      </div>
    </div>
  );
}
