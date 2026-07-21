"use client";

import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";
import type { ProfileFrameworkAnchor, ProfileFrameworkCard } from "@/lib/profilePage/buildProfileQuickMapData";
import styles from "@/components/profile/v2/profileV2System.module.css";
import { PROFILE_V2_COPY } from "@/components/profile/v2/profileV2SystemCopy";

export type ProfileV2SkySectionProps = {
  natalPreview: NatalChartPreview | null;
  previewError: string | null;
  onReloadPreview: () => void;
  frameworkAnchors: ProfileFrameworkAnchor[];
  frameworkCards?: ProfileFrameworkCard[];
};

function roleForAnchor(id: string, cards: ProfileFrameworkCard[]): string | null {
  const card = cards.find((item) => item.id === id);
  const body = card?.body?.trim();
  if (!body) return null;
  const first = body.split(/[.!?]/)[0]?.trim();
  if (!first) return null;
  return first.length > 120 ? `${first.slice(0, 117)}…` : first;
}

export function ProfileV2SkySection({
  natalPreview,
  previewError,
  onReloadPreview,
  frameworkAnchors,
  frameworkCards = [],
}: ProfileV2SkySectionProps) {
  const signatures = frameworkAnchors.length
    ? frameworkAnchors
    : natalPreview
      ? [{ id: "natal", label: "Натальная карта рассчитана" }]
      : [];

  return (
    <div className={styles.skyLayout} data-testid="profile-v2-sky-section">
      <div className={styles.skyHeaderMeta}>
        <span className={styles.skyLiveChip}>
          <span className={styles.skyLiveDot} aria-hidden />
          источники личности
        </span>
      </div>

      {signatures.length ? (
        <div className={styles.factGrid}>
          {signatures.map((anchor) => {
            const role = roleForAnchor(anchor.id, frameworkCards);
            return (
              <article key={anchor.id} className={styles.factCard}>
                <p className={styles.factLabel}>{anchor.label}</p>
                {role ? <p className={styles.factHint}>{role}</p> : null}
              </article>
            );
          })}
        </div>
      ) : (
        <div className={styles.skyEmpty}>
          <p className={styles.skyAspectBody}>
            Сигнатуры появятся после сохранения данных рождения. Полная карта — за «Исследовать глубже».
          </p>
          <button type="button" className={styles.skyReloadBtn} onClick={onReloadPreview}>
            Обновить карту
          </button>
        </div>
      )}

      <p className={styles.skyFootnote}>{PROFILE_V2_COPY.zones.sources.exploreHint}</p>

      {previewError ? <p className={styles.skyError}>{previewError}</p> : null}
    </div>
  );
}
