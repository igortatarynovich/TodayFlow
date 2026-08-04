"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { buildAuthHref } from "@/lib/authRedirect";
import { useAuth } from "@/lib/useAuth";
import { LoadingSpinner } from "@/components/orbit";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { DsBody, DsButton, DsCard, DsPill, DsTitle } from "@/design-system";
import { getJson, postJson } from "@/lib/api";
import type { AccountProfile } from "@/lib/types";
import { useToast } from "@/components/ToastProvider";
import c from "./challenges.module.css";

type Challenge = {
  id: string;
  title: string;
  description: string;
  duration: number;
  goal: string;
  price: number | null;
  is_pro_only: boolean;
  icon: string | null;
  color: string | null;
  is_active: boolean;
};

type ChallengeParticipant = {
  id: number;
  challenge_id: string;
  started_at: string;
  completed_at: string | null;
  current_day: number;
  is_active: boolean;
};

type ChallengeTask = {
  id: number;
  challenge_id: string;
  day_number: number;
  title: string;
  description: string;
  task_type: string;
  order: number;
  is_completed?: boolean;
};

export default function ChallengeDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const toast = useToast();
  const [showContent, setShowContent] = useState(false);
  const [isPro, setIsPro] = useState(false);
  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [participation, setParticipation] = useState<ChallengeParticipant | null>(null);
  const [tasks, setTasks] = useState<ChallengeTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState(false);
  const [completingTask, setCompletingTask] = useState<number | null>(null);

  const fetchTasks = useCallback(async (participationId: number) => {
    try {
      const data = await getJson<ChallengeTask[]>(`/challenges/my/participations/${participationId}/tasks`);
      setTasks(data);
    } catch (err) {
      console.error("Error fetching tasks:", err);
    }
  }, []);

  const fetchChallenge = useCallback(async (challengeId: string) => {
    try {
      setLoading(true);
      const data = await getJson<Challenge>(`/challenges/${challengeId}`);
      setChallenge(data);
    } catch (err: any) {
      console.error("Error fetching challenge:", err);
      if (err.status === 404) {
        router.push("/challenges");
      } else if (err.status === 403) {
        toast.error("Этот марафон доступен только для Pro подписки");
        router.push("/challenges");
      }
    } finally {
      setLoading(false);
    }
  }, [router, toast]);

  const checkProStatus = useCallback(async () => {
    try {
      const profile = await getJson<AccountProfile>("/auth/me");
      setIsPro(profile.is_paid || false);
    } catch (err) {
      console.error("Error checking Pro status:", err);
    }
  }, []);

  const fetchParticipation = useCallback(async (challengeId: string) => {
    try {
      const participations = await getJson<ChallengeParticipant[]>("/challenges/my/participations");
      const myParticipation = participations.find((p) => p.challenge_id === challengeId && p.is_active);
      setParticipation(myParticipation || null);

      if (myParticipation) {
        await fetchTasks(myParticipation.id);
      }
    } catch (err) {
      console.error("Error fetching participation:", err);
    }
  }, [fetchTasks]);

  useEffect(() => {
    setShowContent(true);
    if (id && typeof id === "string") {
      fetchChallenge(id);
      if (isAuthenticated) {
        checkProStatus();
        fetchParticipation(id);
      }
    }
  }, [id, isAuthenticated, fetchChallenge, checkProStatus, fetchParticipation]);

  const handleCompleteTask = async (taskId: number) => {
    if (!participation) return;

    try {
      setCompletingTask(taskId);
      await postJson(`/challenges/tasks/${taskId}/complete`, {});
      await fetchTasks(participation.id);
    } catch (err: any) {
      console.error("Error completing task:", err);
      if (err.status === 400) {
        toast.info("Задание уже выполнено");
      } else {
        toast.error("Ошибка при выполнении задания");
      }
    } finally {
      setCompletingTask(null);
    }
  };

  const handleJoin = async () => {
    if (!isAuthenticated) {
      router.push(buildAuthHref("login", challenge ? `/challenges/${challenge.id}` : "/challenges"));
      return;
    }

    if (!challenge) return;

    try {
      setJoining(true);
      await postJson(`/challenges/${challenge.id}/join`, {});
      await fetchParticipation(challenge.id);
    } catch (err: any) {
      console.error("Error joining challenge:", err);
      if (err.status === 403) {
        toast.error("Этот марафон доступен только для Pro подписки");
      } else if (err.status === 400) {
        toast.info("Вы уже участвуете в этом марафоне");
      } else {
        toast.error("Ошибка при присоединении к марафону");
      }
    } finally {
      setJoining(false);
    }
  };

  const handleLeave = async () => {
    if (!challenge) return;

    try {
      await postJson(`/challenges/${challenge.id}/leave`, {});
      setParticipation(null);
      router.push("/challenges");
    } catch (err) {
      console.error("Error leaving challenge:", err);
      toast.error("Ошибка при выходе из марафона");
    }
  };

  if (authLoading || loading) {
    return (
      <ProductPageScreen
        testId="challenge-detail-page"
        title="Марафон"
        loading
        loadingLabel="Загрузка марафона…"
      />
    );
  }

  if (!challenge) {
    return (
      <ProductPageScreen
        testId="challenge-detail-page"
        title="Марафон не найден"
        subtitle="Марафон с таким ID не существует или был удалён."
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
        <DsCard variant="outline" className={c.joinShell}>
          <DsButton variant="primary" href="/challenges">
            Вернуться к списку марафонов
          </DsButton>
        </DsCard>
      </ProductPageScreen>
    );
  }

  const isAvailable = !challenge.is_pro_only || isPro;
  const isParticipating = participation !== null;
  const progress = isParticipating ? Math.round((participation.current_day / challenge.duration) * 100) : 0;

  return (
    <ProductPageScreen
      testId="challenge-detail-page"
      title={`${challenge.icon ?? ""} ${challenge.title}`.trim()}
      subtitle={challenge.description}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <div
        style={{
          opacity: showContent ? 1 : 0,
          transform: showContent ? "translateY(0)" : "translateY(20px)",
          transition: "opacity 0.8s ease, transform 0.8s ease",
        }}
      >
        <p className={c.backRow}>
          <DsButton variant="ghost" size="sm" href="/challenges">
            ← Вернуться к марафонам
          </DsButton>
        </p>

        {challenge.is_pro_only ? (
          <div className={c.proWrap}>
            <DsPill>PRO</DsPill>
          </div>
        ) : null}

        <div className={`${pl.grid2} ${c.statGrid}`}>
          <DsCard variant="elevated" size="compact" className={c.statShell}>
            <DsBody muted>Длительность</DsBody>
            <DsTitle as="h3">{challenge.duration} дней</DsTitle>
          </DsCard>
          <DsCard variant="elevated" size="compact" className={c.statShell}>
            <DsBody muted>Цель</DsBody>
            <DsTitle as="h3">{challenge.goal}</DsTitle>
          </DsCard>
          {challenge.price !== null ? (
            <DsCard variant="elevated" size="compact" className={c.statShell}>
              <DsBody muted>Стоимость</DsBody>
              <DsTitle as="h3">{challenge.price / 100} ₽</DsTitle>
            </DsCard>
          ) : null}
        </div>

        {isParticipating ? (
          <div className={c.progressBlock}>
            <div className={c.progressMeta}>
              <span>
                День {participation.current_day} из {challenge.duration}
              </span>
              <span>{progress}%</span>
            </div>
            <div className={c.progressTrack}>
              <div className={c.progressFill} style={{ width: `${progress}%` }} />
            </div>
          </div>
        ) : null}

        <div className={c.actionRow}>
          {!isAuthenticated ? (
            <DsButton variant="primary" href="/onboarding/welcome?fresh=1">
              Зарегистрироваться для участия
            </DsButton>
          ) : isParticipating ? (
            <>
              <DsButton variant="secondary" onClick={handleLeave}>
                Покинуть марафон
              </DsButton>
              <DsCard variant="outline" size="compact" className={c.statusShell}>
                <DsBody>✓ Вы участвуете в этом марафоне</DsBody>
              </DsCard>
            </>
          ) : isAvailable ? (
            <DsButton variant="primary" onClick={handleJoin} disabled={joining}>
              {joining ? (
                <span className={c.actionInline}>
                  <LoadingSpinner size="sm" />
                  Присоединение...
                </span>
              ) : challenge.price === null && isPro ? (
                "Начать бесплатно"
              ) : challenge.price ? (
                `Присоединиться за ${challenge.price / 100} ₽`
              ) : (
                "Присоединиться"
              )}
            </DsButton>
          ) : (
            <DsButton variant="secondary" href="/pricing">
              Требуется Pro подписка
            </DsButton>
          )}
        </div>
      </div>

      {isParticipating && participation ? (
        <section
          style={{
            opacity: showContent ? 1 : 0,
            transform: showContent ? "translateY(0)" : "translateY(20px)",
            transition: "opacity 0.8s ease 0.2s, transform 0.8s ease 0.2s",
          }}
        >
          <DsTitle as="h2">Задания дня {participation.current_day}</DsTitle>

          {tasks.length === 0 ? (
            <DsCard variant="outline" className={c.statShell}>
              <DsBody muted>Задания для этого дня пока не добавлены.</DsBody>
            </DsCard>
          ) : (
            <div className={c.taskStack}>
              {tasks.map((task, index) => (
                <div
                  key={task.id}
                  style={{
                    opacity: showContent ? 1 : 0,
                    transform: showContent ? "translateY(0)" : "translateY(20px)",
                    transition: `opacity 0.8s ease ${0.3 + index * 0.1}s, transform 0.8s ease ${0.3 + index * 0.1}s`,
                  }}
                >
                  <DsCard
                    variant="elevated"
                    className={`${c.taskShell} ${task.is_completed ? c.taskShellDone : ""}`}
                  >
                    <div className={c.taskRow}>
                      <div style={{ flex: 1 }}>
                        <div
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "0.5rem",
                            marginBottom: "0.5rem",
                            flexWrap: "wrap",
                          }}
                        >
                          {task.is_completed ? <span aria-hidden>✓</span> : null}
                          <DsTitle as="h3">{task.title}</DsTitle>
                          {task.task_type ? (
                            <span className={c.taskType}>
                              {task.task_type === "reflection"
                                ? "Размышление"
                                : task.task_type === "action"
                                  ? "Действие"
                                  : task.task_type === "journal"
                                    ? "Дневник"
                                    : task.task_type === "meditation"
                                      ? "Медитация"
                                      : task.task_type}
                            </span>
                          ) : null}
                        </div>
                        <DsBody muted>{task.description}</DsBody>
                      </div>
                      {!task.is_completed ? (
                        <DsButton
                          variant="primary"
                          onClick={() => handleCompleteTask(task.id)}
                          disabled={completingTask === task.id}
                        >
                          {completingTask === task.id ? <LoadingSpinner size="sm" /> : "Выполнено"}
                        </DsButton>
                      ) : null}
                    </div>
                  </DsCard>
                </div>
              ))}
            </div>
          )}
        </section>
      ) : null}
    </ProductPageScreen>
  );
}
