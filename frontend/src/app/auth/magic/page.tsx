"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { postJson } from "@/lib/api";
import { claimGuestProfileAfterAuth } from "@/lib/claimGuestProfile";
import { beginAuthSession } from "@/lib/authSession";
import { LoadingSpinner } from "@/components/orbit";

type MagicLoginResponse = {
  token: string;
  email: string;
};

function MagicLoginInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = searchParams.get("token");
    if (!token) {
      setError("Ссылка входа недействительна.");
      return;
    }

    void (async () => {
      try {
        const response = await postJson<MagicLoginResponse>("/auth/magic-login", { token });
        beginAuthSession(response.token);

        const claim = await claimGuestProfileAfterAuth();
        if (claim.status === "ready") {
          router.replace(claim.profilePath);
          return;
        }
        if (claim.status === "needs_refine") {
          router.replace(claim.refinePath);
          return;
        }
        router.replace("/profile");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Не удалось войти по ссылке.");
      }
    })();
  }, [router, searchParams]);

  if (error) {
    return (
      <main className="orbit-page orbit-auth-page" style={{ padding: "2rem" }}>
        <p>{error}</p>
      </main>
    );
  }

  return (
    <main className="orbit-page orbit-auth-page">
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "50vh", gap: "0.75rem" }}>
        <LoadingSpinner size="lg" />
        <span>Открываем твою карту…</span>
      </div>
    </main>
  );
}

export default function MagicLoginPage() {
  return (
    <Suspense fallback={null}>
      <MagicLoginInner />
    </Suspense>
  );
}
