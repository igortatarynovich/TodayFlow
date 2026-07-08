"use client";

import Link from "next/link";
import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { getJson } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";
import { LoadingSpinner } from "@/components/orbit";
import { t } from "@/lib/i18n";

function BillingSuccessContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams?.get("session_id");
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      const redirectTarget = sessionId ? `/billing/success?session_id=${encodeURIComponent(sessionId)}` : "/billing/success";
      router.replace(`/auth?mode=login&redirect=${encodeURIComponent(redirectTarget)}`);
      return;
    }

    const verifySubscription = async () => {
      try {
        // TODO: Заменить на реальный endpoint для проверки entitlements
        // const entitlements = await getJson("/account/entitlements");
        // if (!entitlements.pro_active) {
        //   // Polling если подписка ещё не активирована
        //   setTimeout(verifySubscription, 2000);
        //   return;
        // }
        
        // Временная заглушка
        setTimeout(() => {
          setLoading(false);
        }, 1000);
      } catch (err) {
        console.error("Failed to verify subscription", err);
        setError("Не удалось проверить статус подписки");
        setLoading(false);
      }
    };

    verifySubscription();
  }, [authLoading, isAuthenticated, router, sessionId]);

  if (loading) {
    return (
      <main className="orbit-page" style={{ background: "#FAF9F7" }}>
        <div style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "60vh",
          gap: "var(--orbit-space-lg)"
        }}>
          <LoadingSpinner size="lg" />
          <p className="orbit-body" style={{ color: "#334155" }}>
            Активация доступа...
          </p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="orbit-page" style={{ background: "#FAF9F7" }}>
        <div style={{
          maxWidth: "600px",
          margin: "0 auto",
          padding: "var(--orbit-space-4xl) var(--orbit-space-xl)",
          textAlign: "center"
        }}>
          <h1 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-lg)" }}>
            Ошибка
          </h1>
          <p className="orbit-body" style={{ color: "#334155", marginBottom: "var(--orbit-space-xl)" }}>
            {error}
          </p>
          <Link
            href="/account/subscriptions"
            className="orbit-button orbit-button-primary"
            style={{
              textDecoration: "none",
              display: "inline-block"
            }}
          >
            Перейти в аккаунт
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="orbit-page" style={{ background: "#FAF9F7" }}>
      <section style={{
        paddingTop: "var(--orbit-space-4xl)",
        paddingBottom: "var(--orbit-space-4xl)",
        textAlign: "center"
      }}>
        <div style={{
          maxWidth: "600px",
          margin: "0 auto",
          padding: "0 var(--orbit-space-xl)"
        }}>
          <div style={{
            fontSize: "4rem",
            marginBottom: "var(--orbit-space-lg)",
            lineHeight: 1
          }}>
            ✅
          </div>
          <h1 className="orbit-display" style={{
            fontSize: "clamp(2rem, 4vw, 3rem)",
            lineHeight: 1.2,
            marginBottom: "var(--orbit-space-lg)",
            color: "#0f172a",
            fontWeight: 500
          }}>
            Доступ активирован!
          </h1>
          <p className="orbit-body" style={{
            fontSize: "1.125rem",
            lineHeight: 1.7,
            marginBottom: "var(--orbit-space-2xl)",
            color: "#334155"
          }}>
            Твоя подписка успешно активирована. Теперь у тебя есть доступ ко всем функциям приложения.
          </p>

          <div style={{
            display: "flex",
            flexDirection: "column",
            gap: "var(--orbit-space-lg)",
            maxWidth: "400px",
            margin: "0 auto"
          }}>
            <Link
              href="/account/subscriptions"
              className="orbit-button orbit-button-primary"
              style={{
                fontSize: "1.125rem",
                padding: "var(--orbit-space-lg) var(--orbit-space-2xl)",
                textDecoration: "none",
                display: "inline-block",
                textAlign: "center"
              }}
            >
              Перейти в аккаунт
            </Link>

            <Link
              href="/today"
              className="orbit-button orbit-button-secondary"
              style={{
                fontSize: "1rem",
                padding: "var(--orbit-space-md) var(--orbit-space-xl)",
                textDecoration: "none",
                display: "inline-block",
                textAlign: "center"
              }}
            >
              Открыть в приложении
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}

export default function BillingSuccessPage() {
  return (
    <Suspense fallback={
      <main className="orbit-page" style={{ background: "#FAF9F7" }}>
        <div style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "var(--orbit-space-lg)",
          padding: "var(--orbit-space-4xl)"
        }}>
          <LoadingSpinner size="lg" />
          <p className="orbit-body">Активируем ваш доступ...</p>
        </div>
      </main>
    }>
      <BillingSuccessContent />
    </Suspense>
  );
}
