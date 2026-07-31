"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import {
  practicesExperienceChromeBundle,
  type FlowPracticesChromeLocale,
  type PracticesExperienceChromeBundle,
} from "@/components/today/flowPracticesMainTabChrome";
import { DsButton, MotionReveal, MotionSettle } from "@/design-system";
import { MOTION } from "@/design-system/motion/tokens";
import { PracticeSessionWebScreen } from "@/components/product-ui/PracticeSessionWebScreen";
import { PracticeLiveSession } from "@/components/practices/session/PracticeLiveSession";
import { practiceSessionCopy } from "@/components/practices/session/practiceSessionCopy";
import s from "@/components/product-ui/productWebScreens.module.css";
import { useToastContext } from "@/components/ToastProvider";
import { getJson, postJson } from "@/lib/api";
import { getLocale } from "@/lib/i18n";
import { fetchTodayContractV1 } from "@/lib/todayContract";
import type { RewardMilestone, RewardsSnapshot } from "@/lib/rewards";
import { RewardsContourCard } from "@/components/rewards/RewardsContourCard";
import { useTodayCycle } from "@/components/providers/TodayCycleProvider";
import { useAuth } from "@/lib/useAuth";
import { GuestAccessLimitGate } from "@/components/guest/GuestAccessLimitGate";
import { GUEST_ACCESS_COPY } from "@/components/guest/guestAccessCopy";
import { isGuestPracticeAllowed } from "@/lib/guestAccessStore";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import {
  clearPracticeSessionDraft,
  readPracticeSessionDraft,
  type PracticeStateAfter,
} from "@/lib/practicesPage/practiceSessionDraft";

function tpl(s: string, vars: Record<string, string | number>) {
  return s.replace(/\{\{(\w+)\}\}/g, (_, k) => String(vars[k] ?? ""));
}

function patternAxisLabel(fc: PracticesExperienceChromeBundle, axisId: string): string {
  const map: Record<string, string> = {
    A1: fc.practicePatternAxisA1,
    A2: fc.practicePatternAxisA2,
    A3: fc.practicePatternAxisA3,
    A4: fc.practicePatternAxisA4,
    A5: fc.practicePatternAxisA5,
    A6: fc.practicePatternAxisA6,
    A7: fc.practicePatternAxisA7,
  };
  return map[axisId] ?? axisId;
}

function difficultyLabel(difficulty: string, pc: PracticesExperienceChromeBundle): string {
  if (difficulty === "beginner") return pc.practicesCatalogDifficultyBeginner;
  if (difficulty === "intermediate") return pc.practicesCatalogDifficultyIntermediate;
  return pc.practicesCatalogDifficultyAdvanced;
}

type PracticeStep = {
  step_number: number;
  title: string;
  description: string;
  duration_minutes?: number;
  instructions: string[];
  questions?: string[];
};

type PracticeDetail = {
  id: string;
  title: string;
  description: string;
  category: string;
  practice_type?: string;
  duration_minutes?: number;
  difficulty: string;
  is_free: boolean;
  is_personalized: boolean;
  personalized_reason?: string;
  access_level: string;
  tags: string[];
  instructions: string[];
  prompt?: string;
  questions?: string[];
  steps?: PracticeStep[];
  sequence_id?: string;
  step_number?: number;
  total_steps?: number;
  audio_url?: string;
  related_practices: string[];
  target_axis?: string;
};

