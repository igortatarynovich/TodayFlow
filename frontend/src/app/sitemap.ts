import type { MetadataRoute } from "next";
import { PUBLIC_SEO_BY_SEGMENT } from "@/lib/seo/publicSeoPolicy";

function siteOrigin(): string {
  return (process.env.NEXT_PUBLIC_BASE_URL || "https://todayflow.today").replace(/\/$/, "");
}

/** Marketing + guest-trial share surfaces only — personal shells stay out. */
const SITEMAP_PATHS: Array<{ path: string; changeFrequency: MetadataRoute.Sitemap[0]["changeFrequency"]; priority: number }> = [
  { path: "/", changeFrequency: "weekly", priority: 1 },
  { path: "/demo/today", changeFrequency: "weekly", priority: 0.9 },
  { path: "/compatibility", changeFrequency: "weekly", priority: 0.8 },
  { path: "/tarot", changeFrequency: "weekly", priority: 0.8 },
  { path: "/practices", changeFrequency: "weekly", priority: 0.8 },
  { path: "/help", changeFrequency: "monthly", priority: 0.5 },
  { path: "/pricing", changeFrequency: "monthly", priority: 0.5 },
  { path: "/terms", changeFrequency: "yearly", priority: 0.2 },
  { path: "/privacy", changeFrequency: "yearly", priority: 0.2 },
  { path: "/catalog", changeFrequency: "monthly", priority: 0.4 },
];

export default function sitemap(): MetadataRoute.Sitemap {
  const origin = siteOrigin();
  // Guard: only paths marked sitemap:true in policy (home + demo always included).
  const allowed = new Set(
    Object.entries(PUBLIC_SEO_BY_SEGMENT)
      .filter(([, route]) => route.sitemap)
      .map(([segment]) => `/${segment}`),
  );
  allowed.add("/");
  allowed.add("/demo/today");

  return SITEMAP_PATHS.filter((entry) => allowed.has(entry.path)).map((entry) => ({
    url: `${origin}${entry.path === "/" ? "" : entry.path}`,
    lastModified: new Date(),
    changeFrequency: entry.changeFrequency,
    priority: entry.priority,
  }));
}
