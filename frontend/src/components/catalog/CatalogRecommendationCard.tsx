import Link from "next/link";
import { t } from "@/lib/i18n";
import type { CatalogProduct } from "@/data/catalog";
import { getProductDetailPath } from "@/data/catalog";

type Props = {
  product: CatalogProduct;
  badge?: string;
  theme?: string;
  className?: string;
};

export function CatalogRecommendationCard({ product, badge, theme, className }: Props) {
  const badgeKey = badge ?? product.badge;
  const themeClass = theme ? `catalog-card-image catalog-card-image--${theme}` : undefined;
  const classes = ["catalog-card"];
  if (themeClass) {
    classes.push("catalog-card--with-image");
  }
  if (className) {
    classes.push(className);
  }

  return (
    <div className={classes.join(" ")}>
      {themeClass && <div className={themeClass} aria-hidden="true" />}
      <div className="catalog-card-tag">
        {badgeKey ? t(`catalog.badge.${badgeKey}`, badgeKey) : t("catalog.badge.top", "Popular")}
      </div>
      <h3>{t(product.title_key)}</h3>
      <p>{t(product.summary_key)}</p>
      <Link href={getProductDetailPath(product.id)} className="catalog-card-cta">
        {t(product.cta, product.cta)}
      </Link>
    </div>
  );
}
