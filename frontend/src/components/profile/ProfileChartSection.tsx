"use client";

import Link from "next/link";
import { NatalChartWheel } from "@/components/natal-chart/NatalChartWheel";
import { ProfileChartFullMap } from "@/components/profile/ProfileChartFullMap";
import { ProfileExpandableSection } from "@/components/profile/ProfileExpandableSection";
import type { LifeMapSection, NatalChartPreview } from "@/components/profile/profilePanelTypes";
import { buildNumerologySignatureCards } from "@/components/profile/profileNumerologySignature";
import type { CoreProfile } from "@/lib/types";
import styles from "./profileChartDeep.module.css";

export type ProfileChartSectionProps = {
  natalPreview: NatalChartPreview | null;
  /** Числа из ядра профиля: путь, имя, суть, внешняя линия; показываем рядом с наталом. */
  coreNumerology?: CoreProfile["numerology"] | null;
  previewError: string | null;
  /** True while structure/full natal request is in flight. */
  natalPreviewLoading?: boolean;
  onReloadPreview: () => void;
  lifeMapSections: LifeMapSection[];
  fullChartOpen?: boolean;
  /** @deprecated Signature is always visible; kept for call-site compat. */
  signatureDefaultOpen?: boolean;
  /** @deprecated Always renders as one surface; kept for call-site compat. */
  layout?: "inline" | "expandable";
  /** Step-5 funnel: connected natal reading under signature cards. */
  chartReading?: string | null;
  methodologyNote?: string | null;
  unavailableNote?: string | null;
  housePersonLines?: Record<
    string,
    { line?: string; how?: string; do?: string } | undefined
  > | null;
  aspectPersonLines?: Record<string, { line?: string } | undefined> | null;
};

/**
 * One natal surface: signature + wheel always on.
 * Full houses / planets / aspects (+ life map) behind a single accordion.
 */
