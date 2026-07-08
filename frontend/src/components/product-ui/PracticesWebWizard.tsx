"use client";

import s from "@/components/product-ui/productWebScreens.module.css";

export type PracticesWizardStepId = "goal" | "direction" | "practice";

export type PracticesWizardStepDef = {
  id: PracticesWizardStepId;
  label: string;
};

export type PracticesGoalOption = {
  id: string;
  icon: string;
  name: string;
  description: string;
};

export type PracticesWebWizardStepsProps = {
  steps: PracticesWizardStepDef[];
  activeStep: PracticesWizardStepId;
  stepsAriaLabel: string;
};

export function PracticesWebWizardSteps({ steps, activeStep, stepsAriaLabel }: PracticesWebWizardStepsProps) {
  return (
    <div className={s.practicesWizardSteps} role="list" aria-label={stepsAriaLabel}>
      {steps.map((step) => (
        <span
          key={step.id}
          role="listitem"
          className={`${s.practicesWizardStep} ${activeStep === step.id ? s.practicesWizardStepActive : ""}`}
        >
          {step.label}
        </span>
      ))}
    </div>
  );
}

export type PracticesWebGoalStepProps = {
  prompt: string;
  categories: PracticesGoalOption[];
  onSelect: (goalId: string) => void;
};

export function PracticesWebGoalStep({ prompt, categories, onSelect }: PracticesWebGoalStepProps) {
  return (
    <section className={s.practicesWizardSection} aria-labelledby="practices-goal-heading">
      <h2 id="practices-goal-heading" className={s.practicesWizardPrompt}>
        {prompt}
      </h2>
      <div className={s.practicesGoalGrid}>
        {categories.map((category) => (
          <button
            key={category.id}
            type="button"
            className={s.practicesGoalCard}
            onClick={() => onSelect(category.id)}
          >
            <span className={s.practicesGoalIcon} aria-hidden>
              {category.icon}
            </span>
            <h3 className={s.practicesGoalTitle}>{category.name}</h3>
            <p className={s.practicesGoalBody}>{category.description}</p>
          </button>
        ))}
      </div>
    </section>
  );
}

export type PracticesWebDirectionStepProps = {
  backLabel: string;
  heading: string;
  goal: PracticesGoalOption;
  directions: string[];
  directionLabel: (direction: string) => string;
  onBack: () => void;
  onSelect: (direction: string) => void;
};

export function PracticesWebDirectionStep({
  backLabel,
  heading,
  goal,
  directions,
  directionLabel,
  onBack,
  onSelect,
}: PracticesWebDirectionStepProps) {
  return (
    <section className={s.practicesWizardSection} aria-labelledby="practices-direction-heading">
      <div className={s.practicesWizardToolbar}>
        <button type="button" className={s.practicesWizardBack} onClick={onBack}>
          ← {backLabel}
        </button>
        <h2 id="practices-direction-heading" className={s.practicesWizardHeading}>
          {heading}
        </h2>
      </div>

      <div className={s.practicesSelectedGoalCard}>
        <div className={s.practicesSelectedGoalHead}>
          <span className={s.practicesGoalIcon} aria-hidden>
            {goal.icon}
          </span>
          <h3 className={s.practicesGoalTitle}>{goal.name}</h3>
        </div>
        <p className={s.practicesGoalBody}>{goal.description}</p>
      </div>

      <div className={s.practicesDirectionGrid}>
        {directions.map((direction) => (
          <button
            key={direction}
            type="button"
            className={s.practicesDirectionCard}
            onClick={() => onSelect(direction)}
          >
            {directionLabel(direction)}
          </button>
        ))}
      </div>
    </section>
  );
}
