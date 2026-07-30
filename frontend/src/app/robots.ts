import type { MetadataRoute } from "next";
import { ROBOTS_DISALLOW_PREFIXES } from "@/lib/seo/publicSeoPolicy";

function siteOrigin(): string {
  return (process.env.NEXT_PUBLIC_BASE_URL || "https://todayflow.today").replace(/\/$/, "");
}

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: [...ROBOTS_DISALLOW_PREFIXES],
    },
    sitemap: `${siteOrigin()}/sitemap.xml`,
    host: siteOrigin(),
  };
}
