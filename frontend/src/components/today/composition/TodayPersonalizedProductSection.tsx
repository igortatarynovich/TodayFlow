"use client";

import Link from "next/link";
import type { TodayPromiseSuggestion } from "@/lib/todayDayDialogue";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { TodayStrengthenTool } from "@/lib/todayCompositionModel";
import type { TodayDayStoryViewModel } from "@/lib/todayDayStoryModel";
import type { CoreProfile } from "@/lib/types";
import { buildTodayCompatibilityHook } from "@/lib/todayCompatibilityHook";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import styles from "@/components/today/composition/TodayPersonalizedProductSection.module.css";

type Props = {
  story: TodayDayStoryViewModel;
  contract: TodayContractV1;
  strengthenTools: TodayStrengthenTool[];
  promiseSuggestions: TodayPromiseSuggestion[];
  dayGoal: string | null;
  practiceCompleted: boolean;
  practiceStarted: boolean;
  affirmationRead: boolean;
  practiceCompleting: boolean;
  goalDraftOpen: boolean;
  goalDraft: string;
  coreProfile?: CoreProfile | null;
  tarotDeepenHref?: string | null;
  embeddedInWebDashboard?: boolean;
  onPickPromise: (text: string) => void;
  onOpenGoalDraft: () => void;
  onGoalDraftChange: (value: string) => void;
  onSaveGoal: () => void;
  onPracticeAction: () => void;
  onAffirmationRead: () => void;
};

function firstSentence(text: string): string {
  const trimmed = text.trim();
  if (!trimmed) return "";
  const match = trimmed.match(/^[^.!?]+[.!?]?/);
  return (match?.[0] ?? trimmed).trim();
}

function buildShouldLines(story: TodayDayStoryViewModel, contract: TodayContractV1): string[] {
  const peak = story.sphereFocus.cards.find((card) => card.role === "peak");
  const lines: string[] = [];
  if (peak?.body) {
    lines.push(firstSentence(peak.body));
  }
  for (const domain of ["relationships", "money_work", "family"] as const) {
    const opportunity = contract.domains[domain].opportunity?.trim();
    if (opportunity && lines.length < 2 && !lines.some((line) => line.includes(opportunity))) {
      lines.push(opportunity.charAt(0).toUpperCase() + opportunity.slice(1));
    }
  }
  return lines.slice(0, 2).map((line) => (line.startsWith("→") ? line : `→ ${line}`));
}

function buildAvoidLines(story: TodayDayStoryViewModel, contract: TodayContractV1): string[] {
  const caution = story.sphereFocus.cards.find((card) => card.role === "caution");
  if (caution?.releaseLine) return [`→ ${caution.releaseLine}`];
  if (caution?.body) return [`→ ${firstSentence(caution.body)}`];
  for (const domain of ["relationships", "money_work", "family"] as const) {
    const risk = contract.domains[domain].risk?.trim();
    if (risk) return [`→ ${risk.charAt(0).toUpperCase() + risk.slice(1)}`];
  }
  return [];
}

