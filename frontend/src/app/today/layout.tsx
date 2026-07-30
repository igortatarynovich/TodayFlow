import { Suspense } from "react";
import { metadataForSegment } from "@/lib/seo/publicSeoPolicy";

export const metadata = metadataForSegment("today");

export default function TodayLayout({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={null}>{children}</Suspense>;
}
