"use client";

import { ProductWebLanding } from "@/components/product-ui/ProductWebLanding";

type Props = {
  signupHref: string;
  loginHref: string;
};

/** Product UI web landing (Figma web-landing). */
export function LandingPage(props: Props) {
  return <ProductWebLanding {...props} />;
}
