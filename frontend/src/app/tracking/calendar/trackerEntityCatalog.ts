/**
 * Типы и фильтр каталога аскез для мастера на `/tracking/calendar`.
 * Тексты шаблонов целей/привычек/категорий — `trackerEntityTemplateCatalog.ts` (RU/EN).
 */

export type TrackerEntityKind = "goal" | "habit" | "ascetic";

export type TrackerTemplateCategory = {
  id: string;
  label: string;
  description: string;
};

export type TrackerTemplateItem = {
  title: string;
  hint?: string;
};

export type TrackerTemplateGroup = {
  category: TrackerTemplateCategory;
  items: TrackerTemplateItem[];
};

/** Фильтр аскез по ключевым словам (title + description с API) */
export type AsceticCategoryFilter = {
  category: TrackerTemplateCategory;
  /** Подстрочные совпадения для RU и EN контента каталога */
  keywords: string[];
};

export function filterAsceticismsByCategory<T extends { title: string; description: string }>(
  list: T[],
  keywords: string[],
): T[] {
  if (!keywords.length) return list;
  return list.filter((a) => {
    const blob = `${a.title} ${a.description}`.toLowerCase();
    return keywords.some((k) => blob.includes(k.toLowerCase()));
  });
}
