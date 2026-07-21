"use client";

import type { TarotShellStep } from "@/components/shell/tarotShellStepper";
import { TAROT_SHELL_STEPPER } from "@/components/shell/tarotShellStepper";
import s from "@/components/shell/tarotShell.module.css";

export type TarotRailProps = {
  activeStep: TarotShellStep;
  /** Only pass when sourced from real day context — never invent defaults. */
  focusTag?: string | null;
  riskTag?: string | null;
  practiceTag?: string | null;
};

export function TarotRail({
  activeStep,
  focusTag = null,
  riskTag = null,
  practiceTag = null,
}: TarotRailProps) {
  // Hub (/tarot): no rail content until the user starts a spread.
  if (activeStep < 0) {
    return null;
  }

  const activeIndex = activeStep;
  const dayTags = [
    focusTag?.trim() ? { label: "Фокус", value: focusTag.trim() } : null,
    riskTag?.trim() ? { label: "Риск", value: riskTag.trim() } : null,
    practiceTag?.trim() ? { label: "Практика", value: practiceTag.trim() } : null,
  ].filter((item): item is { label: string; value: string } => Boolean(item));

  return (
    <div className={s.railStack}>
      <section className={s.railPanel} aria-labelledby="tarot-rail-path">
        <h2 id="tarot-rail-path" className={s.railEyebrow}>
          Путь расклада
        </h2>
        <ol className={s.railStepper}>
          {TAROT_SHELL_STEPPER.map((step, index) => {
            const isActive = index === activeIndex;
            return (
              <li
                key={step.id}
                className={`${s.railStep} ${isActive ? s.railStepActive : ""}`.trim()}
              >
                <span className={s.railStepBadge}>{step.id}</span>
                <div className={s.railStepCopy}>
                  <p className={s.railStepTitle}>{step.title}</p>
                  <p className={s.railStepHint}>{step.hint}</p>
                </div>
              </li>
            );
          })}
        </ol>
      </section>

      {dayTags.length > 0 ? (
        <section className={s.railPanel} aria-labelledby="tarot-rail-day">
          <h2 id="tarot-rail-day" className={s.railEyebrow}>
            Связи дня
          </h2>
          <ul className={s.railTags}>
            {dayTags.map((tag) => (
              <li key={tag.label}>
                <span className={s.railTagLabel}>{tag.label}</span>
                <span className={s.railTagValue}>{tag.value}</span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}
