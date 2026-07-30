import { metadataForSegment } from "@/lib/seo/publicSeoPolicy";

export const metadata = metadataForSegment("onboarding");

export default function OnboardingLayout({ children }: { children: React.ReactNode }) {
  return children;
}
