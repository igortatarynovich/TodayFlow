import type { ReactNode } from "react";
import { metadataForSegment } from "@/lib/seo/publicSeoPolicy";
import { GuestProfilePitchSsr } from "@/components/product-ui/GuestProductPitchSsr";

export const metadata = metadataForSegment("profile");

export default function ProfileLayout({ children }: { children: ReactNode }) {
  return (
    <>
      <GuestProfilePitchSsr />
      {children}
    </>
  );
}
