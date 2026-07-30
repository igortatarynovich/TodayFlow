import { Suspense, type ReactNode } from "react";
import { metadataForSegment } from "@/lib/seo/publicSeoPolicy";
import { GuestTodayPitchSsr } from "@/components/product-ui/GuestProductPitchSsr";

export const metadata = metadataForSegment("today");

/**
 * SSR pitch is always in the document for crawlers (avoids CSR bailout empty body).
 * Guest client page returns null; authenticated shell hides the pitch via CSS.
 */
export default function TodayLayout({ children }: { children: ReactNode }) {
  return (
    <>
      <GuestTodayPitchSsr />
      <Suspense fallback={null}>{children}</Suspense>
    </>
  );
}