export function TodayPersonalizedProductSection({
  story,
  contract,
  strengthenTools,
  promiseSuggestions,
  dayGoal,
  practiceCompleted,
  practiceStarted,
  affirmationRead,
  practiceCompleting,
  goalDraftOpen,
  goalDraft,
  coreProfile,
  tarotDeepenHref,
  embeddedInWebDashboard = false,
  onPickPromise,
  onOpenGoalDraft,
  onGoalDraftChange,
  onSaveGoal,
  onPracticeAction,
  onAffirmationRead,
}: Props) {
  const compatibility = buildTodayCompatibilityHook(coreProfile);
  const shouldLines = buildShouldLines(story, contract);
  const avoidLines = buildAvoidLines(story, contract);
  const focusTitle =
    story.sphereFocus.cards.find((card) => card.role === "peak")?.headline ?? story.hero.themeHeadline;

  const synthesisTags = [
    story.tarotImpact ? { id: "tarot", label: story.tarotImpact.title } : null,
    story.skyCards[0] ? { id: story.skyCards[0].id, label: story.skyCards[0].title } : null,
    story.numberImpact ? { id: "number", label: story.numberImpact.title } : null,
  ].filter(Boolean) as Array<{ id: string; label: string }>;

  const completedCount = (practiceCompleted ? 1 : 0) + (affirmationRead ? 1 : 0);
  const totalTools = strengthenTools.length;

  const practiceTool = strengthenTools.find((tool) => tool.id === "practice");
  const affirmationTool = strengthenTools.find((tool) => tool.id === "affirmation");
  const otherTools = strengthenTools.filter((tool) => tool.id !== "practice" && tool.id !== "affirmation");

  return (
    <section
      className={`${styles.section} ${embeddedInWebDashboard ? styles.sectionWebEmbed : ""}`.trim()}
      data-testid="today-zone-personal"
    >
      <article className={styles.synthesisCard} data-testid="today-entity-synthesis">
        <div>
          <p className={styles.synthesisKicker}>Твой день сформирован</p>
          <p className={styles.synthesisText}>{story.pulse}</p>
        </div>
        {synthesisTags.length > 0 ? (
          <div className={styles.synthesisTags}>
            {synthesisTags.map((tag) => (
              <span key={tag.id} className={styles.synthesisTag}>
                {tag.label}
              </span>
            ))}
          </div>
        ) : null}
      </article>

      {(story.glance.supported.length > 0 || story.glance.helpful.length > 0) && (
        <div className={styles.glanceRow} data-testid="today-zone-glance-personal">
          {story.glance.supported[0] ? (
            <article className={styles.glanceTile}>
              <p className={styles.glanceTileLabel}>Поддержано</p>
              <p className={styles.glanceTileValue}>{story.glance.supported[0].sphere}</p>
            </article>
          ) : null}
          {story.glance.helpful[0] ? (
            <article className={styles.glanceTile}>
              <p className={styles.glanceTileLabel}>Требует внимания</p>
              <p className={styles.glanceTileValue}>{story.glance.helpful[0].sphere}</p>
            </article>
          ) : null}
        </div>
      )}

      <article className={styles.productCard} data-testid="today-zone-focus-card">
        <p className={styles.cardEyebrow}>Фокус дня</p>
        <h2 className={styles.cardTitle}>{focusTitle}</h2>
        <div className={styles.focusGroups}>
          {shouldLines.length > 0 ? (
            <div>
              <p className={styles.focusGroupLabel}>Стоит:</p>
              {shouldLines.map((line) => (
                <p key={line} className={styles.focusLine}>
                  {line}
                </p>
              ))}
            </div>
          ) : null}
          {avoidLines.length > 0 ? (
            <div>
              <p className={styles.focusGroupLabel}>Лучше избегать:</p>
              {avoidLines.map((line) => (
                <p key={line} className={styles.focusLine}>
                  {line}
                </p>
              ))}
            </div>
          ) : null}
        </div>
        <div className={styles.cardDivider} />
        <p className={styles.cardEyebrow}>Главный шаг</p>
        <p className={styles.mainStepText}>{contract.primary_action}</p>
      </article>

      <article className={styles.productCard} data-testid="today-zone-promise">
        <p className={styles.cardEyebrow}>Намерение дня</p>
        <div className={styles.chipRow}>
          {promiseSuggestions.map((suggestion) => (
            <button
              key={suggestion.id}
              type="button"
              className={dayGoal === suggestion.text ? styles.chipActive : styles.chip}
              data-testid={`today-promise-${suggestion.id}`}
              onClick={() => onPickPromise(suggestion.text)}
            >
              {suggestion.text}
            </button>
          ))}
        </div>
        {goalDraftOpen ? (
          <div className={styles.customGoalForm} data-testid="today-entity-daily-goal">
            <input
              id="day-goal-input-product"
              className={styles.goalInput}
              value={goalDraft}
              onChange={(event) => onGoalDraftChange(event.target.value)}
              maxLength={200}
              placeholder={copy.goalPrompt}
            />
            <button type="button" className="orbit-button orbit-button-primary" onClick={onSaveGoal}>
              {copy.goalSave}
            </button>
          </div>
        ) : (
          <button type="button" className={styles.customGoalRow} onClick={onOpenGoalDraft}>
            + Своя цель…
          </button>
        )}
      </article>

      {strengthenTools.length > 0 ? (
        <article className={styles.productCard} data-testid="today-zone-strengthen">
          <div className={styles.practicesHeader}>
            <p className={styles.cardEyebrow}>На сегодня</p>
            <p className={styles.practicesProgress}>
              {completedCount} из {totalTools}
            </p>
          </div>

          {practiceTool ? (
            <>
              <div className={styles.practiceRow}>
                <span
                  className={practiceCompleted ? styles.practiceCheckDone : styles.practiceCheck}
                  aria-hidden
                />
                <div className={styles.practiceBody}>
                  <p className={styles.practiceTitle}>{practiceTool.title}</p>
                  {practiceTool.duration ? <p className={styles.practiceMeta}>{practiceTool.duration}</p> : null}
                  {!practiceCompleted ? (
                    <button
                      type="button"
                      className={`orbit-button orbit-button-secondary ${styles.practiceAction}`}
                      data-testid="today-tool-practice"
                      disabled={practiceCompleting}
                      onClick={() => void onPracticeAction()}
                    >
                      {practiceStarted ? copy.practiceComplete : copy.practiceStart}
                    </button>
                  ) : null}
                </div>
              </div>
              {otherTools.length > 0 || affirmationTool ? <div className={styles.practiceRowDivider} /> : null}
            </>
          ) : null}

          {otherTools.map((tool, index) => (
            <div key={tool.id}>
              <div className={styles.practiceRow}>
                <span className={styles.practiceCheck} aria-hidden />
                <div className={styles.practiceBody}>
                  <p className={styles.practiceTitle}>{tool.title}</p>
                  {tool.duration ? <p className={styles.practiceMetaMuted}>{tool.duration}</p> : null}
                </div>
              </div>
              {index < otherTools.length - 1 || affirmationTool ? (
                <div className={styles.practiceRowDivider} />
              ) : null}
            </div>
          ))}

          {affirmationTool ? (
            <div className={styles.practiceRow}>
              <span className={affirmationRead ? styles.practiceCheckDone : styles.practiceCheck} aria-hidden />
              <div className={styles.practiceBody}>
                <p className={styles.practiceQuote}>{affirmationTool.title}</p>
                {!affirmationRead ? (
                  <button
                    type="button"
                    className={`orbit-button orbit-button-secondary ${styles.practiceAction}`}
                    data-testid="today-tool-affirmation"
                    onClick={onAffirmationRead}
                  >
                    {copy.readAffirmation}
                  </button>
                ) : null}
              </div>
            </div>
          ) : null}
        </article>
      ) : null}

      <nav className={styles.bridges} aria-label="Связанные разделы" data-testid="today-zone-bridges">
        <Link href={compatibility.href} className={styles.bridgeLink}>
          → {compatibility.hasSavedPerson ? "Совместимость с партнёром" : "Проверить совместимость"}
        </Link>
        {tarotDeepenHref ? (
          <Link href={tarotDeepenHref} className={styles.bridgeLink} data-testid="today-tarot-deepen">
            → Исследовать тему: Таро
          </Link>
        ) : (
          <Link href="/tarot" className={styles.bridgeLink}>
            → Исследовать тему: Таро
          </Link>
        )}
      </nav>
    </section>
  );
}
