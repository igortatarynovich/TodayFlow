"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { FIRST_TODAY_PATH } from "@/lib/firstTodayState";
import { OnboardingProductLoading } from "@/components/onboarding/OnboardingProductShell";
import { LoadingSpinner } from "@/components/orbit";

/** Legacy deep link — Intent chips live inside First Today (placement C). */
export default function OnboardingIntentPage() {
  const router = useRouter();
  useEffect(() => {
    router.replace(FIRST_TODAY_PATH);
  }, [router]);
  return (
    <OnboardingProductLoading>
      <LoadingSpinner size="lg" />
    </OnboardingProductLoading>
  );
}
