"use client";

import { useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import { LoadingSpinner } from "@/components/orbit";

function CheckoutContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const planId = searchParams?.get("plan") || "";

  useEffect(() => {
    const createCheckout = async () => {
      if (!isAuthenticated) {
        router.push(`/signup?redirect=${encodeURIComponent(`/checkout?plan=${planId}`)}`);
        return;
      }

      if (!planId) {
        router.push("/pricing");
        return;
      }

      try {
        // TODO: Заменить на реальный endpoint
        // const response = await postJson<{ url: string }>("/subscriptions/create-checkout", {
        //   plan_id: planId,
        // });
        // window.location.href = response.url;

        // Stripe пока отключен в текущей ветке. Возвращаем пользователя на тарифы
        // с понятным уведомлением вместо "тихого" no-op.
        router.push(`/pricing?notice=checkout_unavailable&plan=${encodeURIComponent(planId)}`);
      } catch (error) {
        console.error("Failed to create checkout session", error);
        router.push("/pricing?error=checkout_failed");
      }
    };

    createCheckout();
  }, [planId, isAuthenticated, router]);

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
          Перенаправление на оплату...
        </p>
      </div>
    </main>
  );
}

export default function CheckoutPage() {
  return (
    <Suspense fallback={
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
            Перенаправление на оплату...
          </p>
        </div>
      </main>
    }>
      <CheckoutContent />
    </Suspense>
  );
}
