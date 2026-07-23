"use client";

import Link from "next/link";
import {
  profileMotionStaggerDelay,
  profileMotionStyles,
  useProfileMotionInView,
} from "@/components/foundation/ProfileMotion";
import { ProfileAtmosphere } from "@/components/profile/v2/ProfileAtmosphere";
import { TodayDayColorGuideSection } from "@/components/today/composition/TodayDayColorGuideSection";
import { TodaySkyStoryCards } from "@/components/today/composition/TodaySkyStoryCards";
import type { TodayPromiseSuggestion } from "@/lib/todayDayDialogue";
import type { TodayContractV1 } from "@/lib/todayContract";
import { isDomainLensPresent } from "@/lib/todayContract";
import type { TodayStrengthenTool } from "@/lib/todayCompositionModel";
import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import type { TodaySkyCard } from "@/lib/todayDaySpine";
import type { TodayDayStoryViewModel } from "@/lib/todayDayStoryModel";
import type { CoreProfile } from "@/lib/types";
import { buildTodayCompatibilityHook } from "@/lib/todayCompatibilityHook";
import { buildTodayLiteraryReading } from "@/lib/todayLiteraryReading";
import { dayStoryAvoidItems, dayStoryDoItems } from "@/lib/todayContractMapper";
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
  skyCards?: TodaySkyCard[];
  colorGuide?: TodayDayColorGuide | null;
  onPickPromise: (text: string) => void;
  onOpenGoalDraft: () => void;
  onGoalDraftChange: (value: string) => void;
  onSaveGoal: () => void;
  onPracticeAction: () => void;
  onAffirmationRead: () => void;
};

