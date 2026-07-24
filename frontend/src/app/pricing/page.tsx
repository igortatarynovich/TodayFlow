"use client";

// DRAFT PRICING — placeholder numbers, not a decision (see docs/TODAYFLOW_PRODUCT_CANON_UNIFIED.md §7).
// Monetization is not a launch-v1 DoD blocker; paywall + price are a separate wave.

import { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import { SubscriptionTier } from "@/components/home";
import { t } from "@/lib/i18n";
import { LoadingSpinner } from "@/components/orbit";

export default function PricingPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [showContent, setShowContent] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    setShowContent(true);
    if (typeof window !== "undefined") {
      const noticeParam = new URLSearchParams(window.location.search).get("notice");
      if (noticeParam) setNotice(noticeParam);
    }
  }, []);

  if (authLoading) {
    return (
      <main className="orbit-page">
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "50vh" }}>
          <LoadingSpinner size="lg" />
        </div>
      </main>
    );
  }

  return (
    <main className="orbit-page orbit-pricing-page">
      {/* Header */}
      <section className="orbit-hero-content-block" style={{ paddingTop: "var(--orbit-space-4xl)", paddingBottom: "var(--orbit-space-lg)" }}>
        <div className="orbit-hero-content-container" style={{ textAlign: "center", maxWidth: "800px", margin: "0 auto" }}>
          {notice === "checkout_unavailable" && (
            <div
              className="orbit-card"
              style={{
                marginBottom: "var(--orbit-space-lg)",
                padding: "var(--orbit-space-md)",
                borderColor: "rgba(195, 154, 92, 0.42)",
                background: "rgba(255, 249, 237, 0.95)",
              }}
            >
              <p className="orbit-body-sm" style={{ margin: 0, color: "#7a5a32", fontWeight: 700 }}>
                Оплата временно недоступна в этой сборке. Выбери тариф, а подписку подключим на следующем этапе.
              </p>
            </div>
          )}
          <h1 
            className="orbit-display-sm" 
            style={{ 
              marginBottom: "var(--orbit-space-sm)",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease, transform 0.8s ease"
            }}
          >
            {t("pricing.title", "Планы доступа TodayFlow")}
          </h1>
          <p 
            className="orbit-body" 
            style={{ 
              color: "var(--orbit-color-slate)",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease 0.2s, transform 0.8s ease 0.2s"
            }}
          >
            {t("pricing.subtitle", "Основа доступна всем. Подписка добавляет глубину разбора, персонализацию и сопровождение по шагам.")}
          </p>
          <p
            className="orbit-body-sm"
            style={{
              marginTop: "var(--orbit-space-sm)",
              color: "#7a5c35",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease 0.25s, transform 0.8s ease 0.25s",
            }}
          >
            Free = старт и базовый контур. Plus = больше контекста. Pro = полный персональный режим.
          </p>
          <p
            className="orbit-body-xs"
            style={{
              marginTop: "0.35rem",
              color: "#8a6a3c",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease 0.3s, transform 0.8s ease 0.3s",
            }}
          >
            Ты платишь не за текст, а за certainty: что происходит, что делать сейчас и чего избегать дальше.
          </p>
        </div>
      </section>

      {/* Subscription Tiers */}
      <section className="orbit-hero-content-block" style={{ paddingTop: "var(--orbit-space-2xl)", paddingBottom: "var(--orbit-space-4xl)" }}>
        <div className="orbit-hero-content-container" style={{ maxWidth: "1200px", margin: "0 auto" }}>
          <div
            className="orbit-card"
            style={{
              marginBottom: "var(--orbit-space-xl)",
              padding: "var(--orbit-space-md) var(--orbit-space-lg)",
              border: "1px solid rgba(201, 168, 115, 0.24)",
              background: "rgba(255, 252, 245, 0.96)",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease 0.3s, transform 0.8s ease 0.3s",
            }}
          >
            <p className="orbit-body-sm" style={{ margin: 0, color: "#6b5436" }}>
              Не нужно выбирать “идеальный” тариф сразу: начни с Free, потом усили глубину в Plus или Pro, когда почувствуешь ритм.
            </p>
          </div>
          <div 
            className="subscription-tiers-grid"
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
              gap: "var(--orbit-space-xl)",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(30px)",
              transition: "opacity 0.8s ease 0.4s, transform 0.8s ease 0.4s"
            }}
          >
            {/* Free Tier */}
            <SubscriptionTier
              name="Free"
              price="0 ₽"
              features={[
                t("pricing.free.feature1", "Сигналы дня: энергия, фокус, короткие шаги"),
                t("pricing.free.feature2", "Поверхностные инсайты («что сделать сегодня»)"),
                t("pricing.free.feature3", "Карта дня в базовой глубине"),
                t("pricing.free.feature4", "Общий доступ к практикам и гороскопам"),
              ]}
              ctaText={isAuthenticated ? t("pricing.free.ctaCurrent", "Текущий план") : t("pricing.free.ctaStart", "Начать бесплатно")}
              ctaHref={isAuthenticated ? "/today" : "/auth"}
            />

            {/* Plus Tier */}
            <SubscriptionTier
              name="Plus"
              price="990 ₽/мес"
              recommended={true}
              highlight={true}
              features={[
                t("pricing.plus.feature1", "Всё из Free"),
                t("pricing.plus.feature2", "Объяснения «почему так» и первые паттерны"),
                t("pricing.plus.feature3", "Персональная карта дня и комментарии"),
                t("pricing.plus.feature4", "Персонализированные практики"),
                t("pricing.plus.feature5", "Персональные гороскопы"),
                t("pricing.plus.feature6", "Журналы желаний и благодарности"),
                t("pricing.plus.feature7", "Доступ к марафонам (платные отдельно)"),
              ]}
              ctaText={t("pricing.plus.cta", "Начать Plus")}
              ctaHref={isAuthenticated ? "/account/subscriptions" : "/auth"}
            />

            {/* Pro Tier */}
            <SubscriptionTier
              name="Pro"
              price="2490 ₽/мес"
              features={[
                t("pricing.pro.feature1", "Всё из Plus"),
                t("pricing.pro.feature2", "Системные инсайты и более глубокое чтение жизни на «Сегодня»"),
                t("pricing.pro.feature3", "Полный разбор паттернов и сценариев"),
                t("pricing.pro.feature4", "Расширенные расклады таро"),
                t("pricing.pro.feature5", "Совместимости"),
                t("pricing.pro.feature6", "Все марафоны бесплатно"),
                t("pricing.pro.feature7", "Аналитика журналов"),
                t("pricing.pro.feature8", "Приоритетная поддержка и ранний доступ"),
              ]}
              ctaText={t("pricing.pro.cta", "Начать Pro")}
              ctaHref={isAuthenticated ? "/account/subscriptions" : "/auth"}
            />
          </div>
          <div className="orbit-card" style={{ marginTop: "var(--orbit-space-xl)", padding: "var(--orbit-space-lg)" }}>
            <h2 className="orbit-heading-2" style={{ marginBottom: "0.6rem" }}>
              Как выбрать план
            </h2>
            <div style={{ display: "grid", gap: "0.6rem", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
              <div>
                <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700 }}>Free</p>
                <p className="orbit-body-xs orbit-text-muted" style={{ margin: "0.2rem 0 0" }}>Старт, базовый ритм и первый персональный контур.</p>
              </div>
              <div>
                <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700 }}>Plus</p>
                <p className="orbit-body-xs orbit-text-muted" style={{ margin: "0.2rem 0 0" }}>Больше контекста, объяснения и точнее подбор практик.</p>
              </div>
              <div>
                <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700 }}>Pro</p>
                <p className="orbit-body-xs orbit-text-muted" style={{ margin: "0.2rem 0 0" }}>Полная глубина Guidance, совместимость и приоритетная поддержка.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="orbit-hero-content-block" style={{ paddingTop: "var(--orbit-space-2xl)", paddingBottom: "var(--orbit-space-4xl)", background: "var(--orbit-color-mist)" }}>
        <div className="orbit-hero-content-container" style={{ maxWidth: "1200px", margin: "0 auto" }}>
          <h2 
            className="orbit-display-sm" 
            style={{ 
              textAlign: "center",
              marginBottom: "var(--orbit-space-xl)",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease 0.6s, transform 0.8s ease 0.6s"
            }}
          >
            Сравнение тарифов
          </h2>
          
          <div 
            className="orbit-card"
            style={{
              padding: "var(--orbit-space-xl)",
              overflowX: "auto",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease 0.7s, transform 0.8s ease 0.7s"
            }}
          >
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ borderBottom: "2px solid var(--orbit-color-border)" }}>
                  <th style={{ padding: "var(--orbit-space-md)", textAlign: "left", fontWeight: 600 }}>Что получаешь</th>
                  <th style={{ padding: "var(--orbit-space-md)", textAlign: "center", fontWeight: 600 }}>Free</th>
                  <th style={{ padding: "var(--orbit-space-md)", textAlign: "center", fontWeight: 600 }}>Plus</th>
                  <th style={{ padding: "var(--orbit-space-md)", textAlign: "center", fontWeight: 600 }}>Pro</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ borderBottom: "1px solid var(--orbit-color-border-light)" }}>
                  <td style={{ padding: "var(--orbit-space-md)" }}>Глубина инсайта на «Сегодня»</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center" }}>Сигналы</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>
                    + объяснения и паттерны
                  </td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>
                    + жизненный контекст
                  </td>
                </tr>
                <tr style={{ borderBottom: "1px solid var(--orbit-color-border-light)" }}>
                  <td style={{ padding: "var(--orbit-space-md)" }}>Карта дня</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center" }}>Общая</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>✓ Персональная</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>✓ Персональная</td>
                </tr>
                <tr style={{ borderBottom: "1px solid var(--orbit-color-border-light)" }}>
                  <td style={{ padding: "var(--orbit-space-md)" }}>Практики</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center" }}>Общие</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>✓ Персонализированные</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>✓ Персонализированные</td>
                </tr>
                <tr style={{ borderBottom: "1px solid var(--orbit-color-border-light)" }}>
                  <td style={{ padding: "var(--orbit-space-md)" }}>Разбор паттернов</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center" }}>—</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>Lite (3-4 инсайта)</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>✓ Полный</td>
                </tr>
                <tr style={{ borderBottom: "1px solid var(--orbit-color-border-light)" }}>
                  <td style={{ padding: "var(--orbit-space-md)" }}>Гороскопы</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center" }}>Общие</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>✓ Персональные</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>✓ Персональные</td>
                </tr>
                <tr style={{ borderBottom: "1px solid var(--orbit-color-border-light)" }}>
                  <td style={{ padding: "var(--orbit-space-md)" }}>Расклады таро</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center" }}>Базовые</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center" }}>Базовые</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>✓ Все</td>
                </tr>
                <tr style={{ borderBottom: "1px solid var(--orbit-color-border-light)" }}>
                  <td style={{ padding: "var(--orbit-space-md)" }}>Совместимости</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center" }}>—</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center" }}>—</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>✓</td>
                </tr>
                <tr style={{ borderBottom: "1px solid var(--orbit-color-border-light)" }}>
                  <td style={{ padding: "var(--orbit-space-md)" }}>Журналы</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center" }}>—</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>✓ Базовые</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>✓ + Аналитика</td>
                </tr>
                <tr style={{ borderBottom: "1px solid var(--orbit-color-border-light)" }}>
                  <td style={{ padding: "var(--orbit-space-md)" }}>Марафоны</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center" }}>Платные</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center" }}>Платные</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>✓ Бесплатно</td>
                </tr>
                <tr>
                  <td style={{ padding: "var(--orbit-space-md)" }}>Поддержка</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center" }}>Базовая</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center" }}>Базовая</td>
                  <td style={{ padding: "var(--orbit-space-md)", textAlign: "center", color: "var(--orbit-color-highlight)", fontWeight: 600 }}>✓ Приоритетная</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div style={{ marginTop: "var(--orbit-space-lg)", textAlign: "center" }}>
            <Link href="/help" className="orbit-button orbit-button-secondary">
              Перейти в FAQ и поддержку
            </Link>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="orbit-hero-content-block" style={{ paddingTop: "var(--orbit-space-2xl)", paddingBottom: "var(--orbit-space-4xl)" }}>
        <div className="orbit-hero-content-container" style={{ maxWidth: "800px", margin: "0 auto" }}>
          <h2 
            className="orbit-display-sm" 
            style={{ 
              textAlign: "center",
              marginBottom: "var(--orbit-space-xl)",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease 0.8s, transform 0.8s ease 0.8s"
            }}
          >
            Частые вопросы
          </h2>
          
          <div 
            style={{
              display: "grid",
              gap: "var(--orbit-space-lg)",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease 0.9s, transform 0.8s ease 0.9s"
            }}
          >
            <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
              <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-sm)" }}>
                Можно ли отменить подписку?
              </h3>
              <p className="orbit-body-sm orbit-text-muted" style={{ lineHeight: 1.6 }}>
                Да, ты можешь отменить подписку в любой момент в настройках аккаунта. Доступ сохранится до конца оплаченного периода.
              </p>
            </div>

            <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
              <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-sm)" }}>
                Что происходит после регистрации?
              </h3>
              <p className="orbit-body-sm orbit-text-muted" style={{ lineHeight: 1.6 }}>
                После регистрации ты получаешь доступ к Free тарифу. Для получения персонального профиля нужно ввести данные рождения на странице создания профиля.
              </p>
            </div>

            <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
              <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-sm)" }}>
                Можно ли перейти с Plus на Pro?
              </h3>
              <p className="orbit-body-sm orbit-text-muted" style={{ lineHeight: 1.6 }}>
                Да, ты можешь обновить подписку в любой момент. Разница в стоимости будет пропорционально пересчитана.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="orbit-hero-content-block" style={{ paddingTop: "var(--orbit-space-2xl)", paddingBottom: "var(--orbit-space-4xl)", background: "var(--orbit-color-mist)" }}>
        <div className="orbit-hero-content-container" style={{ maxWidth: "600px", margin: "0 auto", textAlign: "center" }}>
          <h2 
            className="orbit-display-sm" 
            style={{ 
              marginBottom: "var(--orbit-space-md)",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease 1s, transform 0.8s ease 1s"
            }}
          >
            Готов начать?
          </h2>
          <p 
            className="orbit-body-sm orbit-text-muted" 
            style={{ 
              marginBottom: "var(--orbit-space-xl)",
              lineHeight: 1.6,
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease 1.1s, transform 0.8s ease 1.1s"
            }}
          >
            Начни с бесплатного тарифа или сразу выбери подходящую подписку
          </p>
          <div 
            style={{ 
              display: "flex", 
              gap: "var(--orbit-space-md)", 
              justifyContent: "center",
              flexWrap: "wrap",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease 1.2s, transform 0.8s ease 1.2s"
            }}
          >
            <Link href={isAuthenticated ? "/account/subscriptions" : "/auth"} className="orbit-button orbit-button-primary orbit-button-large">
              {isAuthenticated ? "Управление подпиской" : "Начать"}
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
