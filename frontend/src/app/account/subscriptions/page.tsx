"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { OrientationRail, LoadingSpinner } from "@/components/orbit";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { getJson, postJson } from "@/lib/api";
import { getLocale, t } from "@/lib/i18n";
import { ruPluralForm } from "@/lib/ruPlural";
import { useToast } from "@/components/ToastProvider";
import { PromoCodeInput } from "@/components/payments/PromoCodeInput";
import type { SubscriptionsListResponse, SubscriptionHistoryResponse, SubscriptionPlansResponse, CreateCheckoutResponse } from "@/lib/types";

function subscriptionsRailStepLabel(count: number): string {
  if (getLocale() === "ru") {
    const word = ruPluralForm(
      count,
      t("subscriptions.account.rail.subOne", "подписка"),
      t("subscriptions.account.rail.subFew", "подписки"),
      t("subscriptions.account.rail.subMany", "подписок"),
    );
    return `${count} ${word}`;
  }
  const word =
    count === 1 ? t("subscriptions.account.rail.subOne", "subscription") : t("subscriptions.account.rail.subMany", "subscriptions");
  return `${count} ${word}`;
}

function paymentsRailStepLabel(count: number): string {
  if (getLocale() === "ru") {
    const word = ruPluralForm(
      count,
      t("subscriptions.account.rail.paymentOne", "платёж"),
      t("subscriptions.account.rail.paymentFew", "платежа"),
      t("subscriptions.account.rail.paymentMany", "платежей"),
    );
    return `${count} ${word}`;
  }
  const word =
    count === 1 ? t("subscriptions.account.rail.paymentOne", "payment") : t("subscriptions.account.rail.paymentMany", "payments");
  return `${count} ${word}`;
}

