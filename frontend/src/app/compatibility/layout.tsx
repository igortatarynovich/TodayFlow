import type { ReactNode } from "react";
import { metadataForSegment } from "@/lib/seo/publicSeoPolicy";
import "./compatibility-desktop.css";

export const metadata = metadataForSegment("compatibility");

export default function CompatibilitySectionLayout({ children }: { children: ReactNode }) {
  return children;
}
