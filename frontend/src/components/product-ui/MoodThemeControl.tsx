"use client";

import {
  PRODUCT_MOOD_LABELS_RU,
  PRODUCT_MOODS,
  type ProductMood,
} from "@/lib/productMoodTheme";
import { useProductMoodTheme } from "@/lib/useProductDayNightTheme";
import styles from "@/components/product-ui/MoodThemeControl.module.css";

type Props = {
  isFirstDay?: boolean;
  className?: string;
};

/**
 * Ritual mood pin (FOUNDATION_UI §8) — not a settings toggle.
 * Tap a mood to pin; tap active pin again to return to auto (clock/first-day).
 */
export function MoodThemeControl({ isFirstDay = false, className }: Props) {
  const { mood, pinned, pinMood, clearPin } = useProductMoodTheme({ isFirstDay });

  return (
    <div
      className={`${styles.root} ${className ?? ""}`.trim()}
      data-testid="mood-theme-control"
      role="group"
      aria-label="Настроение"
    >
      <span className={styles.label}>{pinned ? "Закреплено" : "По моменту"}</span>
      <div className={styles.row}>
        {PRODUCT_MOODS.map((id) => {
          const active = mood === id;
          return (
            <button
              key={id}
              type="button"
              className={`${styles.chip} ${active ? styles.chipActive : ""}`}
              data-mood-chip={id}
              aria-pressed={active && pinned}
              onClick={() => {
                if (pinned && mood === id) clearPin();
                else pinMood(id as ProductMood);
              }}
            >
              {PRODUCT_MOOD_LABELS_RU[id]}
            </button>
          );
        })}
      </div>
    </div>
  );
}
