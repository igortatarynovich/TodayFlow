import Link from "next/link";
import Image from "next/image";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { OrientationRail, MeaningCard } from "@/components/orbit";
import { CatalogCallout } from "@/components/catalog/CatalogCallout";
import { CatalogRecommendationGrid } from "@/components/catalog/CatalogRecommendationGrid";
import { t } from "@/lib/i18n";
import { catalogProducts, getProduct, getProductPlacements } from "@/data/catalog";
import type { CatalogProduct } from "@/data/catalog";

type Params = {
  id: string;
};

export function generateStaticParams() {
  return catalogProducts.map(({ id }) => ({ id }));
}

export function generateMetadata({ params }: { params: Params }): Metadata {
  const product = getProduct(params.id);
  if (!product) {
    return {
      title: t("catalog.product.meta.defaultTitle", "Каталог TodayFlow"),
      description: t("catalog.product.meta.defaultDescription", "Персональные сервисы TodayFlow: профиль, день, отношения, периоды и углублённые разборы.")
    };
  }
  const title = `${t(product.title_key)} · Каталог TodayFlow`;
  const description = t(product.summary_key);
  const url = `/catalog/product/${product.id}`;
  return {
    title,
    description,
    openGraph: {
      title,
      description,
      url
    },
    twitter: {
      card: "summary_large_image",
      title,
      description
    }
  };
}

