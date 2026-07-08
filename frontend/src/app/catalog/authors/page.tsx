import Link from "next/link";
import Image from "next/image";
import { getProduct, getProductDetailPath } from "@/data/catalog";
import { t } from "@/lib/i18n";
import { CatalogRecommendationGrid } from "@/components/catalog/CatalogRecommendationGrid";
import { CatalogCallout } from "@/components/catalog/CatalogCallout";

const SECTION_CONFIG = [
  {
    key: "liz",
    titleKey: "catalog.authors.section.liz.title",
    descriptionKey: "catalog.authors.section.liz",
    productIds: ["psychology_report", "star_stories"]
  },
  {
    key: "robert",
    titleKey: "catalog.authors.section.robert.title",
    descriptionKey: "catalog.authors.section.robert",
    productIds: ["astro_prediction", "year_transits"]
  },
  {
    key: "marcus",
    titleKey: "catalog.authors.section.marcus.title",
    descriptionKey: "catalog.authors.section.marcus",
    productIds: ["second_half_life", "compatibility_portal"]
  }
];

export default function AuthorsCatalogPage() {
  return (
    <main className="orbit-page">
      {/* Hero Section */}
      <section className="orbit-hero-design orbit-hero-design-unified">
        <div className="orbit-hero-design-wrapper">
          <Image
            src="/images/hero-meditation.png"
            alt="Авторы и направления"
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
              {t("catalog.authors.hero.eyebrow", "Авторы")}
            </p>
            <h1 className="orbit-hero-design-title-text">{t("catalog.authors.hero.title", "Авторы и направления")}</h1>
            <p className="orbit-hero-design-subtitle" style={{ textAlign: "center", marginTop: "var(--orbit-space-sm)" }}>
              {t("catalog.authors.hero.body", "Сервисы и материалы, собранные вокруг конкретных авторов, школ и подходов к интерпретации.")}
            </p>
          </div>
        </div>
      </section>

      {/* Content Section */}
      <section className="orbit-hero-content-block">
        <div className="orbit-hero-content-container">
          {/* Recommendations */}
          <section className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)" }}>
            <h2 className="orbit-display-sm">{t("catalog.authors.recommendations.title", "Рекомендуемые авторы и материалы")}</h2>
            <p className="orbit-body-sm orbit-text-muted">{t("catalog.authors.recommendations.body", "Подборка авторских сервисов и работ, с которых удобно начать знакомство.")}</p>
            <CatalogRecommendationGrid slug="authors" />
          </section>

          {/* Sections */}
          {SECTION_CONFIG.map((section) => {
            const products = section.productIds
              .map((id) => getProduct(id))
              .filter((item): item is NonNullable<typeof item> => Boolean(item));
            
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
            eyebrow={t("catalog.authors.hero.eyebrow", "Авторы")}
            title={t("catalog.aside.authors.title", "Посмотреть других авторов")}
            body={t("catalog.aside.authors.body", "Открой соседние материалы, если хочешь сравнить подходы и найти близкий тебе стиль чтения.")}
          />
        </div>
      </section>
    </main>
  );
}