const DOMAIN_LABELS: Record<string, string> = {
  relationships: "Отношения",
  money_work: "Работа и деньги",
  family: "Семья и дом",
};

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
  skyCards = [],
  colorGuide = null,
  onPickPromise,
  onOpenGoalDraft,
  onGoalDraftChange,
  onSaveGoal,
  onPracticeAction,
  onAffirmationRead,
}: Props) {
  const compatibility = buildTodayCompatibilityHook(coreProfile);
  const reading = buildTodayLiteraryReading(story, contract);
  const doItems = dayStoryDoItems(contract);
  const avoidItems = dayStoryAvoidItems(contract);
  const talisman = contract.day_story?.talisman;
  const practiceRec = contract.day_story?.practice_recommendation;

  const completedCount = (practiceCompleted ? 1 : 0) + (affirmationRead ? 1 : 0);
  const totalTools = strengthenTools.length;

  const practiceTool = strengthenTools.find((tool) => tool.id === "practice");
  const affirmationTool = strengthenTools.find((tool) => tool.id === "affirmation");
  const otherTools = strengthenTools.filter((tool) => tool.id !== "practice" && tool.id !== "affirmation");

  const themeLine =
    contract.day_story?.theme?.trim() ||
    contract.global_context?.period?.trim() ||
    story.hero.themeHeadline;

  const domainEntries = (["relationships", "money_work", "family"] as const)
    .map((id) => ({ id, lens: contract.domains[id], label: DOMAIN_LABELS[id] }))
    .filter((row) => isDomainLensPresent(row.lens));

  const skyWithoutSymbols = skyCards.filter((c) => c.id !== "tarot" && c.id !== "number");
  const symbolCards = skyCards.filter((c) => c.id === "tarot" || c.id === "number");

  const motion = useProfileMotionInView<HTMLElement>(40);

  return (
    <section
      ref={motion.ref}
      className={`${styles.section} ${embeddedInWebDashboard ? styles.sectionWebEmbed : ""} ${motion.className}`.trim()}
      style={motion.style}
      data-testid="today-zone-personal"
    >
      <div className={styles.journeyScene} data-testid="today-zone-reading">
        <ProfileAtmosphere motif="today" />
        <header className={styles.journeySceneHeader}>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>3</span>
            <span>{copy.journey.readingTitle}</span>
          </p>
          <p className={styles.journeySceneLead}>{copy.journey.readingLead}</p>
        </header>

        <article
          className={`${styles.synthesisCard} ${profileMotionStyles.staggerItem}`}
          style={profileMotionStaggerDelay(0, 60)}
          data-testid="today-entity-synthesis"
        >
          <p className={styles.synthesisKicker}>{themeLine || "Сегодня"}</p>
          {reading.opening ? <p className={styles.synthesisText}>{reading.opening}</p> : null}
          {reading.why ? (
            <p className={styles.softWhy} data-testid="today-soft-why">
              <span className={styles.softWhyLabel}>Почему это важно сегодня</span>
              {reading.why}
            </p>
          ) : null}
        </article>

        {(reading.lean || reading.ease || reading.close) && (
          <div className={styles.attentionGrid} data-testid="today-zone-focus-card">
            {reading.lean ? (
              <article className={styles.attentionCard}>
                <p className={styles.cardEyebrow}>Куда день тянет</p>
                <p className={styles.readingParagraph}>{reading.lean}</p>
              </article>
            ) : null}
            {reading.ease ? (
              <article className={`${styles.attentionCard} ${styles.attentionCardCaution}`}>
                <p className={styles.cardEyebrow}>Где лучше мягче</p>
                <p className={styles.readingParagraph}>{reading.ease}</p>
              </article>
            ) : null}
            {reading.close ? (
              <article className={styles.attentionCard}>
                <p className={styles.cardEyebrow}>Один ход дня</p>
                <p className={`${styles.readingParagraph} ${styles.readingClose}`.trim()}>{reading.close}</p>
              </article>
            ) : null}
          </div>
        )}

        {(doItems.length > 0 || avoidItems.length > 0) && (
          <div className={styles.dualList} data-testid="today-zone-do-avoid">
            {doItems.length ? (
              <article className={styles.productCard}>
                <p className={styles.cardEyebrow}>На что опереться</p>
                <ul className={styles.bulletList}>
                  {doItems.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
            ) : null}
            {avoidItems.length ? (
              <article className={styles.productCard}>
                <p className={styles.cardEyebrow}>Что не дожимать</p>
                <ul className={styles.bulletList}>
                  {avoidItems.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
            ) : null}
          </div>
        )}
      </div>

      {domainEntries.length ? (
        <div className={styles.journeyScene} data-testid="today-zone-domains">
          <ProfileAtmosphere motif="insight" />
          <header className={styles.journeySceneHeader}>
            <p className={styles.journeyStepIndex}>
              <span className={styles.journeyStepBadge}>·</span>
              <span>Сферы сегодня</span>
            </p>
            <p className={styles.journeySceneLead}>Где день сильнее и где лучше не торопиться.</p>
          </header>
          <div className={styles.domainGrid}>
            {domainEntries.map((row) => (
              <article key={row.id} className={styles.domainCard} data-testid={`today-domain-${row.id}`}>
                <p className={styles.cardEyebrow}>{row.label}</p>
                {row.lens.status ? <p className={styles.domainStatus}>{row.lens.status}</p> : null}
                {row.lens.opportunity ? (
                  <p className={styles.domainMeta}>
                    <span>Сильнее:</span> {row.lens.opportunity}
                  </p>
                ) : null}
                {row.lens.risk ? (
                  <p className={styles.domainMeta}>
                    <span>Риск:</span> {row.lens.risk}
                  </p>
                ) : null}
                {row.lens.action ? (
                  <p className={styles.domainAction}>{row.lens.action}</p>
                ) : null}
              </article>
            ))}
          </div>
        </div>
      ) : null}

      {(skyWithoutSymbols.length > 0 || symbolCards.length > 0) && (
        <div className={styles.journeyScene} data-testid="today-zone-sky">
          <ProfileAtmosphere motif="why" />
          <header className={styles.journeySceneHeader}>
            <p className={styles.journeyStepIndex}>
              <span className={styles.journeyStepBadge}>·</span>
              <span>Небо и фон дня</span>
            </p>
            <p className={styles.journeySceneLead}>Почему именно эти акценты сегодня.</p>
          </header>
          {skyWithoutSymbols.length ? <TodaySkyStoryCards cards={skyWithoutSymbols} /> : null}
          {symbolCards.length ? (
            <div className={styles.symbolLayer} data-testid="today-zone-symbols">
              <p className={styles.cardEyebrow}>Слой после ритуала</p>
              <TodaySkyStoryCards cards={symbolCards} />
            </div>
          ) : null}
        </div>
      )}

      {(colorGuide || talisman?.color || talisman?.stone || talisman?.note) && (
        <div className={styles.journeyScene} data-testid="today-zone-talisman">
          <ProfileAtmosphere motif="effort" />
          <header className={styles.journeySceneHeader}>
            <p className={styles.journeyStepIndex}>
              <span className={styles.journeyStepBadge}>·</span>
              <span>Цвет и опора дня</span>
            </p>
            <p className={styles.journeySceneLead}>Что помочь удержать ритм — и почему.</p>
          </header>
          {colorGuide ? <TodayDayColorGuideSection guide={colorGuide} /> : null}
          {(talisman?.stone || talisman?.note) && (
            <article className={styles.productCard}>
              {talisman.stone ? (
                <p className={styles.readingParagraph}>
                  <strong>Камень:</strong> {talisman.stone}
                </p>
              ) : null}
              {talisman.note ? <p className={styles.readingParagraph}>{talisman.note}</p> : null}
            </article>
          )}
        </div>
      )}

      <div className={styles.journeyScene} data-testid="today-zone-move">
        <ProfileAtmosphere motif="effort" />
        <header className={styles.journeySceneHeader}>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>4</span>
            <span>{copy.journey.moveTitle}</span>
          </p>
          <p className={styles.journeySceneLead}>{copy.journey.moveLead}</p>
        </header>

        <article className={styles.productCard} data-testid="today-zone-promise">
          <p className={styles.cardEyebrow}>Цель на сегодня</p>
          {dayGoal && !goalDraftOpen ? (
            <p className={styles.readingParagraph} data-testid="today-promise-active">
              {dayGoal}
            </p>
          ) : null}
          {!dayGoal && promiseSuggestions.length ? (
            <div className={styles.suggestionRow} data-testid="today-promise-suggestions">
              {promiseSuggestions.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={styles.suggestionChip}
                  onClick={() => onPickPromise(item.text)}
                >
                  {item.text}
                </button>
              ))}
            </div>
          ) : null}
          {goalDraftOpen ? (
            <div className={styles.customGoalForm} data-testid="today-entity-daily-goal">
              <input
                id="day-goal-input-product"
                className={styles.goalInput}
                value={goalDraft}
                onChange={(event) => onGoalDraftChange(event.target.value)}
                maxLength={200}
                placeholder="Своими словами — из того, что уже звучит в дне"
              />
              <button type="button" className="orbit-button orbit-button-primary" onClick={onSaveGoal}>
                {copy.goalSave}
              </button>
            </div>
          ) : (
            <button
              type="button"
              className={styles.customGoalRow}
              data-testid="today-zone-promise-open"
              onClick={onOpenGoalDraft}
            >
              {dayGoal ? "Изменить своими словами…" : "+ Своя цель"}
            </button>
          )}
        </article>

        {strengthenTools.length > 0 || practiceRec?.text ? (
          <article className={styles.productCard} data-testid="today-zone-strengthen">
            <div className={styles.practicesHeader}>
              <p className={styles.cardEyebrow}>Практики и опоры</p>
              {totalTools > 1 ? (
                <p className={styles.practicesProgress}>
                  {completedCount} из {totalTools}
                </p>
              ) : null}
            </div>

            {practiceRec?.text && practiceRec.kind === "affirmation" && !affirmationTool ? (
              <div className={styles.practiceRow}>
                <span className={styles.practiceCheck} aria-hidden />
                <div className={styles.practiceBody}>
                  <p className={styles.practiceTitle}>{practiceRec.text}</p>
                  {practiceRec.reason ? <p className={styles.practiceMeta}>{practiceRec.reason}</p> : null}
                </div>
              </div>
            ) : null}

            {practiceTool ? (
              <div className={styles.practiceRow}>
                <span
                  className={practiceCompleted ? styles.practiceCheckDone : styles.practiceCheck}
                  aria-hidden
                />
                <div className={styles.practiceBody}>
                  <p className={styles.practiceTitle}>{practiceTool.title}</p>
                  {practiceTool.duration ? <p className={styles.practiceMeta}>{practiceTool.duration}</p> : null}
                  {practiceRec?.reason && practiceRec.kind === "practice" ? (
                    <p className={styles.practiceMeta}>{practiceRec.reason}</p>
                  ) : null}
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
                  ) : (
                    <p className={styles.practiceMeta}>{copy.practiceCompleted}</p>
                  )}
                </div>
              </div>
            ) : null}

            {affirmationTool ? (
              <div className={styles.practiceRow}>
                <span className={affirmationRead ? styles.practiceCheckDone : styles.practiceCheck} aria-hidden />
                <div className={styles.practiceBody}>
                  <p className={styles.practiceTitle}>{affirmationTool.title}</p>
                  {practiceRec?.reason && practiceRec.kind === "affirmation" ? (
                    <p className={styles.practiceMeta}>{practiceRec.reason}</p>
                  ) : null}
                  {!affirmationRead ? (
                    <button
                      type="button"
                      className={`orbit-button orbit-button-secondary ${styles.practiceAction}`}
                      onClick={onAffirmationRead}
                    >
                      {copy.readAffirmation}
                    </button>
                  ) : null}
                </div>
              </div>
            ) : null}

            {otherTools.map((tool) => (
              <div key={tool.id} className={styles.practiceRow}>
                <span className={styles.practiceCheck} aria-hidden />
                <div className={styles.practiceBody}>
                  <p className={styles.practiceTitle}>{tool.title}</p>
                  {tool.detail ? <p className={styles.practiceMeta}>{tool.detail}</p> : null}
                </div>
              </div>
            ))}
          </article>
        ) : null}
      </div>

      <div className={`${styles.journeyScene} ${styles.bridgeScene}`} data-testid="today-zone-bridges-wrap">
        <ProfileAtmosphere motif="bridge" />
        <header className={styles.journeySceneHeader}>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>5</span>
            <span>{copy.journey.bridgeTitle}</span>
          </p>
          <p className={styles.journeySceneLead}>{copy.journey.bridgeLead}</p>
        </header>
        <nav className={styles.bridges} aria-label="Связанные разделы" data-testid="today-zone-bridges">
          <Link href="/profile" className={styles.bridgeCta}>
            Открыть карту личности
            <span aria-hidden> →</span>
          </Link>
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
      </div>
    </section>
  );
}
