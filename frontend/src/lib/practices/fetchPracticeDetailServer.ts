/** Server-only practice detail lookup for metadata / soft-404. */

export type PracticeDetailMeta = {
  id: string;
  title: string;
  description: string;
  is_free?: boolean;
  access_level?: string;
};

export type PracticeDetailLookup =
  | { status: "ok"; practice: PracticeDetailMeta }
  | { status: "missing" }
  | { status: "unavailable" };

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
    // Plain RequestInit — avoid Next typed-fetch circular Promise inference in layouts.
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
