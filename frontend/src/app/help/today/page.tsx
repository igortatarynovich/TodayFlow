"use client";

import Link from "next/link";
import helpToday from "@/data/helpToday.ru.json";
import helpHub from "@/data/helpHub.ru.json";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { DsButton } from "@/design-system";

export default function HelpTodayPage() {
  const t = helpToday;
  return (
    <ProductPageScreen
      testId="help-today-page"
      title={t.title}
      subtitle={t.lead}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <p className="orbit-body-xs" style={{ margin: "0 0 var(--orbit-space-lg)" }}>
        <Link href="/help" style={{ color: "#a67c3a", fontWeight: 700, textDecoration: "none" }}>
          ← {t.backHub}
        </Link>
      </p>

      <h2 className="orbit-heading-3" style={{ margin: "0 0 var(--orbit-space-sm)", color: "#5c4426" }}>
        {t.cycleTitle}
      </h2>
      <p className="orbit-body-sm" style={{ margin: "0 0 var(--orbit-space-xl)", color: "#57534e", lineHeight: 1.65 }}>
        {t.cycleBody}
      </p>

      <h2 className="orbit-heading-3" style={{ margin: "0 0 var(--orbit-space-sm)", color: "#5c4426" }}>
        {t.progressTitle}
      </h2>
      <p className="orbit-body-sm" style={{ margin: "0 0 var(--orbit-space-md)", color: "#57534e", lineHeight: 1.65 }}>
        {t.progressBody}
      </p>
      <p className="orbit-body-sm" style={{ margin: "0 0 var(--orbit-space-xl)", color: "#57534e" }}>
        <Link href="/help/rings" style={{ color: "#a67c3a", fontWeight: 700 }}>
          {t.progressRingsLink}
        </Link>
        {" · "}
        <Link href="/help/progress" style={{ color: "#a67c3a", fontWeight: 700 }}>
          {t.progressFormulaLink}
        </Link>
      </p>

      <h2 className="orbit-heading-3" style={{ margin: "0 0 var(--orbit-space-sm)", color: "#5c4426" }}>
        {t.profileTitle}
      </h2>
      <p className="orbit-body-sm" style={{ margin: "0 0 var(--orbit-space-2xl)", color: "#57534e", lineHeight: 1.65 }}>
        {t.profileBody}
      </p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem" }}>
        <Link href="/today"><DsButton variant="primary">{t.ctaToday}</DsButton></Link>
        <Link href="/help/using-profile"><DsButton variant="secondary">{helpHub.usingProfileCardTitle}</DsButton></Link>
      </div>
    </ProductPageScreen>
  );
}
