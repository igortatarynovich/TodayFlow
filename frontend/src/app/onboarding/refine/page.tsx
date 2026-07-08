"use client";

import { Suspense } from "react";
import OnboardingRefinePageInner from "./OnboardingRefinePageInner";

export default function OnboardingRefinePage() {
  return (
    <Suspense fallback={null}>
      <OnboardingRefinePageInner />
    </Suspense>
  );
}