function AccountSubscriptionsContent() {
  const toast = useToast();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [authMissing, setAuthMissing] = useState(false);
  const [subscriptions, setSubscriptions] = useState<SubscriptionsListResponse | null>(null);
  const [history, setHistory] = useState<SubscriptionHistoryResponse | null>(null);
  const [plans, setPlans] = useState<SubscriptionPlansResponse | null>(null);
  const [showContent, setShowContent] = useState(false);
  const [creatingCheckout, setCreatingCheckout] = useState<string | null>(null);
  const [promoCodes, setPromoCodes] = useState<Record<string, string>>({});

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("todayflow_token") : null;
    if (!token) {
      setAuthMissing(true);
      setLoading(false);
      return;
    }

    const loadData = async () => {
      try {
        const [subs, hist, plansData] = await Promise.all([
          getJson<SubscriptionsListResponse>("/subscriptions/list").catch(() => null),
          getJson<SubscriptionHistoryResponse>("/subscriptions/history").catch(() => null),
          getJson<SubscriptionPlansResponse>("/subscriptions/plans").catch(() => null),
        ]);
        setSubscriptions(subs);
        setHistory(hist);
        setPlans(plansData);
      } catch (err) {
        console.error("Failed to load subscription data", err);
        toast.error(t("subscriptions.errors.loadFailed", "Не удалось загрузить данные подписок"));
      } finally {
        setLoading(false);
        setTimeout(() => setShowContent(true), 100);
      }
    };

    loadData();
  }, [toast]);

  // Handle success/cancelled from Stripe redirect
  useEffect(() => {
    const success = searchParams?.get("success");
    const cancelled = searchParams?.get("cancelled");
    
    if (success === "1") {
      toast.success(t("subscriptions.success.activated", "Подписка успешно активирована!"));
      // Reload subscriptions
      getJson<SubscriptionsListResponse>("/subscriptions/list")
        .then(setSubscriptions)
        .catch(console.error);
    } else if (cancelled === "1") {
      toast.info(t("subscriptions.info.cancelled", "Оформление подписки отменено"));
    }
  }, [searchParams, toast]);

  const handleCancel = async (subscriptionId?: number) => {
    if (!confirm(t("subscriptions.cancelConfirm", "Вы уверены, что хотите отменить подписку?"))) {
      return;
    }

    try {
      await postJson("/subscriptions/cancel", { subscription_id: subscriptionId });
      toast.success(t("subscriptions.cancelSuccess", "Подписка отменена"));
      // Reload data
      const subs = await getJson<SubscriptionsListResponse>("/subscriptions/list");
      setSubscriptions(subs);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : t("subscriptions.errors.cancelFailed", "Ошибка при отмене подписки");
      toast.error(errorMessage);
    }
  };

  const handleCreateCheckout = async (planId: string) => {
    setCreatingCheckout(planId);
    try {
      const response = await postJson<CreateCheckoutResponse>("/subscriptions/create-checkout", { 
        plan_id: planId,
        promo_code: promoCodes[planId] || null,
      });
      if (response.checkout_url) {
        window.location.href = response.checkout_url;
      } else {
        toast.error(t("subscriptions.errors.createSessionFailed", "Не удалось создать сессию оплаты"));
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Ошибка при создании подписки";
      toast.error(errorMessage);
      setCreatingCheckout(null);
    }
  };

  if (loading) {
    return (
      <ProductPageScreen
        title="Управление подписками"
        loading
        loadingLabel={t("subscriptions.loading", "Загрузка подписок…")}
      />
    );
  }

  if (authMissing) {
    return (
      <ProductPageScreen
        title="Управление подписками"
        guest={{
          message: "Войдите в аккаунт для управления подписками",
          ctaHref: "/auth?mode=login",
          ctaLabel: "Войти",
        }}
      />
    );
  }

  return (
    <ProductPageScreen
      testId="account-subscriptions-page"
      title="Управление подписками"
      subtitle="Управляйте своими подписками и просматривайте историю платежей"
      railTitle={t("subscriptions.account.rail.section", "Подписки")}
      railHint={t("subscriptions.account.rail.activeMeta", "Активные")}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      {subscriptions && subscriptions.subscriptions.length > 0 ? (
        <section className="orbit-hero-content-block">
          <div className="orbit-hero-content-container">
            <div 
              className="orbit-card" 
              style={{ 
                background: "rgba(255, 255, 255, 0.95)", 
                boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
                opacity: showContent ? 1 : 0,
                transform: showContent ? "translateY(0)" : "translateY(30px)",
                transition: "opacity 0.8s ease 0.3s, transform 0.8s ease 0.3s"
              }}
            >
              <OrientationRail
                sectionLabel={t("subscriptions.account.rail.section", "Подписки")}
                metaLabel={t("subscriptions.account.rail.activeMeta", "Активные")}
                stepLabel={subscriptionsRailStepLabel(subscriptions.subscriptions.length)}
              />
              <div style={{ marginTop: "var(--orbit-space-lg)", display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)" }}>
                {subscriptions.subscriptions.map((sub) => (
                  <div
                    key={sub.id}
                    style={{
                      padding: "var(--orbit-space-md)",
                      border: "1px solid var(--orbit-color-border)",
                      borderRadius: "var(--orbit-radius-sm)",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "var(--orbit-space-sm)" }}>
                      <div style={{ flex: 1 }}>
                        <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-xs)" }}>
                          {plans?.plans[sub.plan_id]?.name || sub.plan_id}
                        </h3>
                        <span className={`orbit-badge-xs ${sub.status === "active" ? "" : "orbit-badge-xs--muted"}`}>
                          {sub.status === "active" ? "Активна" : sub.status === "canceled" ? "Отменена" : sub.status}
                        </span>
                        {plans?.plans[sub.plan_id]?.features && (
                          <div style={{ marginTop: "var(--orbit-space-sm)" }}>
                            <p className="orbit-body-xs orbit-text-muted" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                              Включено:
                            </p>
                            <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: "var(--orbit-space-xs)" }}>
                              {plans.plans[sub.plan_id].features.map((feature, idx) => (
                                <li key={idx} className="orbit-body-xs" style={{ paddingLeft: "var(--orbit-space-md)", position: "relative" }}>
                                  <span style={{ position: "absolute", left: 0, color: "var(--orbit-color-primary)" }}>✓</span>
                                  {feature === "lite_reports" ? "Lite разборы" :
                                   feature === "full_reports" ? "Полные разборы" :
                                   feature === "weekly_insights" ? "Еженедельные инсайты" :
                                   feature === "tarot_flow" ? "Tarot Flow" :
                                   feature === "tarot_history" ? "История карт" :
                                   feature === "tarot_spreads" ? "Расклады карт" :
                                   feature === "numerology" ? "Нумерология" :
                                   feature === "celestial_flow" ? "Небесные события" :
                                   feature}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-xs)", marginLeft: "var(--orbit-space-md)" }}>
                        {sub.status === "active" && (
                          <>
                            <Link
                              href="/pricing"
                              className="orbit-button orbit-button-primary"
                              style={{ fontSize: "var(--orbit-text-body-sm)", whiteSpace: "nowrap" }}
                            >
                              Изменить план
                            </Link>
                            <button
                              onClick={() => handleCancel(sub.id)}
                              className="orbit-button orbit-button-secondary"
                              style={{ fontSize: "var(--orbit-text-body-sm)", whiteSpace: "nowrap" }}
                            >
                              {t("subscriptions.cancel", "Отменить")}
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-xs)", marginTop: "var(--orbit-space-sm)" }}>
                      <p className="orbit-body-sm orbit-text-muted">
                        Период: {new Date(sub.current_period_start).toLocaleDateString("ru-RU")} - {new Date(sub.current_period_end).toLocaleDateString("ru-RU")}
                      </p>
                      {sub.cancel_at_period_end && (
                        <p className="orbit-body-sm" style={{ color: "var(--orbit-color-coral)" }}>
                          {t("subscriptions.cancellingAtPeriodEnd", "Будет отменена в конце периода")}
                        </p>
                      )}
                      {sub.trial_end && new Date(sub.trial_end) > new Date() && (
                        <p className="orbit-body-sm" style={{ color: "var(--orbit-color-turquoise)" }}>
                          {t("subscriptions.trialUntil", "Trial до")} {new Date(sub.trial_end).toLocaleDateString("ru-RU")}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      ) : (
        <section className="orbit-hero-content-block">
          <div className="orbit-hero-content-container">
            <div 
              className="orbit-card" 
              style={{ 
                background: "rgba(255, 255, 255, 0.95)", 
                boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
                opacity: showContent ? 1 : 0,
                transform: showContent ? "translateY(0)" : "translateY(30px)",
                transition: "opacity 0.8s ease 0.3s, transform 0.8s ease 0.3s"
              }}
            >
              <OrientationRail
                sectionLabel={t("subscriptions.account.rail.section", "Подписки")}
                metaLabel={t("subscriptions.account.rail.plansMeta", "Доступные планы")}
              />
              <p className="orbit-body" style={{ marginTop: "var(--orbit-space-md)" }}>
                {t("subscriptions.noSubscriptions", "У вас нет активных подписок")}
              </p>
              <p className="orbit-body-sm orbit-text-muted" style={{ marginTop: "var(--orbit-space-sm)" }}>
                Выберите подписку, чтобы получить доступ ко всем функциям TodayFlow
              </p>
              {plans && Object.keys(plans.plans).length > 0 && (
                <div style={{ marginTop: "var(--orbit-space-lg)", display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)" }}>
                  {Object.entries(plans.plans).map(([planId, plan]) => (
                    <div
                      key={planId}
                      style={{
                        padding: "var(--orbit-space-md)",
                        border: "1px solid var(--orbit-color-border)",
                        borderRadius: "var(--orbit-radius-sm)",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
                        <div style={{ flex: 1 }}>
                          <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-xs)" }}>
                            {plan.name}
                          </h3>
                          {plan.features && plan.features.length > 0 && (
                            <ul style={{ listStyle: "none", padding: 0, margin: "var(--orbit-space-sm) 0 0 0", display: "flex", flexDirection: "column", gap: "var(--orbit-space-xs)" }}>
                              {plan.features.map((feature, idx) => (
                                <li key={idx} className="orbit-body-xs" style={{ paddingLeft: "var(--orbit-space-md)", position: "relative" }}>
                                  <span style={{ position: "absolute", left: 0, color: "var(--orbit-color-primary)" }}>✓</span>
                                  {feature === "lite_reports" ? "Lite разборы" :
                                   feature === "full_reports" ? "Полные разборы" :
                                   feature === "weekly_insights" ? "Еженедельные инсайты" :
                                   feature === "tarot_flow" ? "Tarot Flow" :
                                   feature === "tarot_history" ? "История карт" :
                                   feature === "tarot_spreads" ? "Расклады карт" :
                                   feature === "numerology" ? "Нумерология" :
                                   feature === "celestial_flow" ? "Небесные события" :
                                   feature}
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-sm)", marginLeft: "var(--orbit-space-md)", minWidth: "200px" }}>
                          <PromoCodeInput
                            onValidated={(code) => {
                              setPromoCodes({ ...promoCodes, [planId]: code });
                            }}
                            onRemoved={() => {
                              const newCodes = { ...promoCodes };
                              delete newCodes[planId];
                              setPromoCodes(newCodes);
                            }}
                            productType="subscription"
                          />
                          <button
                            onClick={() => handleCreateCheckout(planId)}
                            disabled={creatingCheckout === planId}
                            className="orbit-button orbit-button-primary"
                            style={{ whiteSpace: "nowrap" }}
                          >
                            {creatingCheckout === planId ? (
                              <>
                                <LoadingSpinner size="sm" />
                                <span style={{ marginLeft: "var(--orbit-space-xs)" }}>Создание...</span>
                              </>
                            ) : (
                              "Оформить"
                            )}
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              <div style={{ marginTop: "var(--orbit-space-md)" }}>
                <Link href="/pricing" className="orbit-button orbit-button-secondary">
                  {t("subscriptions.browsePlans", "Посмотреть все планы")}
                </Link>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Billing History */}
      {history && history.history.length > 0 && (
        <section className="orbit-hero-content-block">
          <div className="orbit-hero-content-container">
            <div 
              className="orbit-card" 
              style={{ 
                background: "rgba(255, 255, 255, 0.95)", 
                boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
                opacity: showContent ? 1 : 0,
                transform: showContent ? "translateY(0)" : "translateY(30px)",
                transition: "opacity 0.8s ease 0.4s, transform 0.8s ease 0.4s"
              }}
            >
              <OrientationRail
                sectionLabel={t("subscriptions.account.rail.billingSection", "Оплаты")}
                metaLabel={t("subscriptions.account.rail.paymentsMeta", "Платежи")}
                stepLabel={paymentsRailStepLabel(history.history.length)}
              />
              <div style={{ marginTop: "var(--orbit-space-lg)", display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)" }}>
                {history.history.map((item) => (
                  <div
                    key={item.id}
                    style={{
                      padding: "var(--orbit-space-md)",
                      border: "1px solid var(--orbit-color-border)",
                      borderRadius: "var(--orbit-radius-sm)",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "var(--orbit-space-xs)" }}>
                      <div>
                        <p className="orbit-body-sm orbit-text-muted">
                          {new Date(item.created_at).toLocaleDateString("ru-RU")}
                        </p>
                        <p className="orbit-body-sm">
                          {(item.amount / 100).toFixed(2)} {item.currency.toUpperCase()}
                        </p>
                      </div>
                      <span className={`orbit-badge-xs ${item.status === "paid" ? "" : "orbit-badge-xs--muted"}`}>
                        {item.status}
                      </span>
                    </div>
                    {item.stripe_invoice_id && (
                      <p className="orbit-body-sm orbit-text-muted" style={{ marginTop: "var(--orbit-space-xs)" }}>
                        Invoice: {item.stripe_invoice_id}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}
    </ProductPageScreen>
  );
}

export default function AccountSubscriptionsPage() {
  return (
    <Suspense
      fallback={
        <ProductPageScreen
          title="Управление подписками"
          loading
          loadingLabel={t("subscriptions.loading", "Загрузка подписок…")}
        />
      }
    >
      <AccountSubscriptionsContent />
    </Suspense>
  );
}
