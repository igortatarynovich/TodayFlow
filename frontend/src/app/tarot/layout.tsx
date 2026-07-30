import type { ReactNode } from "react";
import { metadataForSegment } from "@/lib/seo/publicSeoPolicy";
import { TarotLayoutClient } from "./TarotLayoutClient";

export const metadata = metadataForSegment("tarot");

export default function TarotLayout({ children }: { children: ReactNode }) {
  return <TarotLayoutClient>{children}</TarotLayoutClient>;
}
