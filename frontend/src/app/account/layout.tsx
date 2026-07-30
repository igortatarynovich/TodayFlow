import type { ReactNode } from "react";
import { metadataForSegment } from "@/lib/seo/publicSeoPolicy";
import "../compatibility/compatibility-desktop.css";

export const metadata = metadataForSegment("account");

export default function AccountLayout({ children }: { children: ReactNode }) {
  return children;
}
