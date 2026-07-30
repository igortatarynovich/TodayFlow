import { metadataForSegment } from "@/lib/seo/publicSeoPolicy";

export const metadata = metadataForSegment("profile");

export default function ProfileLayout({ children }: { children: React.ReactNode }) {
  return children;
}
