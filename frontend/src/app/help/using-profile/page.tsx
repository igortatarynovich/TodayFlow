"use client";

import Link from "next/link";
import helpUsingProfile from "@/data/helpUsingProfile.ru.json";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { DsButton } from "@/design-system";

export default function HelpUsingProfilePage() {
  const u = helpUsingProfile;
  return (
    <ProductPageScreen
      testId="help-using-profile-page"
      title={u.title}
      subtitle={u.lead}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <p className="orbit-body-xs" style={{ margin: "0 0 var(--orbit-space-lg)" }}>
        <Link href="/help" style={{ color: "#a67c3a", fontWeight: 700, textDecoration: "none" }}>
          ← {u.backHub}
        </Link>
      </p>

      <h2 className="orbit-heading-3" style={{ margin: "0 0 var(--orbit-space-sm)", color: "#5c4426" }} id="foundation">
        {u.foundationTitle}
      </h2>
      <p className="orbit-body-sm" style={{ margin: "0 0 var(--orbit-space-xl)", color: "#57534e", lineHeight: 1.65 }}>
        {u.foundationBody}
      </p>

      <h2 className="orbit-heading-3" style={{ margin: "0 0 var(--orbit-space-sm)", color: "#5c4426" }} id="strengths">
        {u.strengthsTitle}
      </h2>
      <p className="orbit-body-sm" style={{ margin: "0 0 var(--orbit-space-xl)", color: "#57534e", lineHeight: 1.65 }}>
        {u.strengthsBody}
      </p>

      <h2 className="orbit-heading-3" style={{ margin: "0 0 var(--orbit-space-sm)", color: "#5c4426" }} id="map">
        {u.mapTitle}
      </h2>
      <p className="orbit-body-sm" style={{ margin: "0 0 var(--orbit-space-lg)", color: "#57534e", lineHeight: 1.65 }}>
        {u.mapBody}
      </p>
      <p className="orbit-body-sm" style={{ margin: "0 0 var(--orbit-space-2xl)", color: "#57534e" }}>
        <Link href="/help#profile-sections" style={{ color: "#a67c3a", fontWeight: 700 }}>
          {u.profileTabsLink} →
        </Link>
      </p>

      <Link href="/profile"><DsButton variant="primary">{u.openProfileCta}</DsButton></Link>
    </ProductPageScreen>
  );
}
