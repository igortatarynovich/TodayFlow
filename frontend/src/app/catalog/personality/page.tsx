import Link from "next/link";
import Image from "next/image";
import { getProduct, getProductDetailPath } from "@/data/catalog";
import { t } from "@/lib/i18n";
import { CatalogRecommendationGrid } from "@/components/catalog/CatalogRecommendationGrid";
import { CatalogCallout } from "@/components/catalog/CatalogCallout";
import { MeaningCard } from "@/components/orbit";

const SECTION_CONFIG = [
  {
    key: "core",
    titleKey: "catalog.personality.section.core.title",
    descriptionKey: "catalog.personality.section.core",
    productIds: ["lite_birth_chart", "full_report", "psychology_report"]
  },
  {
    key: "numerology",
    titleKey: "catalog.personality.section.numerology.title",
    descriptionKey: "catalog.personality.section.numerology",
    productIds: ["name_resonance", "numerology_deep_dive"]
  },
  {
    key: "bridges",
    titleKey: "catalog.personality.section.bridges.title",
    descriptionKey: "catalog.personality.section.bridges",
    productIds: ["star_stories", "subscription_lite_plus", "tarot_relationship"]
  }
];

export default function PersonalityCatalogPage() {
  return (
    <main className="orbit-page">
      {/* Hero Section */}
      <section className="orbit-hero-design orbit-hero-design-unified">
        <div className="orbit-hero-design-wrapper">
          <Image
            src="/images/hero-meditation.png"
            alt="Сервисы про личность"
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
              {t("catalog.personality.hero.eyebrow", "Личность")}
            </p>
            <h1 className="orbit-hero-design-title-text">{t("catalog.personality.hero.title", "Сервисы про личность")}</h1>
            <p className="orbit-hero-design-subtitle" style={{ textAlign: "center", marginTop: "var(--orbit-space-sm)" }}>
              {t("catalog.personality.hero.body", "Разбор характера, внутренних паттернов и личной структуры через профиль, отчёты и смежные сервисы.")}
            </p>
          </div>
        </div>
      </section>

      {/* Content Section */}
      <section className="orbit-hero-content-block">
        <div className="orbit-hero-content-container">
          {/* Recommendations */}
          <section className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)" }}>
            <h2 className="orbit-display-sm">{t("catalog.personality.recommendations.title", "Рекомендуемые сервисы")}</h2>
            <p className="orbit-body-sm orbit-text-muted">{t("catalog.personality.recommendations.body", "Стартовые и углублённые разборы, если хочешь понять себя точнее.")}</p>
            <CatalogRecommendationGrid slug="personality" />
          </section>

          {/* Sections */}
          {SECTION_CONFIG.map((section) => {
            const products = section.productIds
              .map((id) => getProduct(id))
              .filter((item): item is NonNullable<typeof item> => Boolean(item));
            
            // Show section even if no products, but mark as "coming soon"
            const hasProducts = products.length > 0;
            const missingProducts = section.productIds.filter(id => !getProduct(id));
            
            return (
              <section key={section.key} className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)", marginTop: "var(--orbit-space-xl)" }}>
                <h2 className="orbit-display-sm">{t(section.titleKey)}</h2>
                <p className="orbit-body-sm orbit-text-muted">{t(section.descriptionKey)}</p>
                
                {hasProducts && (
                  <div className="orbit-card-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", marginTop: "var(--orbit-space-md)" }}>
                    {products.map((product) => (
                      <Link key={product.id} href={getProductDetailPath(product.id)} className="orbit-card orbit-card-link">
                        {product.badge && <span className="orbit-badge-xs">{t(`catalog.badge.${product.badge}`, product.badge)}</span>}
                        <h3 className="orbit-display-xs">{t(product.title_key)}</h3>
                        <p className="orbit-body-sm orbit-text-muted">{t(product.summary_key)}</p>
                        <span className="orbit-link-subtle" style={{ marginTop: "var(--orbit-space-sm)" }}>
                          {t(product.cta, product.cta)} →
                        </span>
                      </Link>
                    ))}
                  </div>
                )}
                
                {missingProducts.length > 0 && (
                  <div style={{ marginTop: "var(--orbit-space-md)", padding: "var(--orbit-space-md)", background: "var(--orbit-color-mist)", borderRadius: "2px" }}>
                    <p className="orbit-body-sm orbit-text-muted">
                      {t("catalog.comingSoon", "В разработке")}: {missingProducts.join(", ")}
                    </p>
                  </div>
                )}
              </section>
            );
          })}

          {/* Callout */}
          <CatalogCallout
            eyebrow={t("catalog.personality.hero.eyebrow", "Личность")}
            title={t("catalog.aside.personality.title", "Продолжить разбор")}
            body={t("catalog.aside.personality.body", "Открой соседние сервисы, чтобы перейти от общего профиля к более точным слоям личности.")}
          />
        </div>
      </section>
    </main>
  );
}
