"use client";

import type { AspectCallout } from "@/lib/types";
import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";
import {
  ensureTwelveProfileHouses,
  HOUSE_FALLBACK,
  HOUSE_LAYER,
} from "@/components/profile/profileHouseConstants";
import { PlanetIcon } from "@/components/visualIdentity/PlanetIcon";
import styles from "@/design-system/profile/dsProfileChartDeep.module.css";

const PLANET_LABELS: Record<string, string> = {
  sun: "Солнце",
  moon: "Луна",
  mercury: "Меркурий",
  venus: "Венера",
  mars: "Марс",
  jupiter: "Юпитер",
  saturn: "Сатурн",
  uranus: "Уран",
  neptune: "Нептун",
  pluto: "Плутон",
};

const KEY_HOUSES = new Set([1, 4, 7, 10]);

type ProfileChartFullMapProps = {
  natalPreview: NatalChartPreview | null;
  natalPreviewLoading?: boolean;
  onReloadPreview: () => void;
  /** CE person-voice lines keyed by house number string — preferred over encyclopedia. */
  housePersonLines?: Record<
    string,
    { line?: string; how?: string; do?: string } | undefined
  > | null;
  /** CE person-voice aspect essays keyed by aspect_id / normalized bodies. */
  aspectPersonLines?: Record<string, { line?: string } | undefined> | null;
};

