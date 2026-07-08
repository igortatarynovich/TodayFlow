export type ProfileHeaderVariant = "a" | "b" | "c";

export function parseProfileHeaderVariant(raw: string | null | undefined): ProfileHeaderVariant {
  const v = raw?.trim().toLowerCase();
  if (v === "b" || v === "c") return v;
  return "a";
}

/** Порядок визуальной важности: primary → secondary → tertiary */
export function heroTierOrder(variant: ProfileHeaderVariant): {
  primary: "archetype" | "number" | "sign";
  secondary: "archetype" | "number" | "sign";
  tertiary: "archetype" | "number" | "sign";
} {
  switch (variant) {
    case "b":
      return { primary: "number", secondary: "archetype", tertiary: "sign" };
    case "c":
      return { primary: "sign", secondary: "number", tertiary: "archetype" };
    default:
      return { primary: "archetype", secondary: "number", tertiary: "sign" };
  }
}

export const HEADER_VARIANT_META: Record<
  ProfileHeaderVariant,
  { label: string; title: string; primaryHero: string; query: string }
> = {
  a: {
    label: "A",
    title: "Архетип главный",
    primaryHero: "Архетип — бренд пользователя",
    query: "a",
  },
  b: {
    label: "B",
    title: "Число главное",
    primaryHero: "Life Path — якорь памяти",
    query: "b",
  },
  c: {
    label: "C",
    title: "Знак главный",
    primaryHero: "Солнце — астрологический вход",
    query: "c",
  },
};

/** Каноническая иерархия ценности (после выбора победителя A/B/C). */
export const CANONICAL_VALUE_HIERARCHY = ["archetype", "number", "sign"] as const;
