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
  onReloadPreview: () => void;
  lifeMapSections: LifeMapSection[];
  fullChartOpen?: boolean;
};

export function ProfileChartSection({
  natalPreview,
  coreNumerology,
  previewError,
  onReloadPreview,
  lifeMapSections,
  fullChartOpen = false,
}: ProfileChartSectionProps) {
  const quickSignature = buildQuickSignature(natalPreview);
  const numerologyCards = buildNumerologySignatureCards(coreNumerology);
  const aspectLines = natalPreview?.aspects?.callouts ?? [];

  return (
    <div className={styles.chartStack}>
      <ProfileExpandableSection
        title="Натальная карта"
        subtitle="Сигнатура: знак Солнца и Луны, асцендент, личные числа и колесо."
        defaultOpen
      >
        {natalPreview ? (
          <>
            {quickSignature.length ? (
              <div className={styles.signatureGrid}>
                {quickSignature.map((item) => (
                  <div key={item.label} className={styles.signatureCard}>
                    <p className={styles.signatureLabel}>{item.label}</p>
                    <p className={styles.signatureValue}>{item.value}</p>
                    {item.hint ? <p className={styles.signatureHint}>{item.hint}</p> : null}
                  </div>
                ))}
              </div>
            ) : null}
            {numerologyCards.length ? (
              <div className={styles.signatureGrid} style={{ marginTop: quickSignature.length ? "0.65rem" : 0 }}>
                {numerologyCards.map((item) => (
                  <div key={item.key} className={`${styles.signatureCard} ${styles.signatureCardNumerology}`}>
                    <p className={`${styles.signatureLabel} ${styles.signatureLabelNumerology}`}>{item.label}</p>
                    <p className={styles.signatureValue}>{item.value}</p>
                    {item.hint ? <p className={styles.signatureHint}>{item.hint}</p> : null}
                  </div>
                ))}
              </div>
            ) : null}
            <div className={styles.wheelWrap}>
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
                aspects={aspectLines}
              />
            </div>
            <div className={styles.ribbon}>
              {buildZodiacRibbon(natalPreview).map((item) => (
                <span key={item.key} className={styles.ribbonChip}>
                  {item.glyph} {item.title}
                </span>
              ))}
            </div>
            <div className={styles.actions} style={{ marginTop: "0.85rem" }}>
              <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" onClick={onReloadPreview}>
                Обновить карту
              </button>
            </div>
          </>
        ) : (
          <div className={styles.emptyState}>
            <p className="orbit-body-sm" style={{ margin: 0, color: "#475569" }}>
              Карта еще не построена. Нажми обновить, когда профиль будет готов.
            </p>
          </div>
        )}
        {previewError ? (
          <p className="orbit-body-sm" style={{ margin: "0.75rem 0 0", color: "#991b1b" }}>
            {previewError}
          </p>
        ) : null}
      </ProfileExpandableSection>

      <ProfileExpandableSection
        title="Моя карта жизни"
        subtitle="Четыре главные опоры: кто ты, где дом, как строишь связь и как проявляешься в мире."
        defaultOpen={false}
      >
        <div className={styles.lifeMapGrid}>
          {lifeMapSections.map((item) => (
            <Link
              key={item.house}
              href={item.href}
              className={styles.lifeMapCard}
              style={{ border: `1px solid ${item.accent}2f` }}
            >
              <p className={styles.lifeMapHouse} style={{ color: item.accent }}>
                {item.house} дом
              </p>
              <p className={styles.lifeMapTitle}>{item.title}</p>
              <p className={styles.lifeMapSummary}>{item.summary}</p>
              <p className={styles.lifeMapRoute}>{item.routeTitle}</p>
            </Link>
          ))}
        </div>
      </ProfileExpandableSection>

      <ProfileExpandableSection
        title="Полная карта"
        subtitle="12 домов, планеты в знаках и аспекты — полный разбор натала."
        defaultOpen={fullChartOpen}
      >
        <ProfileChartFullMap natalPreview={natalPreview} onReloadPreview={onReloadPreview} />
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

  return [
    {
      label: "Солнце",
      value: sun?.sign || "—",
      hint: sun?.house ? `${sun.house} дом` : undefined,
    },
    {
      label: "Луна",
      value: moon?.sign || "—",
      hint: moon?.house ? `${moon.house} дом` : undefined,
    },
    {
      label: "Асцендент",
      value: ascSign,
      hint: typeof ascDegree === "number" ? `${Math.round(ascDegree)}°` : undefined,
    },
  ].filter((item) => item.value && item.value !== "—");
}

function buildZodiacRibbon(natalPreview: NatalChartPreview | null) {
  if (!natalPreview) return [];
  const signs = Array.from(
    new Set(
      Object.values(natalPreview.positions || {})
        .map((pos) => (pos?.sign || "").trim())
        .filter(Boolean),
    ),
  ).slice(0, 6);

  return signs.map((title) => ({
    key: title,
    title,
    glyph: zodiacGlyph(title),
  }));
}

function zodiacGlyph(sign: string) {
  const s = sign.toLowerCase();
  if (s.includes("aries") || s.includes("овен")) return "♈";
  if (s.includes("taurus") || s.includes("телец")) return "♉";
  if (s.includes("gemini") || s.includes("близнец")) return "♊";
  if (s.includes("cancer") || s.includes("рак")) return "♋";
  if (s.includes("leo") || s.includes("лев")) return "♌";
  if (s.includes("virgo") || s.includes("дева")) return "♍";
  if (s.includes("libra") || s.includes("вес")) return "♎";
  if (s.includes("scorpio") || s.includes("скорпион")) return "♏";
  if (s.includes("sagittarius") || s.includes("стрел")) return "♐";
  if (s.includes("capricorn") || s.includes("козер")) return "♑";
  if (s.includes("aquarius") || s.includes("водол")) return "♒";
  if (s.includes("pisces") || s.includes("рыб")) return "♓";
  return "✦";
}
