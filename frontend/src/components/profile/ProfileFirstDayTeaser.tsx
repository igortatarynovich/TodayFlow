"use client";

import Link from "next/link";
import {
  HeroLarge,
  HeroLargeChipRow,
  HeroLargeInsightPanel,
  heroLargeStyles,
} from "@/components/foundation/HeroLarge";
import { ProfileLivingMapsSection } from "@/components/profile/ProfileLivingMapsSection";
import { ProfilePortraitSection } from "@/components/profile/ProfilePortraitSection";
import { PROFILE_QUICK_MAP_COPY as portalCopy } from "@/components/profile/quickMap/profileQuickMapCopy";
import type { ProfileV0ViewModel } from "@/lib/profilePage/buildProfileV0Data";
import {
  INTENT_CHIP_OPTIONS,
  REALITY_CHIP_OPTIONS,
  type IntentTheme,
  type RealityState,
} from "@/lib/onboardingContext";
import editorialStyles from "@/components/profile/editorial/profileEditorial.module.css";

type ProfileFirstDayTeaserProps = {
  model: ProfileV0ViewModel;
  intentTheme?: IntentTheme | null;
  realityState?: RealityState | null;
  onOpenFullPortrait: () => void;
};

function chipLabel<T extends string>(
  options: Array<{ slug: T; label: string }>,
  slug: T | null | undefined,
): string | null {
  if (!slug) return null;
  return options.find((item) => item.slug === slug)?.label ?? slug;
}

export function ProfileFirstDayTeaser({
  model,
  intentTheme,
  realityState,
  onOpenFullPortrait,
}: ProfileFirstDayTeaserProps) {
  const { header } = model;
  const intentLabel = chipLabel(INTENT_CHIP_OPTIONS, intentTheme);
  const realityLabel = chipLabel(REALITY_CHIP_OPTIONS, realityState);

  const identityParts = [
    header.sunSignDisplay,
    header.lifePath != null ? `число пути ${header.lifePath}` : null,
  ].filter(Boolean);

  const teaserLine =
    header.intro?.trim() ||
    header.tagline?.trim() ||
    "Карта уже собрана — ниже короткий вход в портрет. Полный разбор откроется, когда будешь готов(а) углубиться.";

  const startChips = [
    intentLabel ? `Фокус: ${intentLabel}` : null,
    realityLabel ? `Состояние: ${realityLabel}` : null,
  ].filter(Boolean) as string[];

  return (
    <div className={heroLargeStyles.insightBand} data-testid="profile-first-day-teaser">
      <ProfilePortraitSection variant="editorial">
        <HeroLarge
          symbolSeed={header.archetypeLabel}
          kicker="Портрет · день 1"
          title={header.archetypeLabel}
          metaLine={identityParts.length ? identityParts.join(" · ") : null}
          digest={teaserLine}
          edgeToEdge={false}
          ariaLabel="Портрет первого дня"
        />

        {startChips.length ? (
          <HeroLargeInsightPanel eyebrow="Твой старт сегодня">
            <HeroLargeChipRow items={startChips} />
          </HeroLargeInsightPanel>
        ) : null}

        {header.qualities.length ? (
          <HeroLargeInsightPanel eyebrow="Первые якоря">
            <ul className={heroLargeStyles.anchorList}>
              {header.qualities.slice(0, 2).map((q) => (
                <li key={`${q.title}-${q.subtitle}`} className={heroLargeStyles.anchorItem}>
                  <strong>{q.title}</strong>
                  {q.subtitle ? ` — ${q.subtitle}` : ""}
                </li>
              ))}
            </ul>
          </HeroLargeInsightPanel>
        ) : null}
      </ProfilePortraitSection>

      <ProfileLivingMapsSection variant="editorial" showMyDays />

      <button
        type="button"
        className={`${editorialStyles.portal} ${editorialStyles.portalButton}`}
        data-testid="profile-first-day-portal"
        onClick={onOpenFullPortrait}
      >
        <p className={editorialStyles.portalKicker}>{portalCopy.portalKicker}</p>
        <p className={editorialStyles.portalTitle}>{portalCopy.portalTitle}</p>
        <p className={editorialStyles.portalSub}>{portalCopy.portalSub}</p>
        <span className={editorialStyles.portalCta}>Открыть полную карту →</span>
      </button>

      <Link href="/today" className={editorialStyles.linkBtn}>
        Вернуться в Today
      </Link>
    </div>
  );
}
