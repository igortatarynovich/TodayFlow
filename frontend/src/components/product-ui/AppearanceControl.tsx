"use client";

import {
  type ProductAppearanceMode,
} from "@/lib/productAppearance";
import { useProductMoodTheme } from "@/lib/useProductDayNightTheme";
import styles from "@/components/product-ui/MoodThemeControl.module.css";

type Props = {
  className?: string;
};

const LABELS: Record<ProductAppearanceMode, string> = {
  system: "Авто",
  light: "Светлая",
  dark: "Тёмная",
};

/**
 * Appearance (light/dark) — independent of mood pin.
 * Does not change day-phase photography.
 */
export function AppearanceControl({ className }: Props) {
  const { appearanceMode, setAppearanceMode } = useProductMoodTheme();

  return (
    <div
      className={`${styles.root} ${className ?? ""}`.trim()}
      data-testid="appearance-control"
      role="group"
      aria-label="Оформление"
    >
      <span className={styles.label}>Оформление</span>
      <div className={styles.row}>
        {(Object.keys(LABELS) as ProductAppearanceMode[]).map((mode) => {
          const active = appearanceMode === mode;
          return (
            <button
              key={mode}
              type="button"
              className={`${styles.chip} ${active ? styles.chipActive : ""}`}
              data-appearance-chip={mode}
              aria-pressed={active}
              onClick={() => setAppearanceMode(mode)}
            >
              {LABELS[mode]}
            </button>
          );
        })}
      </div>
    </div>
  );
}
