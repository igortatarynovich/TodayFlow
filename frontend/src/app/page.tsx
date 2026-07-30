"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { ProductWebLanding } from "@/components/product-ui/ProductWebLanding";
import { useAuth } from "@/lib/useAuth";
import { buildAuthHref, resolveTargetAfterAuthSession } from "@/lib/authRedirect";
import { VALUE_FIRST_PATHS } from "@/lib/guestProfileDraft";

const SIGNUP_HREF = `${VALUE_FIRST_PATHS.welcome}?fresh=1`;
const LOGIN_HREF = buildAuthHref("login");

/**
 * Always render the marketing landing in HTML (crawlers + first paint).
 * Authed users redirect after session resolve — do not replace the page with a spinner
 * while auth is still loading (that emptied SSR for search/robots).
 */
export default function HomePage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      void resolveTargetAfterAuthSession().then((target) => router.push(target));
    }
  }, [isAuthenticated, authLoading, router]);

  return <ProductWebLanding signupHref={SIGNUP_HREF} loginHref={LOGIN_HREF} />;
}