export default function PracticeDetailPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated } = useAuth();
  const { refetchToday } = useTodayCycle();
  const { trackMeaningEvent } = useMeaningRuntime();
  const toast = useToastContext();
  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const pc = useMemo(() => practicesExperienceChromeBundle(locale), [locale]);
  const sessionCopy = useMemo(() => practiceSessionCopy(locale), [locale]);

  const [loading, setLoading] = useState(true);
  const [practice, setPractice] = useState<PracticeDetail | null>(null);
  const [loadError, setLoadError] = useState<"not_found" | "transport" | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [isCompleting, setIsCompleting] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [sessionOpen, setSessionOpen] = useState(false);
  const [sessionSaving, setSessionSaving] = useState(false);
  const [sequenceProgress, setSequenceProgress] = useState<{
    completed_steps: number;
    total_steps: number;
    current_step: number | null;
    is_completed: boolean;
  } | null>(null);
  const [rewardsAfterCompletion, setRewardsAfterCompletion] = useState<RewardsSnapshot | null>(null);
  const [rewardMilestones, setRewardMilestones] = useState<RewardMilestone[]>([]);
  const [dayWhy, setDayWhy] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      setDayWhy(null);
      return;
    }
    let cancelled = false;
    void fetchTodayContractV1()
      .then((contract) => {
        if (cancelled) return;
        const rec = contract.day_story?.practice_recommendation;
        const kind = (rec?.kind || "").trim().toLowerCase();
        const reason = (rec?.reason || "").trim();
        if (!kind || kind === "none" || !reason) {
          setDayWhy(null);
          return;
        }
        setDayWhy(reason);
      })
      .catch(() => {
        if (!cancelled) setDayWhy(null);
      });
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated]);

  useEffect(() => {
    const loadPractice = async () => {
      setLoading(true);
      setLoadError(null);
      try {
        const practiceId = params.id as string;
        const data = await getJson<PracticeDetail>(`/practices/${practiceId}`);
        setPractice(data);

        if (isAuthenticated && data.sequence_id) {
          try {
            const progress = await getJson<{
              completed_steps: number;
              total_steps: number;
              current_step: number | null;
              is_completed: boolean;
            }>(`/practices/sequences/${data.sequence_id}/progress`);
            setSequenceProgress(progress);
          } catch (err) {
            console.error("Error loading sequence progress:", err);
          }
        }
      } catch (err) {
        console.error("Error loading practice:", err);
        setPractice(null);
        const status = err && typeof err === "object" && "status" in err ? Number((err as { status: number }).status) : NaN;
        setLoadError(status === 404 ? "not_found" : "transport");
      } finally {
        setLoading(false);
      }
    };

    void loadPractice();
  }, [params.id, isAuthenticated, reloadKey]);

  const sessionMeta = useMemo(() => {
    if (!practice) return [];
    const items = [
      practice.duration_minutes
        ? {
            label: pc.practiceDetailMetaDuration,
            value: tpl(pc.practiceDetailDurationValue, { n: practice.duration_minutes }),
          }
        : null,
      {
        label: pc.practiceDetailMetaLevel,
        value: difficultyLabel(practice.difficulty, pc),
      },
      {
        label: pc.practiceDetailMetaAccess,
        value: practice.is_free ? pc.practiceDetailAccessFree : pc.practiceDetailAccessSubscription,
        tone: practice.is_free ? ("success" as const) : ("accent" as const),
      },
    ];
    return items.filter((item): item is NonNullable<typeof item> => item !== null);
  }, [practice, pc]);

  const draftElapsed = useMemo(() => {
    if (!practice) return 0;
    const draft = readPracticeSessionDraft();
    if (!draft || draft.practiceId !== practice.id) return 0;
    return draft.elapsedSeconds;
  }, [practice, sessionOpen]);

  useEffect(() => {
    if (!practice) return;
    if (searchParams.get("run") === "1") {
      setSessionOpen(true);
    }
  }, [practice, searchParams]);

  const closeSession = useCallback(() => {
    setSessionOpen(false);
    if (searchParams.get("run") === "1") {
      router.replace(`/practices/${practice?.id ?? ""}`);
    }
  }, [router, searchParams, practice?.id]);

  const handleSaveSessionToToday = useCallback(
    async (input: { stateAfter: PracticeStateAfter; elapsedSeconds: number }) => {
      if (!practice || !isAuthenticated) return;
      setSessionSaving(true);
      try {
        await postJson(`/practices/${practice.id}/complete`, {
          state_after: input.stateAfter,
          elapsed_seconds: input.elapsedSeconds,
          surface: "practices_session_p1",
        });
        const localDate = new Date().toISOString().slice(0, 10);
        trackMeaningEvent({
          event_type: "practice_completed",
          event_source: "today",
          local_date: localDate,
          payload: {
            practice_id: practice.id,
            duration_minutes: practice.duration_minutes ?? null,
            elapsed_seconds: input.elapsedSeconds,
            state_after: input.stateAfter,
            surface: "practices_session_p1",
          },
          refreshRings: true,
        });
        setIsCompleted(true);
        clearPracticeSessionDraft(practice.id);
        const data = await refetchToday({ force: true });
        setRewardsAfterCompletion(data?.rewards ?? null);
        setRewardMilestones(Array.isArray(data?.reward_milestones) ? data.reward_milestones : []);
      } catch (err: unknown) {
        console.error("Error saving practice session:", err);
        const anyErr = err as { response?: { data?: { detail?: string } }; message?: string };
        const errorMsg =
          anyErr?.response?.data?.detail || anyErr?.message || pc.practiceDetailCompleteErrorFallback;
        toast.error(errorMsg);
        throw err;
      } finally {
        setSessionSaving(false);
      }
    },
    [
      practice,
      isAuthenticated,
      trackMeaningEvent,
      refetchToday,
      pc.practiceDetailCompleteErrorFallback,
      toast,
    ],
  );

  if (loading) {
    return <PracticeSessionWebScreen backLabel={pc.practiceDetailBackLink} loading />;
  }

  if (!practice) {
    const isTransport = loadError === "transport";
    return (
      <PracticeSessionWebScreen backLabel={pc.practiceDetailBackLink}>
        <div className={s.practiceSessionEmpty}>
          <h2 className={s.practiceSessionEmptyTitle}>
            {isTransport ? pc.practiceDetailLoadFailedTitle : pc.practiceDetailNotFoundTitle}
          </h2>
          {isTransport ? (
            <DsButton variant="primary" onClick={() => setReloadKey((k) => k + 1)}>
              {pc.practiceDetailLoadFailedRetry}
            </DsButton>
          ) : (
            <Link href="/practices">
              <DsButton variant="primary">{pc.practiceDetailBackToPracticesCta}</DsButton>
            </Link>
          )}
        </div>
      </PracticeSessionWebScreen>
    );
  }

  if (!isAuthenticated && practice && !isGuestPracticeAllowed(practice)) {
    return (
      <PracticeSessionWebScreen
        title={practice.title}
        subtitle={practice.description}
        backLabel={pc.practiceDetailBackLink}
      >
        <GuestAccessLimitGate
          title={GUEST_ACCESS_COPY.practiceLockedTitle}
          body={GUEST_ACCESS_COPY.practiceLockedBody}
          secondaryHref="/practices"
          secondaryLabel={pc.practiceDetailBackToPracticesCta}
          testId="guest-practice-locked"
        />
      </PracticeSessionWebScreen>
    );
  }

  if (!isAuthenticated && !practice.is_free) {
    return (
      <PracticeSessionWebScreen
        title={practice.title}
        subtitle={practice.description}
        backLabel={pc.practiceDetailBackLink}
      >
        <div className={s.practiceSessionEmpty}>
          <h2 className={s.practiceSessionEmptyTitle}>{pc.practiceDetailAuthOnlyTitle}</h2>
          <Link href="/onboarding/welcome?fresh=1">
            <DsButton variant="primary">{pc.practiceDetailSignUpCta}</DsButton>
          </Link>
        </div>
      </PracticeSessionWebScreen>
    );
  }

  return (
    <>
      {sessionOpen && practice ? (
        <PracticeLiveSession
          locale={locale}
          practiceId={practice.id}
          title={practice.title}
          instruction={
            practice.instructions?.[0]?.trim() ||
            practice.prompt?.trim() ||
            practice.description
          }
          durationMinutes={practice.duration_minutes && practice.duration_minutes > 0 ? practice.duration_minutes : 5}
          initialElapsedSeconds={draftElapsed}
          audioUrl={practice.audio_url ?? null}
          imageUrl="/images/praktiki_banner.png"
          isAuthenticated={isAuthenticated}
          saving={sessionSaving}
          onClose={closeSession}
          onSaveToToday={handleSaveSessionToToday}
        />
      ) : null}
      <PracticeSessionWebScreen
        title={practice.title}
        subtitle={practice.personalized_reason?.trim() || practice.description}
        dayWhy={dayWhy}
        meta={sessionMeta}
        backLabel={pc.practiceDetailBackLink}
      >
          <>
            {!isCompleted ? (
              <div className={s.practiceSessionActions}>
                <DsButton
                  variant="primary"
                  size="block"
                  onClick={() => setSessionOpen(true)}
                  data-testid="practice-start-session"
                >
                  {draftElapsed > 0 ? sessionCopy.resumeCta : sessionCopy.startCta}
                </DsButton>
              </div>
            ) : null}

            {practice.is_personalized && practice.personalized_reason && !dayWhy && (
              <MotionReveal className={s.practiceSessionHighlight}>
                <p className={s.practiceSessionHighlightText}>
                  {practice.personalized_reason}
                </p>
              </MotionReveal>
            )}

            {practice.prompt && (
              <MotionReveal className={s.practiceSessionHighlight} delayMs={MOTION.staggerMs}>
                <h3 className={s.practiceSessionSectionTitle}>
                  {pc.practiceDetailTodaysTaskTitle}
                </h3>
                <p className={s.practiceSessionHighlightText}>
                  {practice.prompt}
                </p>
              </MotionReveal>
            )}

            {practice.questions && practice.questions.length > 0 && (
              <MotionReveal delayMs={MOTION.staggerMs * 2}>
                <div style={{ marginBottom: "var(--orbit-space-xl)" }}>
                  <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-md)" }}>
                    {pc.practiceDetailReflectionQuestionsTitle}
                  </h3>
                  <ol style={{ paddingLeft: "var(--orbit-space-lg)", lineHeight: 1.8 }}>
                    {practice.questions.map((question, idx) => (
                      <li key={idx} className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-md)" }}>
                        <MotionSettle delayMs={idx * MOTION.staggerMs}>{question}</MotionSettle>
                      </li>
                    ))}
                  </ol>
                </div>
              </MotionReveal>
            )}

            {practice.steps && practice.steps.length > 0 && (
              <MotionReveal delayMs={MOTION.staggerMs}>
                <div style={{ marginBottom: "var(--orbit-space-xl)" }}>
                  <h3 className={s.practiceSessionSectionTitle}>
                    {tpl(pc.practiceDetailSequenceStepsTitle, { count: practice.total_steps || practice.steps.length })}
                  </h3>
                  <div className={s.practiceSessionStepList}>
                    {practice.steps.map((step, index) => (
                      <MotionSettle key={step.step_number} delayMs={index * MOTION.staggerMs}>
                        <div className={s.practiceSessionStepCard}>
                          <div className={s.practiceSessionStepHead}>
                            <div className={s.practiceSessionStepBadge}>
                              {step.step_number}
                            </div>
                            <div style={{ flex: 1 }}>
                              <h4 className={s.practiceSessionStepTitle}>
                                {step.title}
                              </h4>
                              <p className={s.practiceSessionStepBody}>
                                {step.description}
                              </p>
                              {step.duration_minutes && (
                                <p className="orbit-body-xs orbit-text-muted" style={{ marginBottom: "var(--orbit-space-sm)" }}>
                                  {tpl(pc.practiceDetailStepDurationValue, { n: step.duration_minutes })}
                                </p>
                              )}
                              {step.instructions && step.instructions.length > 0 && (
                                <ol style={{ paddingLeft: "var(--orbit-space-md)", marginTop: "var(--orbit-space-sm)", lineHeight: 1.7 }}>
                                  {step.instructions.map((instruction, idx) => (
                                    <li key={idx} className="orbit-body-sm" style={{ marginBottom: "4px" }}>
                                      {instruction}
                                    </li>
                                  ))}
                                </ol>
                              )}
                              {step.questions && step.questions.length > 0 && (
                                <div style={{ marginTop: "var(--orbit-space-sm)" }}>
                                  <p className="orbit-body-xs orbit-text-muted" style={{ marginBottom: "4px", fontWeight: 600 }}>
                                    {pc.practiceDetailStepQuestionsLabel}
                                  </p>
                                  <ul style={{ paddingLeft: "var(--orbit-space-md)", lineHeight: 1.7 }}>
                                    {step.questions.map((question, idx) => (
                                      <li key={idx} className="orbit-body-sm" style={{ marginBottom: "4px" }}>
                                        {question}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </MotionSettle>
                    ))}
                  </div>
                </div>
              </MotionReveal>
            )}

            {practice.instructions && practice.instructions.length > 0 && !practice.steps && (
              <MotionReveal delayMs={MOTION.staggerMs}>
                <div style={{ marginBottom: "var(--orbit-space-xl)" }}>
                  <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-md)" }}>
                    {pc.practiceDetailHowToTitle}
                  </h3>
                  <ol style={{ paddingLeft: "var(--orbit-space-lg)", lineHeight: 1.8 }}>
                    {practice.instructions.map((instruction, idx) => (
                      <li key={idx} className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-sm)" }}>
                        <MotionSettle delayMs={idx * MOTION.staggerMs}>{instruction}</MotionSettle>
                      </li>
                    ))}
                  </ol>
                </div>
              </MotionReveal>
            )}

            {practice.tags && practice.tags.length > 0 && (
              <div className={s.practiceSessionTagRow}>
                {practice.tags.map((tag, index) => (
                  <MotionSettle key={tag} delayMs={index * MOTION.staggerMs}>
                    <span className={s.practiceSessionTag}>{tag}</span>
                  </MotionSettle>
                ))}
              </div>
            )}

            {practice.audio_url && (
              <div style={{ marginBottom: "var(--orbit-space-xl)" }}>
                <audio controls style={{ width: "100%" }}>
                  <source src={practice.audio_url} type="audio/mpeg" />
                  {pc.practiceDetailAudioUnsupported}
                </audio>
              </div>
            )}

            {practice.sequence_id && sequenceProgress && (
              <div className={s.practiceSessionProgress}>
                <h3 className={s.practiceSessionSectionTitle}>
                  {pc.practiceDetailSequenceProgressHeading}
                </h3>
                <div style={{ marginBottom: "var(--orbit-space-md)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--orbit-space-xs)" }}>
                    <span className="orbit-body-sm">{pc.stepsDoneLabel}</span>
                    <span className="orbit-body-sm" style={{ fontWeight: 600 }}>
                      {sequenceProgress.completed_steps} / {sequenceProgress.total_steps}
                    </span>
                  </div>
                  <div className={s.practiceSessionProgressBar}>
                    <div
                      className={s.practiceSessionProgressFill}
                      style={{
                        width: `${(sequenceProgress.completed_steps / sequenceProgress.total_steps) * 100}%`,
                      }}
                    />
                  </div>
                </div>
                {sequenceProgress.current_step && !sequenceProgress.is_completed && (
                  <p className="orbit-body-sm orbit-text-muted">
                    {pc.practiceDetailNextStepPrefix} {sequenceProgress.current_step}
                  </p>
                )}
                {sequenceProgress.is_completed && (
                  <p className="orbit-body-sm" style={{ color: "var(--orbit-color-success)", fontWeight: 600 }}>
                    {pc.practiceDetailSequenceDoneShort}
                  </p>
                )}
              </div>
            )}

            {/* P1: completion only via session check-in (Start/Resume above) — no mark-done bypass. */}

            {isCompleted && practice.target_axis && (
              <div style={{
                marginTop: "var(--orbit-space-xl)",
                paddingTop: "var(--orbit-space-xl)",
                borderTop: "2px solid var(--orbit-color-highlight)"
              }}>
                <div className="orbit-card" style={{
                  padding: "var(--orbit-space-xl)",
                  background: "rgba(212, 175, 55, 0.05)",
                  border: "1px solid rgba(212, 175, 55, 0.2)"
                }}>
                  <p className="orbit-body" style={{
                    marginBottom: "var(--orbit-space-lg)",
                    lineHeight: 1.6
                  }}>
                    {pc.practiceDetailCompletionWorkedPattern}{" "}
                    <Link
                      href={`/discover/pattern/${practice.target_axis}`}
                      className="orbit-link"
                      style={{ fontWeight: 600 }}
                    >
                      {patternAxisLabel(pc, practice.target_axis)}
                    </Link>
                    .
                  </p>

                  <div style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "var(--orbit-space-md)"
                  }}>
                    <Link
                      href="/journal"
                      className="orbit-button orbit-button-primary"
                      style={{ width: "100%" }}
                    >
                      {pc.practiceDetailJournalFixFeelingCta}
                    </Link>
                    <Link
                      href={`/discover/pattern/${practice.target_axis}`}
                      className="orbit-button orbit-button-secondary"
                      style={{ width: "100%" }}
                    >
                      {pc.practiceDetailPatternExploreCta}
                    </Link>
                  </div>

                  {rewardsAfterCompletion && (
                    <div style={{ marginTop: "var(--orbit-space-lg)" }}>
                      <RewardsContourCard rewards={rewardsAfterCompletion} milestones={rewardMilestones || []} compact />
                    </div>
                  )}
                </div>
              </div>
            )}

            {isCompleted && !practice.target_axis && (
              <div style={{
                marginTop: "var(--orbit-space-xl)",
                paddingTop: "var(--orbit-space-xl)",
                borderTop: "1px solid var(--orbit-color-border)"
              }}>
                <div className="orbit-card" style={{
                  padding: "var(--orbit-space-lg)",
                  background: "var(--orbit-color-mist)"
                }}>
                  <p className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-md)" }}>
                    {pc.practiceDetailCompletedFallbackBody}
                  </p>
                  {rewardsAfterCompletion && (
                    <div style={{ marginBottom: "var(--orbit-space-md)" }}>
                      <RewardsContourCard rewards={rewardsAfterCompletion} milestones={rewardMilestones || []} compact />
                    </div>
                  )}
                  <Link
                    href="/profile"
                    className="orbit-button orbit-button-secondary"
                    style={{ width: "100%" }}
                  >
                    {pc.practiceDetailOpenProfileRewardsCta}
                  </Link>
                </div>
              </div>
            )}

            {isAuthenticated && practice.sequence_id && sequenceProgress && sequenceProgress.current_step && !sequenceProgress.is_completed && (
              <div className={s.practiceSessionActions}>
                <DsButton
                  variant="primary"
                  size="block"
                  onClick={() => handleCompleteSequenceStep(sequenceProgress.current_step!)}
                  disabled={isCompleting}
                >
                  {isCompleting ? pc.practiceDetailMarkingShort : tpl(pc.practiceDetailCompleteStepCta, { n: sequenceProgress.current_step })}
                </DsButton>
              </div>
            )}
          </>
    </PracticeSessionWebScreen>
    </>
  );

  async function loadRewardsSnapshot() {
    if (!isAuthenticated) return;
    const data = await refetchToday({ force: true });
    setRewardsAfterCompletion(data?.rewards ?? null);
    setRewardMilestones(Array.isArray(data?.reward_milestones) ? data.reward_milestones : []);
  }

  async function handleCompleteSequenceStep(stepNumber: number) {
    if (!practice?.sequence_id || !isAuthenticated) return;

    setIsCompleting(true);
    try {
      await postJson(`/practices/sequences/${practice.sequence_id}/steps/${stepNumber}/complete`, {});
      toast.success(tpl(pc.practiceDetailStepDoneToast, { n: stepNumber }));
      await loadRewardsSnapshot();

      try {
        const progress = await getJson<{
          completed_steps: number;
          total_steps: number;
          current_step: number | null;
          is_completed: boolean;
        }>(`/practices/sequences/${practice.sequence_id}/progress`);
        setSequenceProgress(progress);
      } catch (err) {
        console.error("Error loading updated progress:", err);
      }
    } catch (err: unknown) {
      console.error("Error completing sequence step:", err);
      const anyErr = err as { response?: { data?: { detail?: string } }; message?: string };
      const errorMsg = anyErr?.response?.data?.detail || anyErr?.message || pc.practiceDetailStepCompleteErrorFallback;
      toast.error(errorMsg);
    } finally {
      setIsCompleting(false);
    }
  }
}
