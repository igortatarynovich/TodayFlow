"use client";

import Link from "next/link";
import helpHub from "@/data/helpHub.ru.json";
import { HelpRingsDetail } from "@/components/help/HelpRingsDetail";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";

export default function HelpRingsPage() {
  return (
    <ProductPageScreen
      testId="help-rings-page"
      title={helpHub.ringsCardTitle}
      subtitle={helpHub.ringsCardBody}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <p className="orbit-body-xs" style={{ margin: "0 0 var(--orbit-space-lg)" }}>
        <Link href="/help" style={{ color: "#a67c3a", fontWeight: 700, textDecoration: "none" }}>
          ← Справка
        </Link>
      </p>
      <HelpRingsDetail />
    </ProductPageScreen>
  );
}
