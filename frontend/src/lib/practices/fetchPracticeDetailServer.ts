/** Server-only practice lookups for metadata / SSR / soft-404. */

export type PracticeDetailMeta = {
  id: string;
  title: string;
  description: string;
  is_free?: boolean;
  access_level?: string;
  duration_minutes?: number | null;
  difficulty?: string | null;
  instructions?: string[] | null;
  tags?: string[] | null;
};

export type PracticeDetailLookup =
  | { status: "ok"; practice: PracticeDetailMeta }
  | { status: "missing" }
  | { status: "unavailable" };

export type PracticeCatalogEntry = {
  id: string;
  title: string;
  description: string;
  duration_minutes?: number | null;
  difficulty?: string | null;
  is_free?: boolean;
};

function apiBase(): string {
  return (
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    process.env.PUBLIC_API_URL ||
    "http://localhost:8080"
  ).replace(/\/$/, "");
}

export async function lookupPracticeDetail(practiceId: string): Promise<PracticeDetailLookup> {
  const id = practiceId.trim();
  if (!id) return { status: "missing" };

  try {
    const res = await fetch(`${apiBase()}/practices/${encodeURIComponent(id)}`, {
      headers: { Accept: "application/json", "Accept-Language": "ru" },
      cache: "force-cache",
    } satisfies RequestInit);
    if (res.status === 404) return { status: "missing" };
    if (!res.ok) return { status: "unavailable" };
    const data = (await res.json()) as PracticeDetailMeta;
    if (!data?.id || !data?.title) return { status: "unavailable" };
    return { status: "ok", practice: data };
  } catch {
    return { status: "unavailable" };
  }
}

/** Free/public practices for SSR catalog (crawlers + first paint). */
export async function lookupPracticesCatalogServer(): Promise<PracticeCatalogEntry[]> {
  try {
    const res = await fetch(`${apiBase()}/practices?limit=40`, {
      headers: { Accept: "application/json", "Accept-Language": "ru" },
      cache: "force-cache",
    } satisfies RequestInit);
    if (!res.ok) return [];
    const data = (await res.json()) as unknown;
    const list = Array.isArray(data) ? data : [];
    return list
      .map((raw) => {
        const item = raw as PracticeCatalogEntry;
        if (!item?.id || !item?.title) return null;
        return {
          id: String(item.id),
          title: String(item.title),
          description: String(item.description || ""),
          duration_minutes: item.duration_minutes ?? null,
          difficulty: item.difficulty ?? null,
          is_free: item.is_free !== false,
        };
      })
      .filter((item): item is PracticeCatalogEntry => item != null)
      .filter((item) => item.is_free !== false)
      .slice(0, 24);
  } catch {
    return [];
  }
}
