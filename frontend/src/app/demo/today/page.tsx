"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { LoadingSpinner } from "@/components/orbit";
import { VALUE_FIRST_PATHS } from "@/lib/guestProfileDraft";

/** Launch v1: demo removed from path — redirect to value-first signup. */
export default function DemoTodayPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace(`${VALUE_FIRST_PATHS.welcome}?fresh=1`);
  }, [router]);

  return (
    <main className="orbit-page todayflow-serene" style={{ background: "#f3efe8", minHeight: "100dvh" }}>
      <div style={{ display: "grid", placeItems: "center", minHeight: "50dvh" }}>
        <LoadingSpinner size="lg" />
      </div>
    </main>
  );
}
