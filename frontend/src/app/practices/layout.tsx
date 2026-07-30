import { metadataForSegment } from "@/lib/seo/publicSeoPolicy";

export const metadata = metadataForSegment("practices");

export default function PracticesLayout({ children }: { children: React.ReactNode }) {
  return children;
}
