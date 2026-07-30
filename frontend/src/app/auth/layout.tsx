import { metadataForSegment } from "@/lib/seo/publicSeoPolicy";

export const metadata = metadataForSegment("auth");

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return children;
}
