"use client";

import { useState, useEffect } from "react";
import { selectColdState, type ColdState } from "@/lib/coldStart";
import { OnboardingScreen1 } from "./OnboardingScreen1";
import { OnboardingScreen2 } from "./OnboardingScreen2";
import { OnboardingScreen3 } from "./OnboardingScreen3";
import { OnboardingScreen4 } from "./OnboardingScreen4";

export function OnboardingFlow() {
  const [currentScreen, setCurrentScreen] = useState(1);
  const [state, setState] = useState<ColdState | null>(null);

  useEffect(() => {
    setState(selectColdState());
  }, []);

  // При завершении онбординга сохраняем флаг
  useEffect(() => {
    if (currentScreen === 4) {
      const today = new Date().toDateString();
      const onboardingKey = `onboarding_completed_${today}`;
      localStorage.setItem(onboardingKey, "true");
    }
  }, [currentScreen]);

  const handleNext = () => {
    setCurrentScreen(prev => Math.min(prev + 1, 4));
  };

  const handleComplete = () => {
    setCurrentScreen(4);
  };

  if (!state) {
    return null;
  }

  switch (currentScreen) {
    case 1:
      return <OnboardingScreen1 state={state} onNext={handleNext} />;
    case 2:
      return <OnboardingScreen2 state={state} onNext={handleNext} />;
    case 3:
      return <OnboardingScreen3 state={state} onComplete={handleComplete} />;
    case 4:
      return <OnboardingScreen4 state={state} />;
    default:
      return <OnboardingScreen1 state={state} onNext={handleNext} />;
  }
}

