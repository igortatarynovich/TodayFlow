"use client";

import type { AspectCallout } from "@/lib/types";
import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";
import {
  ensureTwelveProfileHouses,
  HOUSE_FALLBACK,
  HOUSE_LAYER,
} from "@/components/profile/profileHouseConstants";
import { PlanetIcon } from "@/components/visualIdentity/PlanetIcon";
import styles from "./profileChartDeep.module.css";

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
  onReloadPreview: () => void;
};

export function ProfileChartFullMap({ natalPreview, onReloadPreview }: ProfileChartFullMapProps) {
  if (!natalPreview) {
    return (
      <div className={styles.emptyState}>
        <p className="orbit-body-sm" style={{ margin: 0, color: "#475569" }}>
          Полная карта появится после построения натала. Нажми «Обновить карту», когда данные рождения сохранены.
        </p>
        <div className={styles.actions} style={{ marginTop: "0.75rem" }}>
          <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={onReloadPreview}>
            Обновить карту
          </button>
        </div>
      </div>
    );
  }

  const houses = ensureTwelveProfileHouses(natalPreview);
  const houseInterpretations = natalPreview.interpretations?.houses ?? {};
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
            const interpretation = houseInterpretations[house.house];
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
                <p className={styles.houseText}>
                  {interpretation?.description?.trim() ||
                    interpretation?.theme?.trim() ||
                    HOUSE_FALLBACK[house.house]}
                </p>
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
              <AspectCard key={callout.aspect_id || `${callout.bodies}-${callout.label}`} callout={callout} />
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

function AspectCard({ callout }: { callout: AspectCallout }) {
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

  return (
    <article className={`${styles.aspectCard} ${cardClass}`}>
      <div className={styles.aspectHeader}>
        <p className={styles.aspectLabel}>{callout.label}</p>
        {callout.tension_level ? (
          <p className={`${styles.aspectBadge} ${badgeClass}`}>{tensionLabel(callout.tension_level)}</p>
        ) : null}
      </div>
      {callout.bodies ? <p className={styles.aspectBodies}>{callout.bodies}</p> : null}
      {callout.description ? <p className={styles.aspectDescription}>{callout.description}</p> : null}
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
