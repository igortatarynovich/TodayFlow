"use client";

import type { ReactNode } from "react";
import { DsEyebrow, DsThemeViz } from "@/design-system";
import { ProfilePortalDeepSection } from "@/components/profile/ProfilePortalDeepSection";
import { ProfileChartSection } from "@/components/profile/ProfileChartSection";
import type { LifeMapSection, NatalChartPreview } from "@/components/profile/profilePanelTypes";
import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import type { CoreProfile } from "@/lib/types";
import type { ProfileQuickMapViewModel } from "@/lib/profilePage/buildProfileQuickMapData";
import { buildProfileHeroQuote, profileSphereIcon } from "@/lib/product-ui/profileWebFigmaHelpers";
import { PROFILE_QUICK_MAP_COPY as copy } from "@/components/profile/quickMap/profileQuickMapCopy";
import { ProfileWebMyDays } from "@/components/product-ui/ProfileWebMyDays";
import { profileWebChromeBundle } from "@/components/product-ui/profileWebChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";
import s from "@/components/product-ui/productWebScreens.module.css";

export type ProfileWebQuickMapProps = {
  model: ProfileQuickMapViewModel;
  lifeSpheres?: ProfileLifeSphere[];
  deepExpanded?: boolean;
  deep?: {
    natalPreview: NatalChartPreview | null;
    coreNumerology?: CoreProfile["numerology"] | null;
    previewError: string | null;
    onReloadPreview: () => void;
    lifeMapSections: LifeMapSection[];
  } | null;
  notices?: ReactNode;
};

function BalanceList({ items, variant }: { items: string[]; variant: "strengthen" | "drain" }) {
  if (!items.length) return null;
  return (
    <ul className={s.balanceList}>
      {items.map((item) => (
        <li key={item} className={s.balanceItem}>
          <span className={`${s.balanceDot} ${variant === "drain" ? s.balanceDotMuted : ""}`.trim()} aria-hidden />
          {item}
        </li>
      ))}
    </ul>
  );
}

function sphereHint(sphere: ProfileLifeSphere): string {
  const words = sphere.how.trim().split(/\s+/).slice(0, 2).join(" ");
  return words || sphere.turnsOn || sphere.need;
}

export function ProfileWebQuickMap({
  model,
  lifeSpheres,
  deepExpanded = false,
  deep,
  notices,
  locale,
}: ProfileWebQuickMapProps & { locale?: FlowPracticesChromeLocale }) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const profileChrome = profileWebChromeBundle(resolvedLocale);
  const quote = buildProfileHeroQuote(model.archetype, model.identitySummary);

  return (
    <div className={s.profileWebStack} data-testid="profile-web-quick-map">
      {notices}

      <section className={s.profileHero} aria-label={profileChrome.archetypeAria}>
        <div className={s.profileHeroOrbital}>
          <DsThemeViz />
        </div>
        {quote ? <blockquote className={s.profileHeroQuote}>{quote}</blockquote> : null}
      </section>

      {model.identitySummary ? (
        <section className={s.profileSection} aria-labelledby="profile-web-who">
          <DsEyebrow id="profile-web-who">{copy.whoTitle.toUpperCase()}</DsEyebrow>
          <p className={s.profileSectionLead}>{model.identitySummary}</p>
        </section>
      ) : null}

      {model.strengthens.length || model.drains.length ? (
        <section className={s.profileSection} aria-labelledby="profile-web-balance">
          <DsEyebrow id="profile-web-balance">Что усиливает / забирает</DsEyebrow>
          <div className={s.balanceGrid}>
            {model.strengthens.length ? (
              <article className={`${s.balanceCard} ${s.balanceCardStrengthen}`}>
                <p className={s.balanceCardTitle}>{copy.strengthensTitle}</p>
                <BalanceList items={model.strengthens} variant="strengthen" />
              </article>
            ) : null}
            {model.drains.length ? (
              <article className={`${s.balanceCard} ${s.balanceCardDrain}`}>
                <p className={s.balanceCardTitle}>{copy.drainsTitle}</p>
                <BalanceList items={model.drains} variant="drain" />
              </article>
            ) : null}
          </div>
        </section>
      ) : null}

      {lifeSpheres?.length ? (
        <section className={s.profileSection} aria-labelledby="profile-web-spheres">
          <DsEyebrow id="profile-web-spheres">Сферы жизни</DsEyebrow>
          <div className={s.sphereGrid}>
            {lifeSpheres.map((sphere) => (
              <article key={sphere.id} className={s.sphereTile}>
                <span className={s.sphereIcon} aria-hidden>
                  {profileSphereIcon(sphere.title)}
                </span>
                <div className={s.sphereCopy}>
                  <p className={s.sphereTitle}>{sphere.title}</p>
                  <p className={s.sphereHint}>{sphereHint(sphere)}</p>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <ProfileWebMyDays />

      {deep ? (
        <details className={s.profileDeepWrap}>
          <summary className={s.profileDeepSummary}>Полная карта и портал</summary>
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
        </details>
      ) : null}
    </div>
  );
}
