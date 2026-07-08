import navigation from "../../../CONTENT/catalog/navigation.json";
import recommendations from "../../../CONTENT/catalog/recommendations.json";
import productsData from "../../../CONTENT/catalog/products.json";

export type CatalogProduct = {
  id: string;
  title_key: string;
  summary_key: string;
  cta: string;
  link: string;
  access: "free" | "paid";
  badge?: string;
  image?: string;
  author_key?: string;
  delivery_key?: string;
  price_key?: string;
};

export type CatalogNavigation = typeof navigation;
export type CatalogRecommendationMap = Record<string, { product_id: string; badge?: string; image?: string }[]>;
type CatalogColumn = CatalogNavigation["columns"][number];
type CatalogSection = CatalogColumn["sections"][number];

const productsMap = new Map<string, CatalogProduct>();
for (const product of productsData.products as CatalogProduct[]) {
  productsMap.set(product.id, product);
}

export const catalogNavigation = navigation as CatalogNavigation;
export const catalogRecommendations = recommendations as CatalogRecommendationMap;
export const catalogProducts = productsData.products as CatalogProduct[];

export function getProduct(productId: string): CatalogProduct | undefined {
  return productsMap.get(productId);
}

export function getProductDetailPath(productId: string) {
  return `/catalog/product/${productId}`;
}

export function getRecommendationCards(slug?: string) {
  const key = slug ?? "default";
  return catalogRecommendations[key] ?? catalogRecommendations.default ?? [];
}

export function getProductPlacements(productId: string) {
  const placements: { column: CatalogColumn; section: CatalogSection }[] = [];
  for (const column of catalogNavigation.columns) {
    for (const section of column.sections) {
      if (section.items.some((item) => item.product_id === productId)) {
        placements.push({ column, section });
      }
    }
  }
  return placements;
}
