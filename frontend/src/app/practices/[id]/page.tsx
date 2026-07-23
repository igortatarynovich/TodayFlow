"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  practicesExperienceChromeBundle,
  type FlowPracticesChromeLocale,
  type PracticesExperienceChromeBundle,
} from "@/components/today/flowPracticesMainTabChrome";
import { DsButton } from "@/design-system";
import { PracticeSessionWebScreen } from "@/components/product-ui/PracticeSessionWebScreen";
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
  const { isAuthenticated } = useAuth();
  const { refetchToday } = useTodayCycle();
  const toast = useToastContext();
  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const pc = useMemo(() => practicesExperienceChromeBundle(locale), [locale]);

  const [loading, setLoading] = useState(true);
  const [practice, setPractice] = useState<PracticeDetail | null>(null);
  const [isCompleting, setIsCompleting] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
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
      } finally {
        setLoading(false);
      }
    };

    loadPractice();
  }, [params.id, isAuthenticated]);

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

  if (loading) {
    return <PracticeSessionWebScreen backLabel={pc.practiceDetailBackLink} loading />;
  }

  if (!practice) {
    return (
      <PracticeSessionWebScreen backLabel={pc.practiceDetailBackLink}>
        <div className={s.practiceSessionEmpty}>
          <h2 className={s.practiceSessionEmptyTitle}>{pc.practiceDetailNotFoundTitle}</h2>
          <Link href="/practices">
            <DsButton variant="primary">{pc.practiceDetailBackToPracticesCta}</DsButton>
          </Link>
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
    <PracticeSessionWebScreen
      title={practice.title}
      subtitle={practice.personalized_reason?.trim() || practice.description}
      dayWhy={dayWhy}
      meta={sessionMeta}
      backLabel={pc.practiceDetailBackLink}
    >
          <>
            {practice.is_personalized && practice.personalized_reason && !dayWhy && (
              <div className={s.practiceSessionHighlight}>
                <p className={s.practiceSessionHighlightText}>
                  {practice.personalized_reason}
                </p>
              </div>
            )}

            {practice.prompt && (
              <div className={s.practiceSessionHighlight}>
                <h3 className={s.practiceSessionSectionTitle}>
                  {pc.practiceDetailTodaysTaskTitle}
                </h3>
                <p className={s.practiceSessionHighlightText}>
                  {practice.prompt}
                </p>
              </div>
            )}

            {practice.questions && practice.questions.length > 0 && (
              <div style={{ marginBottom: "var(--orbit-space-xl)" }}>
                <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-md)" }}>
                  {pc.practiceDetailReflectionQuestionsTitle}
                </h3>
                <ol style={{ paddingLeft: "var(--orbit-space-lg)", lineHeight: 1.8 }}>
                  {practice.questions.map((question, idx) => (
                    <li key={idx} className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-md)" }}>
                      {question}
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {practice.steps && practice.steps.length > 0 && (
              <div style={{ marginBottom: "var(--orbit-space-xl)" }}>
                <h3 className={s.practiceSessionSectionTitle}>
                  {tpl(pc.practiceDetailSequenceStepsTitle, { count: practice.total_steps || practice.steps.length })}
                </h3>
                <div className={s.practiceSessionStepList}>
                  {practice.steps.map((step) => (
                    <div key={step.step_number} className={s.practiceSessionStepCard}>
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
                  ))}
                </div>
              </div>
            )}

            {practice.instructions && practice.instructions.length > 0 && !practice.steps && (
              <div style={{ marginBottom: "var(--orbit-space-xl)" }}>
                <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-md)" }}>
                  {pc.practiceDetailHowToTitle}
                </h3>
                <ol style={{ paddingLeft: "var(--orbit-space-lg)", lineHeight: 1.8 }}>
                  {practice.instructions.map((instruction, idx) => (
                    <li key={idx} className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-sm)" }}>
                      {instruction}
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {practice.tags && practice.tags.length > 0 && (
              <div className={s.practiceSessionTagRow}>
                  {practice.tags.map((tag) => (
                    <span key={tag} className={s.practiceSessionTag}>
                      {tag}
                    </span>
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

            {isAuthenticated && practice.practice_type !== "guided_sequence" && !isCompleted && (
              <div className={s.practiceSessionActions}>
                <DsButton variant="primary" size="block" onClick={handleCompletePractice} disabled={isCompleting}>
                  {isCompleting ? pc.practiceDetailMarkingShort : pc.practiceDetailMarkCompleteCta}
                </DsButton>
              </div>
            )}

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
  );

  async function handleCompletePractice() {
    if (!practice || !isAuthenticated) return;

    setIsCompleting(true);
    try {
      await postJson(`/practices/${practice.id}/complete`, {});
      setIsCompleted(true);
      await loadRewardsSnapshot();
    } catch (err: unknown) {
      console.error("Error completing practice:", err);
      const anyErr = err as { response?: { data?: { detail?: string } }; message?: string };
      const errorMsg = anyErr?.response?.data?.detail || anyErr?.message || pc.practiceDetailCompleteErrorFallback;
      toast.error(errorMsg);
    } finally {
      setIsCompleting(false);
    }
  }

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
