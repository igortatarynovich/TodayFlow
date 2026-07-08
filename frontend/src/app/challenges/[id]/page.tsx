"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { buildAuthHref } from "@/lib/authRedirect";
import { useAuth } from "@/lib/useAuth";
import { LoadingSpinner } from "@/components/orbit";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { DsButton } from "@/design-system";
import { getJson, postJson } from "@/lib/api";
import type { AccountProfile } from "@/lib/types";
import { useToast } from "@/components/ToastProvider";

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
        <section className={pl.panel} style={{ textAlign: "center" }}>
          <Link href="/challenges">
            <DsButton variant="primary">Вернуться к списку марафонов</DsButton>
          </Link>
        </section>
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
        <p className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-lg)" }}>
          <Link href="/challenges" style={{ color: "var(--orbit-color-slate)", textDecoration: "none" }}>
            ← Вернуться к марафонам
          </Link>
        </p>

        {challenge.is_pro_only && (
          <span
            style={{
              display: "inline-block",
              background: "var(--orbit-color-lock)",
              color: "var(--orbit-color-page)",
              padding: "4px 8px",
              borderRadius: "var(--orbit-radius-sm)",
              fontSize: "0.75rem",
              fontWeight: 600,
              textTransform: "uppercase",
              marginBottom: "var(--orbit-space-lg)",
            }}
          >
            PRO
          </span>
        )}

        <div
          className={pl.grid2}
          style={{ marginBottom: "var(--orbit-space-xl)" }}
        >
          <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
            <div className="orbit-body-xs orbit-text-muted" style={{ marginBottom: "var(--orbit-space-xs)" }}>
              Длительность
            </div>
            <div className="orbit-body" style={{ fontWeight: 600 }}>
              {challenge.duration} дней
            </div>
          </div>
          <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
            <div className="orbit-body-xs orbit-text-muted" style={{ marginBottom: "var(--orbit-space-xs)" }}>
              Цель
            </div>
            <div className="orbit-body" style={{ fontWeight: 600 }}>
              {challenge.goal}
            </div>
          </div>
          {challenge.price !== null && (
            <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
              <div className="orbit-body-xs orbit-text-muted" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                Стоимость
              </div>
              <div className="orbit-body" style={{ fontWeight: 600 }}>
                {challenge.price / 100} ₽
              </div>
            </div>
          )}
        </div>

        {isParticipating && (
          <div style={{ marginBottom: "var(--orbit-space-xl)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "var(--orbit-space-xs)" }}>
              <span className="orbit-body-sm" style={{ fontWeight: 600 }}>
                День {participation.current_day} из {challenge.duration}
              </span>
              <span className="orbit-body-sm orbit-text-muted">{progress}%</span>
            </div>
            <div
              style={{
                width: "100%",
                height: "8px",
                background: "var(--orbit-color-mist)",
                borderRadius: "var(--orbit-radius-sm)",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${progress}%`,
                  height: "100%",
                  background: "var(--orbit-color-primary)",
                  transition: "width 0.3s ease",
                }}
              />
            </div>
          </div>
        )}

        <div style={{ display: "flex", gap: "var(--orbit-space-md)", flexWrap: "wrap", marginBottom: "var(--orbit-space-xl)" }}>
          {!isAuthenticated ? (
            <Link href="/auth" className="orbit-button orbit-button-primary">
              Зарегистрироваться для участия
            </Link>
          ) : isParticipating ? (
            <>
              <button onClick={handleLeave} className="orbit-button orbit-button-secondary">
                Покинуть марафон
              </button>
              <div className="orbit-card" style={{ padding: "var(--orbit-space-md)", flex: 1 }}>
                <p className="orbit-body-sm" style={{ margin: 0, color: "var(--orbit-color-success)" }}>
                  ✓ Вы участвуете в этом марафоне
                </p>
              </div>
            </>
          ) : isAvailable ? (
            <button
              onClick={handleJoin}
              className="orbit-button orbit-button-primary"
              disabled={joining}
              style={{ minWidth: "200px" }}
            >
              {joining ? (
                <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "var(--orbit-space-xs)" }}>
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
            </button>
          ) : (
            <Link href="/pricing" className="orbit-button orbit-button-secondary">
              Требуется Pro подписка
            </Link>
          )}
        </div>
      </div>

      {isParticipating && participation && (
        <section
          style={{
            opacity: showContent ? 1 : 0,
            transform: showContent ? "translateY(0)" : "translateY(20px)",
            transition: "opacity 0.8s ease 0.2s, transform 0.8s ease 0.2s",
          }}
        >
          <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-xl)" }}>
            Задания дня {participation.current_day}
          </h2>

          {tasks.length === 0 ? (
            <div className="orbit-card" style={{ padding: "var(--orbit-space-xl)" }}>
              <p className="orbit-body" style={{ color: "var(--orbit-color-slate)", textAlign: "center" }}>
                Задания для этого дня пока не добавлены.
              </p>
            </div>
          ) : (
            <div style={{ display: "grid", gap: "var(--orbit-space-lg)" }}>
              {tasks.map((task, index) => (
                <div
                  key={task.id}
                  className="orbit-card"
                  style={{
                    padding: "var(--orbit-space-xl)",
                    border: task.is_completed
                      ? "2px solid var(--orbit-color-success)"
                      : "1px solid var(--orbit-color-border)",
                    background: task.is_completed
                      ? "linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.02))"
                      : "var(--orbit-color-card)",
                    opacity: showContent ? 1 : 0,
                    transform: showContent ? "translateY(0)" : "translateY(20px)",
                    transition: `opacity 0.8s ease ${0.3 + index * 0.1}s, transform 0.8s ease ${0.3 + index * 0.1}s`,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "var(--orbit-space-md)" }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "var(--orbit-space-sm)", marginBottom: "var(--orbit-space-sm)" }}>
                        {task.is_completed && <span style={{ fontSize: "1.5rem" }}>✓</span>}
                        <h3 className="orbit-body" style={{ fontWeight: 600, margin: 0 }}>
                          {task.title}
                        </h3>
                        {task.task_type && (
                          <span
                            style={{
                              fontSize: "0.75rem",
                              padding: "2px 8px",
                              borderRadius: "var(--orbit-radius-sm)",
                              background: "var(--orbit-color-mist)",
                              color: "var(--orbit-color-slate)",
                              textTransform: "capitalize",
                            }}
                          >
                            {task.task_type === "reflection" ? "Размышление" :
                             task.task_type === "action" ? "Действие" :
                             task.task_type === "journal" ? "Дневник" :
                             task.task_type === "meditation" ? "Медитация" :
                             task.task_type}
                          </span>
                        )}
                      </div>
                      <p className="orbit-body-sm" style={{ color: "var(--orbit-color-slate)", lineHeight: 1.6 }}>
                        {task.description}
                      </p>
                    </div>
                    {!task.is_completed && (
                      <button
                        onClick={() => handleCompleteTask(task.id)}
                        className="orbit-button orbit-button-primary"
                        disabled={completingTask === task.id}
                        style={{ minWidth: "120px", flexShrink: 0 }}
                      >
                        {completingTask === task.id ? (
                          <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "var(--orbit-space-xs)" }}>
                            <LoadingSpinner size="sm" />
                          </span>
                        ) : (
                          "Выполнено"
                        )}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}
    </ProductPageScreen>
  );
}
