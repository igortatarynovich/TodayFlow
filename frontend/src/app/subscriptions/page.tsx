"use client";

import { useEffect, useState } from "react";
import { DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { getJson, postJson } from "@/lib/api";
import { t } from "@/lib/i18n";
import { useToast } from "@/components/ToastProvider";
import type { SubscriptionPlansResponse, CreateCheckoutResponse } from "@/lib/types";

export default function SubscriptionsPage() {
  const toast = useToast();
  const [loading, setLoading] = useState(true);
  const [authMissing, setAuthMissing] = useState(false);
  const [plans, setPlans] = useState<SubscriptionPlansResponse | null>(null);
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("todayflow_token") : null;
    if (!token) {
      setAuthMissing(true);
      setLoading(false);
      return;
    }

    const loadPlans = async () => {
      try {
        const data = await getJson<SubscriptionPlansResponse>("/subscriptions/plans");
        setPlans(data);
      } catch (err) {
        console.error("Failed to load subscription plans", err);
        toast.error(t("subscriptions.errors.loadFailed", "Не удалось загрузить планы подписок"));
      } finally {
        setLoading(false);
        setTimeout(() => setShowContent(true), 100);
      }
    };

    void loadPlans();
  }, [toast]);

  const handleSubscribe = async (planId: string) => {
    try {
      const result = await postJson<CreateCheckoutResponse>("/subscriptions/create-checkout", {
        plan_id: planId,
      });
      if (result.checkout_url) {
        window.location.href = result.checkout_url;
      } else {
        toast.error(t("subscriptions.errors.createSessionFailed", "Не удалось создать сессию оплаты"));
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : t("subscriptions.errors.createFailed", "Ошибка при создании подписки");
      toast.error(errorMessage);
    }
  };

  if (loading) {
    return (
      <ProductPageScreen
        testId="subscriptions-page"
        title={t("subscriptions.public.title", "Подписки")}
        loading
        loadingLabel={t("subscriptions.loading", "Загрузка планов подписок…")}
      />
    );
  }

  if (authMissing) {
    return (
      <ProductPageScreen
        testId="subscriptions-page"
        title={t("subscriptions.public.title", "Подписки")}
        guest={{
          message: "Войдите в аккаунт, чтобы выбрать план подписки.",
          ctaHref: "/auth?mode=login",
          ctaLabel: "Войти",
        }}
      />
    );
  }

  return (
    <ProductPageScreen
      testId="subscriptions-page"
      title={t("subscriptions.public.title", "Подписки")}
      subtitle="Выберите план подписки для доступа к расширенным функциям"
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      {plans ? (
        <div className={pl.grid2}>
          {Object.entries(plans.plans).map(([planId, plan], index) => (
            <article
              key={planId}
              className={pl.panel}
              style={{
                display: "flex",
                flexDirection: "column",
                border: planId === "full_access" ? "2px solid var(--orbit-color-highlight, #c39a5c)" : undefined,
                opacity: showContent ? 1 : 0,
                transform: showContent ? "translateY(0)" : "translateY(30px)",
                transition: `opacity 0.8s ease ${0.3 + index * 0.1}s, transform 0.8s ease ${0.3 + index * 0.1}s`,
              }}
            >
              <p className={v2.eyebrow}>
                {planId === "full_access"
                  ? t("subscriptions.plans.tag.popular", "Популярный")
                  : planId === "lite_plus"
                    ? t("subscriptions.plans.tag.starter", "Старт")
                    : t("subscriptions.plans.tag.special", "Особый")}
              </p>
              <h2 className={v2.sectionTitle}>{plan.name}</h2>
              <ul style={{ listStyle: "none", padding: 0, margin: "1rem 0", display: "flex", flexDirection: "column", gap: "0.5rem", flex: 1 }}>
                {plan.features.map((feature, idx) => (
                  <li key={idx} style={{ display: "flex", alignItems: "start", gap: "0.35rem" }}>
                    <span style={{ color: "var(--orbit-color-highlight, #c39a5c)" }}>✓</span>
                    <span className="orbit-body-sm">{feature}</span>
                  </li>
                ))}
              </ul>
              <DsButton
                variant={planId === "full_access" ? "primary" : "secondary"}
                onClick={() => void handleSubscribe(planId)}
              >
                {t("subscriptions.subscribe", "Подписаться")}
              </DsButton>
            </article>
          ))}
        </div>
      ) : null}
    </ProductPageScreen>
  );
}