export function ProfileChartSection({
  natalPreview,
  coreNumerology,
  previewError,
  natalPreviewLoading = false,
  onReloadPreview,
  lifeMapSections,
  fullChartOpen = false,
  chartReading = null,
  methodologyNote = null,
  unavailableNote = null,
  housePersonLines = null,
  aspectPersonLines = null,
}: ProfileChartSectionProps) {
  const quickSignature = buildQuickSignature(natalPreview);
  const numerologyCards = buildNumerologySignatureCards(coreNumerology);
  const aspectLines = natalPreview?.aspects?.callouts ?? [];
  const emptyState = (
    <div className={styles.emptyState}>
      <p className="orbit-body-sm" style={{ margin: 0, color: "#475569" }}>
        {natalPreviewLoading
          ? "Собираем натальную карту…"
          : previewError
            ? "Не удалось загрузить карту. Попробуй обновить."
            : "Карта еще не построена. Нажми обновить, когда профиль будет готов."}
      </p>
      {!natalPreviewLoading ? (
        <div className={styles.actions} style={{ marginTop: "0.85rem" }}>
          <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={onReloadPreview}>
            Обновить карту
          </button>
        </div>
      ) : null}
    </div>
  );
  const readingBlock =
    chartReading || methodologyNote || unavailableNote ? (
      <div className={styles.chartReading} data-testid="profile-chart-reading">
        {methodologyNote ? <p className={styles.chartReadingMethod}>{methodologyNote}</p> : null}
        {chartReading ? <p className={styles.chartReadingBody}>{chartReading}</p> : null}
        {unavailableNote ? <p className={styles.chartReadingUnavailable}>{unavailableNote}</p> : null}
      </div>
    ) : null;

  return (
    <div className={styles.chartStack} data-testid="profile-chart-inline">
      {natalPreview ? (
        <>
          {quickSignature.length ? (
            <div className={styles.signatureGrid} data-testid="profile-chart-signature">
              {quickSignature.map((item) => (
                <div
                  key={item.label}
                  className={[
                    styles.signatureCard,
                    item.weight === "sun" ? styles.signatureCardSun : "",
                    item.weight === "moon" ? styles.signatureCardMoon : "",
                    item.weight === "asc" ? styles.signatureCardAsc : "",
                    item.weight === "mc" ? styles.signatureCardMc : "",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                >
                  <span
                    className={[
                      styles.signatureGlyph,
                      item.weight === "sun" ? styles.signatureGlyphSun : "",
                      item.weight === "moon" ? styles.signatureGlyphMoon : "",
                      item.weight === "asc" ? styles.signatureGlyphAsc : "",
                      item.weight === "mc" ? styles.signatureGlyphMc : "",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                    aria-hidden
                  />
                  <p className={styles.signatureLabel}>{item.label}</p>
                  <p className={styles.signatureValue}>{item.value}</p>
                  {item.hint ? <p className={styles.signatureHint}>{item.hint}</p> : null}
                </div>
              ))}
            </div>
          ) : null}
          {readingBlock}
          {numerologyCards.length ? (
            <div
              className={styles.signatureGrid}
              style={{ marginTop: quickSignature.length ? "0.65rem" : 0 }}
              data-testid="profile-chart-numerology"
            >
              {numerologyCards.map((item) => (
                <div key={item.key} className={`${styles.signatureCard} ${styles.signatureCardNumerology}`}>
                  <p className={`${styles.signatureLabel} ${styles.signatureLabelNumerology}`}>{item.label}</p>
                  <p className={styles.signatureValue}>{item.value}</p>
                  {item.hint ? <p className={styles.signatureHint}>{item.hint}</p> : null}
                </div>
              ))}
            </div>
          ) : null}
          <div className={styles.wheelWrap} data-testid="profile-chart-wheel">
            <NatalChartWheel
              chartPositions={Object.entries(natalPreview.positions || {})
                .filter(([planet]) => {
                  const key = planet.toLowerCase();
                  return [
                    "sun",
                    "moon",
                    "mercury",
                    "venus",
                    "mars",
                    "jupiter",
                    "saturn",
                    "uranus",
                    "neptune",
                    "pluto",
                  ].includes(key);
                })
                .map(([planet, data]) => ({
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
              aspects={aspectLines}
            />
          </div>
        </>
      ) : (
        emptyState
      )}
      {previewError ? (
        <p className="orbit-body-sm" style={{ margin: "0.75rem 0 0", color: "#991b1b" }}>
          {previewError}
        </p>
      ) : null}

      <ProfileExpandableSection
        title="Полный разбор"
        subtitle="Опоры жизни, 12 домов, планеты и аспекты."
        defaultOpen={fullChartOpen}
        variant="plain"
      >
        {lifeMapSections.length ? (
          <div className={styles.lifeMapGrid} style={{ marginBottom: "1rem" }}>
            {lifeMapSections.map((item) => (
              <Link
                key={item.house}
                href={item.href}
                className={styles.lifeMapCard}
                style={{ borderLeft: `3px solid ${item.accent}` }}
              >
                <p className={styles.lifeMapHouse} style={{ color: item.accent }}>
                  {item.house} дом
                </p>
                <p className={styles.lifeMapTitle}>{item.title}</p>
                <p className={styles.lifeMapSummary}>{item.summary}</p>
                {item.do ? <p className={styles.lifeMapDo}>{item.do}</p> : null}
                <p className={styles.lifeMapRoute}>{item.routeTitle}</p>
              </Link>
            ))}
          </div>
        ) : null}
        <ProfileChartFullMap
          natalPreview={natalPreview}
          natalPreviewLoading={natalPreviewLoading}
          onReloadPreview={onReloadPreview}
          housePersonLines={housePersonLines}
          aspectPersonLines={aspectPersonLines}
        />
      </ProfileExpandableSection>
    </div>
  );
}

function buildQuickSignature(natalPreview: NatalChartPreview | null) {
  if (!natalPreview) return [];

  const sun = natalPreview.positions?.sun;
  const moon = natalPreview.positions?.moon;
  const ascSign = natalPreview.ascendant?.sign || natalPreview.houses?.[0]?.sign || "—";
  const ascDegree = natalPreview.ascendant?.longitude ?? natalPreview.ascendant?.degree;
  const mcSign = natalPreview.positions?.mc?.sign || natalPreview.houses?.[9]?.sign || null;

  return [
    {
      label: "Солнце",
      value: sun?.sign || "—",
      hint: sun?.house ? `${sun.house} дом` : undefined,
      weight: "sun" as const,
    },
    {
      label: "Луна",
      value: moon?.sign || "—",
      hint: moon?.house ? `${moon.house} дом` : undefined,
      weight: "moon" as const,
    },
    {
      label: "Асцендент",
      value: ascSign,
      hint: typeof ascDegree === "number" ? `${Math.round(ascDegree)}°` : undefined,
      weight: "asc" as const,
    },
    ...(mcSign
      ? [
          {
            label: "MC",
            value: mcSign,
            hint: undefined as string | undefined,
            weight: "mc" as const,
          },
        ]
      : []),
  ].filter((item) => item.value && item.value !== "—");
}