export function ProfileChartFullMap({
  natalPreview,
  natalPreviewLoading = false,
  onReloadPreview,
  housePersonLines = null,
  aspectPersonLines = null,
}: ProfileChartFullMapProps) {
  if (!natalPreview) {
    return (
      <div className={styles.emptyState}>
        <p className="orbit-body-sm" style={{ margin: 0, color: "#475569" }}>
          {natalPreviewLoading
            ? "Собираем полную карту…"
            : "Полная карта появится после построения натала. Нажми «Обновить карту», когда данные рождения сохранены."}
        </p>
        {!natalPreviewLoading ? (
          <div className={styles.actions} style={{ marginTop: "0.75rem" }}>
            <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={onReloadPreview}>
              Обновить карту
            </button>
          </div>
        ) : null}
      </div>
    );
  }

  const houses = ensureTwelveProfileHouses(natalPreview);
  const callouts = natalPreview.aspects?.callouts ?? [];
  const planets = Object.entries(natalPreview.positions || {}).sort(([a], [b]) => a.localeCompare(b));

  return (
    <div className={styles.sectionBlock}>
      <section aria-labelledby="profile-chart-houses">
        <p id="profile-chart-houses" className={styles.sectionHeading}>
          12 домов
        </p>
        <div className={styles.housesGrid}>
          {houses.map((house) => {
            const layer = HOUSE_LAYER[house.house];
            const signLabel = formatHouseSign(house.sign, house.degree);
            const isKey = KEY_HOUSES.has(house.house);

            return (
              <article
                key={house.house}
                className={`${styles.houseCard} ${isKey ? styles.houseCardKey : ""}`}
              >
                <div className={styles.houseTop}>
                  <p className={styles.houseNumber}>{house.house} дом</p>
                  {signLabel ? <p className={styles.houseSign}>{signLabel}</p> : null}
                </div>
                <p className={styles.houseTitle}>{layer?.title ?? `Дом ${house.house}`}</p>
                {(() => {
                  const ce = housePersonLines?.[String(house.house)];
                  const how = ce?.how?.trim() || ce?.line?.trim() || null;
                  const doLine = ce?.do?.trim() || null;
                  if (how) {
                    return (
                      <>
                        <p className={styles.houseText}>{how}</p>
                        {doLine ? <p className={styles.houseDo}>{doLine}</p> : null}
                      </>
                    );
                  }
                  // No CE thesis: short person-facing fallback only — never natal encyclopedia.
                  const short = HOUSE_FALLBACK[house.house] || null;
                  if (!short) return null;
                  return <p className={styles.houseText}>{short}</p>;
                })()}
              </article>
            );
          })}
        </div>
      </section>

      {planets.length ? (
        <section aria-labelledby="profile-chart-planets">
          <p id="profile-chart-planets" className={styles.sectionHeading}>
            Планеты в знаках
          </p>
          <div className={styles.tableWrap}>
            <table className={styles.planetTable}>
              <thead>
                <tr>
                  <th>Планета</th>
                  <th>Знак</th>
                  <th>Дом</th>
                </tr>
              </thead>
              <tbody>
                {planets.map(([key, data]) => (
                  <tr key={key}>
                    <td>
                      <span className={styles.planetCell}>
                        <PlanetIcon planet={key} size={20} stroke="currentColor" />
                        {PLANET_LABELS[key.toLowerCase()] ?? key}
                      </span>
                    </td>
                    <td>{data.sign || "—"}</td>
                    <td>{data.house ? `${data.house}` : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      <section aria-labelledby="profile-chart-aspects">
        <p id="profile-chart-aspects" className={styles.sectionHeading}>
          Аспекты
        </p>
        {callouts.length ? (
          <div className={styles.aspectsList}>
            {callouts.map((callout) => (
              <AspectCard
                key={callout.aspect_id || `${callout.bodies}-${callout.label}`}
                callout={callout}
                aspectPersonLines={aspectPersonLines}
              />
            ))}
          </div>
        ) : (
          <div className={styles.emptyState}>
            <p className="orbit-body-sm" style={{ margin: 0, color: "#475569" }}>
              Аспекты для этой карты пока не загружены. Попробуй обновить карту.
            </p>
            <div className={styles.actions} style={{ marginTop: "0.75rem" }}>
              <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={onReloadPreview}>
                Обновить карту
              </button>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

function resolveAspectPersonLine(
  callout: AspectCallout,
  aspectPersonLines?: Record<string, { line?: string } | undefined> | null,
): string | null {
  if (!aspectPersonLines) return null;
  const byId = callout.aspect_id ? aspectPersonLines[callout.aspect_id]?.line?.trim() : null;
  if (byId) return byId;
  const bodyBits = String(callout.bodies || "").match(/[A-Za-z]+/g) || [];
  const asp = String(callout.aspect_id || callout.label || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_|_$/g, "");
  // Prefer bodies + last aspect token from aspect_id (sun_moon_square → square)
  const aspToken = asp.includes("_") ? asp.split("_").slice(-1)[0] : asp;
  const key = [...bodyBits.map((b) => b.toLowerCase()), aspToken].filter(Boolean).join("_");
  const byKey = key ? aspectPersonLines[key]?.line?.trim() : null;
  if (byKey) return byKey;
  if (asp && aspectPersonLines[asp]?.line?.trim()) return aspectPersonLines[asp]?.line?.trim() || null;
  return null;
}

function AspectCard({
  callout,
  aspectPersonLines = null,
}: {
  callout: AspectCallout;
  aspectPersonLines?: Record<string, { line?: string } | undefined> | null;
}) {
  const tension = (callout.tension_level || "").toLowerCase();
  const cardClass =
    tension === "high"
      ? styles.aspectCardHigh
      : tension === "medium"
        ? styles.aspectCardMedium
        : styles.aspectCardLow;
  const badgeClass =
    tension === "high"
      ? styles.aspectBadgeHigh
      : tension === "medium"
        ? styles.aspectBadgeMedium
        : styles.aspectBadgeLow;
  const description =
    resolveAspectPersonLine(callout, aspectPersonLines) || callout.description?.trim() || null;

  return (
    <article className={`${styles.aspectCard} ${cardClass}`}>
      <div className={styles.aspectHeader}>
        <p className={styles.aspectLabel}>{callout.label}</p>
        {callout.tension_level ? (
          <p className={`${styles.aspectBadge} ${badgeClass}`}>{tensionLabel(callout.tension_level)}</p>
        ) : null}
      </div>
      {callout.bodies ? <p className={styles.aspectBodies}>{callout.bodies}</p> : null}
      {description ? <p className={styles.aspectDescription}>{description}</p> : null}
      {callout.keywords?.length ? (
        <div className={styles.aspectKeywords}>
          {callout.keywords.slice(0, 5).map((keyword) => (
            <p key={keyword} className={styles.aspectKeyword}>
              {keyword}
            </p>
          ))}
        </div>
      ) : null}
    </article>
  );
}

function tensionLabel(level: string) {
  const normalized = level.toLowerCase();
  if (normalized === "high") return "Высокое напряжение";
  if (normalized === "medium") return "Среднее напряжение";
  if (normalized === "low") return "Мягкий аспект";
  return level;
}

function formatHouseSign(sign?: string, degree?: number) {
  if (!sign) return null;
  if (typeof degree === "number" && !Number.isNaN(degree)) {
    return `${sign} · ${Math.round(degree)}°`;
  }
  return sign;
}