export default function CatalogProductPage({ params }: { params: Params }) {
  const product = getProduct(params.id);
  if (!product) {
    notFound();
  }
  const translateOptional = (key: string) => {
    const value = t(key);
    return value === key ? null : value;
  };
  const placements = getProductPlacements(product.id);
  const primaryPlacement = placements[0];
  const siblingProducts = (primaryPlacement?.section.items ?? [])
    .map((entry) => getProduct(entry.product_id))
    .filter((entry): entry is CatalogProduct => Boolean(entry));
  const relatedProducts = siblingProducts.filter((entry) => entry.id !== product.id);
  const heroContext = translateOptional(`catalog.products.${product.id}.hero_context`);
  const featureCards: { title: string; body: string }[] = [];
  for (let index = 1; index <= 6; index += 1) {
    const title = translateOptional(`catalog.products.${product.id}.feature.${index}.title`);
    const body = translateOptional(`catalog.products.${product.id}.feature.${index}.body`);
    if (!title) {
      break;
    }
    featureCards.push({ title, body: body ?? "" });
  }
  const requirementsTitle =
    translateOptional(`catalog.products.${product.id}.requirements.title`) ??
    t("catalog.product.section.requirements.title", "Что понадобится от тебя");
  const requirementsBody =
    translateOptional(`catalog.products.${product.id}.requirements.body`) ??
    t("catalog.product.section.requirements.body", "Один и тот же профиль и уже собранная база используются дальше в Today, weekly-focus и более глубоких сервисах.");
  const requirementItems: string[] = [];
  for (let index = 1; index <= 8; index += 1) {
    const item = translateOptional(`catalog.products.${product.id}.requirements.list.${index}`);
    if (!item) {
      break;
    }
    requirementItems.push(item);
  }
  const hasRequirementsCopy = requirementItems.length > 0 || requirementsBody;
  const bridgeTitle = translateOptional(`catalog.products.${product.id}.bridge.title`);
  const bridgeBody = translateOptional(`catalog.products.${product.id}.bridge.body`);
  const bridgeCta =
    translateOptional(`catalog.products.${product.id}.bridge.cta`) ??
    t("catalog.product.section.bridge.defaultCta", "Продолжить в сервисе");

  return (
    <main className="orbit-page">
      {/* Hero Section */}
      <section className="orbit-hero-design orbit-hero-design-unified">
        <div className="orbit-hero-design-wrapper">
          <Image
            src="/images/hero-meditation.png"
            alt={t(product.title_key)}
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
              {t("catalog.product.hero.eyebrow", "Сервис TodayFlow")}
            </p>
            <h1 className="orbit-hero-design-title-text">{t(product.title_key)}</h1>
            <p className="orbit-hero-design-subtitle" style={{ textAlign: "center", marginTop: "var(--orbit-space-sm)" }}>
              {t(product.summary_key)}
            </p>
            {heroContext && (
              <p className="orbit-hero-design-subtitle" style={{ textAlign: "center", marginTop: "var(--orbit-space-xs)", fontStyle: "italic", color: "rgba(255, 255, 255, 0.8)" }}>
                {heroContext}
              </p>
            )}
            <div style={{ 
              display: "flex", 
              gap: "var(--orbit-space-sm)", 
              alignItems: "center", 
              justifyContent: "center",
              marginTop: "var(--orbit-space-md)",
              flexWrap: "wrap"
            }}>
              <span className="orbit-body-sm" style={{ color: "rgba(255, 255, 255, 0.95)" }}>
                {product.access === "free" ? t("catalog.product.access.free") : t("catalog.product.access.paid")}
              </span>
              {product.badge && (
                <span className="orbit-badge-xs" style={{ background: "rgba(255, 255, 255, 0.2)", color: "rgba(255, 255, 255, 0.95)" }}>
                  {t(`catalog.badge.${product.badge}`, product.badge)}
                </span>
              )}
            </div>
            <div className="orbit-hero-design-ctas" style={{ marginTop: "var(--orbit-space-lg)" }}>
              <Link
                href={product.link || `/catalog/product/${product.id}`}
                className="orbit-button orbit-button-primary orbit-button-hero"
              >
                {t(product.cta, product.cta)}
              </Link>
              <Link href="/catalog" className="orbit-button orbit-button-secondary orbit-button-hero">
                {t("catalog.product.hero.back", "Назад в каталог")}
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Content Section */}
      <section className="orbit-hero-content-block">
        <div className="orbit-hero-content-container">
          <section className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)" }}>
            <OrientationRail
              sectionLabel={t("dashboard.orientation.section.catalog", "КАТАЛОГ · Сервис")}
              metaLabel={t("catalog.product.orientation.meta", "Разбор сервиса")}
            />
            <ul className="orbit-list-unstyled" style={{ marginTop: "var(--orbit-space-md)" }}>
              {product.author_key && <li className="orbit-body-sm">{t(product.author_key)}</li>}
              {product.delivery_key && <li className="orbit-body-sm">{t(product.delivery_key)}</li>}
              {product.price_key && <li className="orbit-body-sm">{t(product.price_key)}</li>}
            </ul>
          </section>

          {featureCards.length > 0 && (
            <section className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)", marginTop: "var(--orbit-space-xl)" }}>
          <h2 className="orbit-display-sm">{t("catalog.product.section.features.title", "Что ты получаешь")}</h2>
          <p className="orbit-body-sm orbit-text-muted">{t("catalog.product.section.features.body", "Каждый сервис собран так, чтобы сразу было понятно: что ты получаешь и какой следующий шаг.")}</p>
          <div className="orbit-card-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", marginTop: "var(--orbit-space-1)" }}>
            {featureCards.map((feature) => (
              <MeaningCard key={feature.title} label={feature.title} body={<p>{feature.body}</p>} />
            ))}
          </div>
        </section>
      )}

          {hasRequirementsCopy && (
            <section className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)", marginTop: "var(--orbit-space-xl)" }}>
          <h2 className="orbit-display-sm">{requirementsTitle}</h2>
          {requirementsBody && <p className="orbit-body-sm orbit-text-muted">{requirementsBody}</p>}
          {requirementItems.length > 0 && (
            <ul className="orbit-list-unstyled" style={{ marginTop: "var(--orbit-space-1)", paddingLeft: "var(--orbit-space-2)" }}>
              {requirementItems.map((item) => (
                <li key={item} className="orbit-body-sm">{item}</li>
              ))}
            </ul>
          )}
        </section>
      )}

          <section className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)", marginTop: "var(--orbit-space-xl)" }}>
            <h2 className="orbit-display-sm">{t("catalog.product.section.context.title", "Где использовать этот сервис")}</h2>
        <p className="orbit-body-sm orbit-text-muted">{t("catalog.product.section.context.body", "Сервис встроен в твой обычный путь: профиль, Today, weekly focus и углубленные разборы.")}</p>
        <div className="orbit-card-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", marginTop: "var(--orbit-space-1)" }}>
          <MeaningCard
            label={t("catalog.product.section.context.featureOne", "Связь с основным маршрутом")}
            body={<p>{t("catalog.product.section.context.featureOne.body", "Этот сервис не начинается с нуля: он продолжает уже собранную основу и не ломает ожидания между экранами.")}</p>}
          />
          <MeaningCard
            label={t("catalog.product.section.context.featureTwo", "Аккаунт и сохранение")}
            body={<p>{t("catalog.product.section.context.featureTwo.body", "Данные профиля, результаты и связанные материалы сохраняются внутри аккаунта и остаются доступны в общем потоке.")}</p>}
          />
        </div>
      </section>

          <section className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)", marginTop: "var(--orbit-space-xl)" }}>
            <h2 className="orbit-display-sm">{t("catalog.product.section.category.title", "Где сервис находится в каталоге")}</h2>
        <p className="orbit-body-sm orbit-text-muted">{t("catalog.product.section.category.body", "Этот раздел показывает, где сервис живет в каталоге и как в него приходят из соседних сценариев и карточек.")}</p>
        {placements.length === 0 ? (
          <p className="orbit-body-sm orbit-text-muted">{t("catalog.product.section.category.empty", "Этот сервис пока не привязан к навигации каталога. Открой его через кнопку выше и добавь в закладки.")}</p>
        ) : (
          <ul className="orbit-list-unstyled" style={{ marginTop: "var(--orbit-space-1)" }}>
            {placements.map(({ column, section }) => (
              <li key={`${column.slug}-${section.slug}`} className="orbit-card" style={{ padding: "var(--orbit-space-md)", marginBottom: "var(--orbit-space-sm)" }}>
                <div style={{ marginBottom: "var(--orbit-space-xs)" }}>
                  <strong className="orbit-body-sm">{t(column.title_key)}</strong>
                  <p className="orbit-body-sm orbit-text-muted">{t(section.title_key)}</p>
                </div>
                {column.href && (
                  <Link href={column.href} className="orbit-link-subtle">
                    {t("catalog.product.category.link", "Открыть категорию →")}
                  </Link>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

          {relatedProducts.length > 0 && (
            <section className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)", marginTop: "var(--orbit-space-xl)" }}>
          <h2 className="orbit-display-sm">{t("catalog.product.section.related.title", "Соседние сервисы в этом разделе")}</h2>
          <p className="orbit-body-sm orbit-text-muted">{t("catalog.product.section.related.body", "Похожие сервисы в том же разделе, чтобы пользователь видел следующий логичный шаг, а не упирался в один экран.")}</p>
          <div className="orbit-card-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", marginTop: "var(--orbit-space-1)" }}>
            {relatedProducts.map((entry) => (
              <MeaningCard
                key={entry.id}
                label={t(entry.title_key)}
                body={<p>{t(entry.summary_key)}</p>}
                cta={
                  <Link href={`/catalog/product/${entry.id}`} className="orbit-link-subtle">
                    {t("catalog.product.category.link", "Открыть категорию →")}
                  </Link>
                }
              />
            ))}
          </div>
        </section>
      )}

          <section className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)", marginTop: "var(--orbit-space-xl)" }}>
            <h2 className="orbit-display-sm">{t("catalog.product.section.recos.title", "Что открыть дальше")}</h2>
        <p className="orbit-body-sm orbit-text-muted">{t("catalog.product.section.recos.body", "Соседние точки входа из той же зоны, если пользователь хочет углубиться или сменить угол разбора.")}</p>
        <CatalogRecommendationGrid slug={primaryPlacement?.column.slug} limit={3} />
      </section>

          {bridgeTitle ? (
            <CatalogCallout eyebrow={t("catalog.index.quote.eyebrow")} title={bridgeTitle} body={bridgeBody ?? ""}>
              <Link
                href={product.link || `/catalog/product/${product.id}`}
                className="orbit-button orbit-button-primary"
              >
                {bridgeCta}
              </Link>
            </CatalogCallout>
          ) : (
            <CatalogCallout
              eyebrow={t("catalog.index.quote.eyebrow")}
              title={t("catalog.product.callout.title", "Переходы между сервисами должны быть простыми")}
              body={t("catalog.product.callout.body", "Любой вход должен возвращать пользователя в единый язык: профиль, Today, weekly focus и понятный следующий сервис по задаче.")}
            />
          )}
        </div>
      </section>
    </main>
  );
}
