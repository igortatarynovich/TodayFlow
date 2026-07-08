"use client";

import {
  LANDING_HEATMAP_DEMO,
  landingHeatmapCellClass,
} from "@/components/landing/landingContent";
import styles from "@/components/landing/landing.module.css";

type Props = {
  title: string;
  lead: string;
  layers: readonly string[];
};

export function LandingMapsTeaser({ title, lead, layers }: Props) {
  return (
    <section className={styles.insightSection} aria-labelledby="landing-insight-title" data-testid="landing-maps-teaser">
      <h2 id="landing-insight-title" className={styles.insightTitle}>
        {title}
      </h2>
      <p className={styles.insightLead}>{lead}</p>

      <div className={styles.insightVisual}>
        <div className={styles.heatmapPanel} role="img" aria-label="Пример карты настроения и энергии">
          <p className={styles.heatmapLabel}>Карта недели</p>
          <div className={styles.heatmapWrap}>
            <div className={styles.heatmapGrid}>
              {LANDING_HEATMAP_DEMO.flatMap((row, rowIndex) =>
                row.map((cell, colIndex) => (
                  <span
                    key={`${rowIndex}-${colIndex}`}
                    className={`${styles.heatmapCell} ${styles[landingHeatmapCellClass(cell)]}`}
                  />
                )),
              )}
            </div>
          </div>
          <div className={styles.heatmapLegend}>
            <span>тише</span>
            <span className={styles.legendBar} aria-hidden />
            <span>ярче</span>
          </div>
        </div>

        <ul className={styles.mapsLayerList}>
          {layers.map((layer) => (
            <li key={layer} className={styles.mapsLayerChip}>
              {layer}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
