"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { ProductWebLanding } from "@/components/product-ui/ProductWebLanding";
import { useAuth } from "@/lib/useAuth";
import { buildAuthHref, resolveTargetAfterAuthSession } from "@/lib/authRedirect";

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

  return <ProductWebLanding loginHref={LOGIN_HREF} />;
}
