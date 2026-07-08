"use client";

import type { TarotShellStep } from "@/components/shell/tarotShellStepper";
import { TAROT_SHELL_STEPPER } from "@/components/shell/tarotShellStepper";
import s from "@/components/shell/tarotShell.module.css";

export type TarotRailProps = {
  activeStep: TarotShellStep;
  focusTag?: string;
  riskTag?: string;
  practiceTag?: string;
};

export function TarotRail({
  activeStep,
  focusTag = "мягкость",
  riskTag = "контроль",
  practiceTag = "дыхание",
}: TarotRailProps) {
  const activeIndex = activeStep >= 0 ? activeStep : -1;

  return (
    <div className={s.railStack}>
      <section className={s.railPanel} aria-labelledby="tarot-rail-gate">
        <div className={s.railGateOrb} aria-hidden />
        <h2 id="tarot-rail-gate" className={s.railPanelTitle}>
          Ritual gate
        </h2>
        <p className={s.railBody}>
          Перед раскладом система собирает контекст дня: намерение, энергию, личные якоря и
          последний вечерний отклик.
        </p>
      </section>

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

      <section className={s.railPanel} aria-labelledby="tarot-rail-day">
        <h2 id="tarot-rail-day" className={s.railEyebrow}>
          Связи дня
        </h2>
        <ul className={s.railTags}>
          <li>
            <span className={s.railTagLabel}>Фокус</span>
            <span className={s.railTagValue}>{focusTag}</span>
          </li>
          <li>
            <span className={s.railTagLabel}>Риск</span>
            <span className={s.railTagValue}>{riskTag}</span>
          </li>
          <li>
            <span className={s.railTagLabel}>Практика</span>
            <span className={s.railTagValue}>{practiceTag}</span>
          </li>
        </ul>
      </section>
    </div>
  );
}
