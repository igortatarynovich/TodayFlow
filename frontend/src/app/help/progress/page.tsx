"use client";

import Link from "next/link";
import help from "@/data/growthIndexHelp.ru.json";
import helpHub from "@/data/helpHub.ru.json";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { DsButton } from "@/design-system";

export default function GrowthIndexHelpPage() {
  const data = help;
  return (
    <ProductPageScreen
      testId="help-progress-page"
      eyebrow={data.pageEyebrow}
      title={data.title}
      subtitle={data.lead}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <p className="orbit-body-xs" style={{ margin: "0 0 var(--orbit-space-lg)" }}>
        <Link href="/help" style={{ color: "#a67c3a", fontWeight: 700, textDecoration: "none" }}>
          ← {helpHub.title}
        </Link>
      </p>

      <h2 className="orbit-heading-3" style={{ margin: "0 0 var(--orbit-space-sm)", color: "#5c4426" }}>
        {data.formulaTitle}
      </h2>
      <p className="orbit-body-sm" style={{ margin: "0 0 var(--orbit-space-xl)", color: "#57534e", lineHeight: 1.65 }}>
        {data.formulaBody}
      </p>

      <h2 className="orbit-heading-3" style={{ margin: "0 0 var(--orbit-space-md)", color: "#5c4426" }}>
        {data.pillarsTitle}
      </h2>
      <ul style={{ margin: "0 0 var(--orbit-space-xl)", padding: 0, listStyle: "none", display: "grid", gap: "var(--orbit-space-lg)" }}>
        {data.pillars.map((pillar) => (
          <li
            key={pillar.title}
            style={{
              padding: "var(--orbit-space-md) var(--orbit-space-lg)",
              borderRadius: "16px",
              background: "rgba(255,253,249,0.95)",
              border: "1px solid rgba(201, 168, 115, 0.22)",
            }}
          >
            <p className="orbit-body-sm" style={{ margin: "0 0 0.35rem", fontWeight: 700, color: "#7c6242" }}>
              {pillar.title}
            </p>
            <p className="orbit-body-sm" style={{ margin: 0, color: "#44403c", lineHeight: 1.65 }}>
              {pillar.body}
            </p>
          </li>
        ))}
      </ul>

      <h2 className="orbit-heading-3" style={{ margin: "0 0 var(--orbit-space-sm)", color: "#5c4426" }}>
        {data.ringsTitle}
      </h2>
      <p className="orbit-body-sm" style={{ margin: "0 0 var(--orbit-space-xl)", color: "#57534e", lineHeight: 1.65 }}>
        {data.ringsBody}
      </p>

      <h2 className="orbit-heading-3" style={{ margin: "0 0 var(--orbit-space-sm)", color: "#5c4426" }}>
        {data.archetypeTitle}
      </h2>
      <p className="orbit-body-sm" style={{ margin: "0 0 var(--orbit-space-2xl)", color: "#57534e", lineHeight: 1.65 }}>
        {data.archetypeBody}
      </p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", alignItems: "center" }}>
        <Link href="/today"><DsButton variant="primary">{data.backLink}</DsButton></Link>
        <Link href="/profile"><DsButton variant="secondary">{data.profileLink}</DsButton></Link>
      </div>
    </ProductPageScreen>
  );
}
