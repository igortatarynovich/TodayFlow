import { getProduct, getRecommendationCards } from "@/data/catalog";
import { CatalogRecommendationCard } from "./CatalogRecommendationCard";

type Props = {
  slug?: string;
  limit?: number;
  className?: string;
};

export function CatalogRecommendationGrid({ slug, limit, className }: Props) {
  const cards = getRecommendationCards(slug);
  const list = typeof limit === "number" ? cards.slice(0, limit) : cards;
  if (!list.length) {
    return null;
  }
  return (
    <div className={className ?? "catalog-grid"}>
      {list.map((card) => {
        const product = getProduct(card.product_id);
        if (!product) return null;
        return (
          <CatalogRecommendationCard
            key={product.id}
            product={product}
            badge={card.badge}
            theme={card.image}
          />
        );
      })}
    </div>
  );
}
