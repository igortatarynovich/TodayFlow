"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { ProductWebLanding } from "@/components/product-ui/ProductWebLanding";
import { useAuth } from "@/lib/useAuth";
import { buildAuthHref, resolveTargetAfterAuthSession } from "@/lib/authRedirect";
import { VALUE_FIRST_PATHS } from "@/lib/guestProfileDraft";
import { LoadingSpinner } from "@/components/orbit";

const SIGNUP_HREF = `${VALUE_FIRST_PATHS.welcome}?fresh=1`;
const LOGIN_HREF = buildAuthHref("login");

export default function HomePage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      void resolveTargetAfterAuthSession().then((target) => router.push(target));
    }
  }, [isAuthenticated, authLoading, router]);

  if (authLoading || isAuthenticated) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "60vh" }}>
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return <ProductWebLanding signupHref={SIGNUP_HREF} loginHref={LOGIN_HREF} />;
}
