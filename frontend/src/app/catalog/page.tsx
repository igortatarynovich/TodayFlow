"use client";

import Link from "next/link";
import Image from "next/image";
import { t } from "@/lib/i18n";
import { catalogNavigation, getProduct, getProductDetailPath } from "@/data/catalog";
import { CatalogRecommendationGrid } from "@/components/catalog/CatalogRecommendationGrid";
import { CatalogCallout } from "@/components/catalog/CatalogCallout";

export default function CatalogIndexPage() {
  const columns = catalogNavigation.columns;

  return (
    <main className="orbit-page">
      {/* Hero Section */}
      <section className="orbit-hero-design orbit-hero-design-unified">
        <div className="orbit-hero-design-wrapper">
          <Image
            src="/images/hero-meditation.png"
            alt="Catalog"
            fill
            priority
            className="orbit-hero-design-bg"
            style={{ objectFit: "cover", objectPosition: "center" }}
          />
          <div className="orbit-hero-design-overlay" />
          
          {/* Large transparent gradient forms (silk/fog effect) */}
          <div className="orbit-hero-design-silk">
            <div className="orbit-hero-design-silk-1" />
            <div className="orbit-hero-design-silk-2" />
            <div className="orbit-hero-design-silk-3" />
          </div>

          {/* Connecting lines */}
          <div className="orbit-hero-design-lines">
            <svg className="orbit-hero-design-lines-svg" viewBox="0 0 1920 1080" preserveAspectRatio="none">
              <path d="M300,200 Q600,150 900,200 T1500,200" stroke="rgba(255,255,255,0.25)" strokeWidth="1.5" fill="none" />
              <path d="M400,400 Q700,350 1000,400 T1600,400" stroke="rgba(255,255,255,0.2)" strokeWidth="1" fill="none" />
            </svg>
          </div>

          {/* Content */}
          <div className="orbit-hero-design-container">
            <p className="orbit-hero-design-subtitle" style={{ textAlign: "center", marginBottom: "var(--orbit-space-sm)", color: "rgba(255, 255, 255, 0.85)" }}>
              {t("catalog.index.hero.eyebrow", "Каталог сервисов")}
            </p>
            <h1 className="orbit-hero-design-title-text">{t("catalog.index.hero.title", "Сервисы TodayFlow")}</h1>
            <p className="orbit-hero-design-subtitle" style={{ textAlign: "center", marginTop: "var(--orbit-space-sm)" }}>
              {t("catalog.index.hero.body", "Выбери сервис по своей задаче: понять себя, прочитать день, углубиться в отношения или открыть следующий слой персонального разбора.")}
            </p>
            <div className="orbit-hero-design-ctas" style={{ marginTop: "var(--orbit-space-lg)" }}>
              <Link href="/onboarding/core" className="orbit-button orbit-button-primary orbit-button-hero">
                {t("catalog.index.hero.cta.birth", "Начать с профиля")}
              </Link>
              <Link href="/today" className="orbit-button orbit-button-secondary orbit-button-hero">
                {t("catalog.index.hero.cta.dashboard", "Открыть Today")}
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Content Section */}
      <section className="orbit-hero-content-block">
        <div className="orbit-hero-content-container">

          <section className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)" }}>
            <h2 className="orbit-display-sm">{t("catalog.index.recommendations.title", "Доступные сервисы")}</h2>
        <p className="orbit-body-sm orbit-text-muted">
          {t("catalog.index.recommendations.body", "На данный момент доступны два основных направления.")}
        </p>
        <div style={{ 
          display: "flex",
          justifyContent: "center",
          alignItems: "flex-start",
          gap: "var(--orbit-space-3xl)", 
          maxWidth: "1200px",
          margin: "var(--orbit-space-md) auto 0",
          flexWrap: "wrap",
        }}>
          {columns.map((column) =>
            column.sections.map((section) =>
              section.items.map((item) => {
                const product = getProduct(item.product_id);
                if (!product) return null;
                return (
                  <Link
                    key={product.id}
                    href={getProductDetailPath(product.id)}
                    className="orbit-card orbit-card-link"
                    style={{ padding: "var(--orbit-space-lg)", textAlign: "center", maxWidth: "300px" }}
                  >
                    <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-sm)" }}>
                      {t(product.title_key)}
                    </h3>
                    <p className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-sm)", lineHeight: 1.5 }}>
                      {t(product.summary_key)}
                    </p>
                    <div style={{ marginTop: "var(--orbit-space-sm)" }}>
                      <span className="orbit-body-sm" style={{ fontWeight: 600 }}>
                        {product.access === "free" ? t("catalog.product.access.free", "Бесплатно") : t("catalog.product.access.paid", "Платно")}
                      </span>
                      {product.badge && (
                        <span className="orbit-badge-xs" style={{ marginLeft: "var(--orbit-space-xs)" }}>{t(`catalog.badge.${product.badge}`, product.badge)}</span>
                      )}
                    </div>
                  </Link>
                );
              })
            )
          )}
        </div>
      </section>

          <section className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)", marginTop: "var(--orbit-space-xl)" }}>
            <h2 className="orbit-display-sm">В разработке</h2>
        <p className="orbit-body-sm orbit-text-muted">
          Следующие функции находятся в разработке и будут доступны в ближайшее время:
        </p>
        <ul className="orbit-list-unstyled" style={{ marginTop: "var(--orbit-space-md)", paddingLeft: "var(--orbit-space-md)" }}>
          <li className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-sm)" }}>• Tarot Flow — ежедневные карты, ритуалы и guided readings</li>
          <li className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-sm)" }}>• Numerology — более глубокий слой чисел имени и даты рождения</li>
          <li className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-sm)" }}>• Celestial — лунные фазы, транзиты и текущие небесные акценты</li>
          <li className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-sm)" }}>• Weekly Focus — недельный фокус и интеграция</li>
        </ul>
          </section>
        </div>
      </section>
    </main>
  );
}
