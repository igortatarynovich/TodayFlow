"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import { CrossSectionLinks } from "@/components/CrossSectionLinks";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import { LoadingSpinner } from "@/components/orbit";
import { getJson, postJson } from "@/lib/api";
import { t } from "@/lib/i18n";
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

export default function ChallengesPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const toast = useToast();
  const [isPro, setIsPro] = useState(false);
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState<string | null>(null);

  useEffect(() => {
    fetchChallenges();
    if (isAuthenticated) {
      checkProStatus();
    }
  }, [isAuthenticated]);

  const fetchChallenges = async () => {
    try {
      setLoading(true);
      const data = await getJson<Challenge[]>("/challenges");
      setChallenges(data);
    } catch (err) {
      console.error("Error fetching challenges:", err);
    } finally {
      setLoading(false);
    }
  };

  const checkProStatus = async () => {
    try {
      const profile = await getJson<AccountProfile>("/auth/me");
      setIsPro(profile.is_paid || false);
    } catch (err) {
      console.error("Error checking Pro status:", err);
    }
  };

  const handleJoin = async (challengeId: string) => {
    if (!isAuthenticated) {
      window.location.href = "/auth";
      return;
    }

    try {
      setJoining(challengeId);
      await postJson(`/challenges/${challengeId}/join`, {});
      window.location.href = `/challenges/${challengeId}`;
    } catch (err: any) {
      console.error("Error joining challenge:", err);
      if (err.status === 403) {
        toast.error(t("challenges.errors.proOnly", "Этот марафон доступен только для Pro подписки"));
      } else if (err.status === 400) {
        toast.error(t("challenges.errors.alreadyJoined", "Вы уже участвуете в этом марафоне"));
      } else {
        toast.error(t("challenges.errors.joinFailed", "Ошибка при присоединении к марафону"));
      }
    } finally {
      setJoining(null);
    }
  };

  if (authLoading || loading) {
    return (
      <ProductPageScreen
        testId="challenges-page"
        title="Марафоны и челленджи"
        loading
        loadingLabel="Загрузка марафонов…"
      />
    );
  }

  return (
    <ProductPageScreen
      testId="challenges-page"
      eyebrow="TodayFlow"
      title="Марафоны и челленджи"
      subtitle="Структурированные программы для развития осознанности и личностного роста"
    >
      <div className={c.grid}>
        {challenges.map((challenge) => {
          const isAvailable = !challenge.is_pro_only || isPro;
          const isFree = challenge.price === null && isPro;
          const locked = challenge.is_pro_only && !isPro;
          const priceInRubles = challenge.price ? Math.round(challenge.price / 100) : null;

          return (
            <Link
              key={challenge.id}
              href={`/challenges/${challenge.id}`}
              className={`${c.card} ${locked ? c.cardLocked : ""}`}
            >
              {locked && <span className={c.proBadge}>PRO</span>}

              <div className={c.icon}>{challenge.icon || "🎯"}</div>

              <h3 className={c.title}>{challenge.title}</h3>
              <p className={c.body}>{challenge.description}</p>

              <div className={c.meta}>
                <div className={c.metaRow}>
                  <span className={c.metaLabel}>Длительность</span>
                  <span className={c.metaValue}>{challenge.duration} дней</span>
                </div>
                <div className={c.metaRow}>
                  <span className={c.metaLabel}>Цель</span>
                  <span className={c.metaValue}>{challenge.goal}</span>
                </div>
              </div>

              <div className={c.action}>
                {isAvailable ? (
                  <button
                    type="button"
                    className={`${c.cta} ${c.ctaPrimary}`}
                    disabled={joining === challenge.id}
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      handleJoin(challenge.id);
                    }}
                  >
                    {joining === challenge.id ? (
                      <span className={c.ctaInline}>
                        <LoadingSpinner size="sm" />
                        Присоединение…
                      </span>
                    ) : isFree ? (
                      t("challenges.startFree", "Начать бесплатно")
                    ) : priceInRubles ? (
                      `${t("challenges.joinFor", "Присоединиться за")} ${priceInRubles} ₽`
                    ) : (
                      t("challenges.join", "Присоединиться")
                    )}
                  </button>
                ) : (
                  <button
                    type="button"
                    className={`${c.cta} ${c.ctaSecondary}`}
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      window.location.href = "/pricing";
                    }}
                  >
                    Требуется Pro подписка
                  </button>
                )}
              </div>
            </Link>
          );
        })}
      </div>

      {!isAuthenticated && (
        <section className={c.joinPanel}>
          <h3 className={c.joinTitle}>Присоединяйся к марафонам</h3>
          <p className={c.joinBody}>
            Зарегистрируйся, чтобы участвовать в марафонах и отслеживать свой прогресс.
          </p>
          <Link href="/auth" className={`${c.cta} ${c.ctaPrimary}`} style={{ width: "auto", paddingInline: "2rem" }}>
            Начать
          </Link>
        </section>
      )}

      {isAuthenticated && (
        <CrossSectionLinks currentSection="challenges" title={t("challenges.sections.title", "Связанные разделы")} />
      )}
    </ProductPageScreen>
  );
}
