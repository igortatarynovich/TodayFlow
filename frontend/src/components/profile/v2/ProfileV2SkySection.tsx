"use client";

import { NatalChartWheel } from "@/components/natal-chart/NatalChartWheel";
import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";
import type { AspectCallout } from "@/lib/types";
import styles from "@/components/profile/v2/profileV2System.module.css";

const HOUSE_ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"] as const;

const HOUSE_KEYWORD_RU: Record<number, string> = {
  1: "образ",
  2: "ресурс",
  3: "слово",
  4: "дом",
  5: "творчество",
  6: "ритуал",
  7: "связь",
  8: "глубина",
  9: "путь",
  10: "дело",
  11: "сообщество",
  12: "тишина",
};

export type ProfileV2SkySectionProps = {
  natalPreview: NatalChartPreview | null;
  previewError: string | null;
  onReloadPreview: () => void;
  updatedLabel: string;
};

function formatNatalChipTime(updatedLabel: string): string {
  const match = updatedLabel.match(/(\d{1,2}:\d{2})/);
  return match?.[1] ?? new Intl.DateTimeFormat("ru-RU", { hour: "2-digit", minute: "2-digit" }).format(new Date());
}

function pickSkyAspects(callouts: AspectCallout[] | undefined, limit = 3): AspectCallout[] {
  if (!callouts?.length) return [];
  return callouts.slice(0, limit);
}

function houseKeyword(houseNum: number, preview: NatalChartPreview | null): string {
  const theme = preview?.interpretations?.houses?.[houseNum]?.theme?.trim();
  if (theme) {
    const short = theme.split(/[,:]/)[0]?.trim().toLowerCase();
    if (short && short.length <= 16) return short;
  }
  return HOUSE_KEYWORD_RU[houseNum] ?? "дом";
}

export function ProfileV2SkySection({
  natalPreview,
  previewError,
  onReloadPreview,
  updatedLabel,
}: ProfileV2SkySectionProps) {
  const aspects = pickSkyAspects(natalPreview?.aspects?.callouts);
  const natalChip = `натальная · ${formatNatalChipTime(updatedLabel)}`;

  return (
    <div className={styles.skyLayout} data-testid="profile-v2-sky-section">
      <div className={styles.skyHeaderMeta}>
        <span className={styles.skyLiveChip}>
          <span className={styles.skyLiveDot} aria-hidden />
          {natalChip}
        </span>
      </div>

      {natalPreview ? (
        <div className={styles.skyGrid}>
          <div className={styles.skyWheelPanel}>
            <div className={styles.skyWheelFrame}>
              <NatalChartWheel
                chartPositions={Object.entries(natalPreview.positions || {}).map(([planet, data]) => ({
                  body: planet,
                  sign: data.sign || "",
                  house: data.house,
                  degree: data.degree,
                  longitude: data.longitude || data.degree || 0,
                }))}
                houses={(natalPreview.houses || []).reduce(
                  (acc, house) => {
                    acc[`house_${house.house}`] = {
                      sign: house.sign,
                      degree: house.degree,
                      cusp_longitude: house.cusp_longitude,
                    };
                    return acc;
                  },
                  {} as Record<string, { sign?: string; degree?: number; cusp_longitude?: number }>,
                )}
                ascendant={natalPreview.ascendant?.longitude || natalPreview.ascendant?.degree || 0}
                aspects={aspects}
              />
            </div>
          </div>

          <div className={styles.skyAside}>
            {aspects.length ? (
              <div className={styles.skyAspectStack}>
                {aspects.map((aspect) => (
                  <article key={aspect.aspect_id} className={styles.skyAspectCard}>
                    <p className={styles.skyAspectTitle}>{aspect.label || aspect.bodies}</p>
                    <p className={styles.skyAspectBody}>{aspect.description}</p>
                  </article>
                ))}
              </div>
            ) : (
              <article className={styles.skyAspectCard}>
                <p className={styles.skyAspectTitle}>Натальные акценты</p>
                <p className={styles.skyAspectBody}>
                  Аспекты появятся после полного расчёта карты. Нажми «Обновить карту», если данные рождения уже
                  сохранены.
                </p>
              </article>
            )}

            <div className={styles.skyHouseGrid}>
              {HOUSE_ROMAN.map((roman, index) => {
                const houseNum = index + 1;
                return (
                  <article key={roman} className={styles.skyHouseCard}>
                    <p className={styles.skyHouseRoman}>{roman}</p>
                    <p className={styles.skyHouseKeyword}>{houseKeyword(houseNum, natalPreview)}</p>
                  </article>
                );
              })}
            </div>

            <p className={styles.skyFootnote}>
              L1 collapsed / L4 deep: на общем scroll виден смысл, а планеты, дома и натальные акценты раскрываются
              только здесь — внутри уровня 05.
            </p>
          </div>
        </div>
      ) : (
        <div className={styles.skyEmpty}>
          <p className={styles.skyAspectBody}>
            Карта ещё не построена. Сохрани данные рождения и обнови карту — колесо, дома и аспекты появятся здесь.
          </p>
          <button type="button" className={styles.skyReloadBtn} onClick={onReloadPreview}>
            Обновить карту
          </button>
        </div>
      )}

      {previewError ? <p className={styles.skyError}>{previewError}</p> : null}
    </div>
  );
}
