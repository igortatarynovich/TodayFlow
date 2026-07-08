"use client";

import Link from "next/link";
import helpHub from "@/data/helpHub.ru.json";
import { PROFILE_SECTION_IDS, PROFILE_SECTION_META } from "@/components/profile/profileSections";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { DsButton } from "@/design-system";

export default function HelpHubPage() {
  const hub = helpHub;

  const cards: { title: string; body: string; href: string; cta: string }[] = [
    {
      title: hub.todayCardTitle,
      body: hub.todayCardBody,
      href: "/help/today",
      cta: "Открыть",
    },
    {
      title: hub.usingProfileCardTitle,
      body: hub.usingProfileCardBody,
      href: "/help/using-profile",
      cta: "Открыть",
    },
    {
      title: hub.progressCardTitle,
      body: hub.progressCardBody,
      href: "/help/progress",
      cta: "Открыть",
    },
    {
      title: hub.ringsCardTitle,
      body: hub.ringsCardBody,
      href: "/help/rings",
      cta: "Открыть",
    },
  ];

  return (
    <ProductPageScreen
      testId="help-hub-page"
      eyebrow="TodayFlow"
      title={hub.title}
      subtitle={hub.intro}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <p className="orbit-body-xs orbit-text-muted" style={{ marginBottom: "var(--orbit-space-lg)" }}>
        Формат справки: коротко, по шагам, без длинной теории.
      </p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.65rem", marginBottom: "var(--orbit-space-lg)" }}>
        <Link href="/today"><DsButton variant="secondary">Открыть Today</DsButton></Link>
        <Link href="/tarot"><DsButton variant="secondary">Открыть Таро</DsButton></Link>
        <Link href="/compatibility"><DsButton variant="secondary">Открыть Compatibility</DsButton></Link>
        <Link href="/profile"><DsButton variant="secondary">Открыть профиль</DsButton></Link>
      </div>

      <div style={{ display: "grid", gap: "var(--orbit-space-md)", marginBottom: "var(--orbit-space-2xl)" }}>
        {cards.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="orbit-card todayflow-panel"
            style={{
              textDecoration: "none",
              padding: "var(--orbit-space-lg)",
              borderRadius: "20px",
              border: "1px solid rgba(201, 168, 115, 0.25)",
              display: "grid",
              gap: "0.5rem",
              transition: "box-shadow 0.2s ease",
            }}
          >
            <p className="orbit-heading-3" style={{ margin: 0, color: "#5c4426" }}>
              {card.title}
            </p>
            <p className="orbit-body-sm" style={{ margin: 0, color: "#57534e", lineHeight: 1.65 }}>
              {card.body}
            </p>
            <span className="orbit-body-xs" style={{ color: "#a67c3a", fontWeight: 700 }}>
              {card.cta} →
            </span>
          </Link>
        ))}
      </div>

      <h2 className="orbit-heading-3" style={{ margin: "0 0 var(--orbit-space-sm)", color: "#5c4426" }} id="profile-sections">
        {hub.profileSectionsTitle}
      </h2>
      <p className="orbit-body-sm" style={{ margin: "0 0 var(--orbit-space-lg)", color: "#57534e", lineHeight: 1.65 }}>
        {hub.profileSectionsIntro}
      </p>
      <ul style={{ margin: "0 0 var(--orbit-space-2xl)", padding: 0, listStyle: "none", display: "grid", gap: "var(--orbit-space-md)" }}>
        {PROFILE_SECTION_IDS.map((id) => {
          const meta = PROFILE_SECTION_META[id];
          return (
            <li
              key={id}
              className="orbit-card"
              style={{
                padding: "var(--orbit-space-md) var(--orbit-space-lg)",
                borderRadius: "16px",
                border: "1px solid rgba(201, 168, 115, 0.18)",
                background: "rgba(255,253,249,0.95)",
              }}
            >
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#7c6242" }}>
                {meta.label}
              </p>
              <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#44403c", lineHeight: 1.65 }}>
                {meta.description}
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.5rem 0 0" }}>
                <Link href={`/profile?section=${id}`} style={{ color: "#a67c3a", fontWeight: 700 }}>
                  Открыть в профиле →
                </Link>
              </p>
            </li>
          );
        })}
      </ul>

      <h2 className="orbit-heading-3" style={{ margin: "0 0 var(--orbit-space-sm)", color: "#5c4426" }}>
        {hub.accountCardTitle}
      </h2>
      <p className="orbit-body-sm" style={{ margin: "0 0 var(--orbit-space-lg)", color: "#57534e", lineHeight: 1.65 }}>
        {hub.accountCardBody}
      </p>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", marginBottom: "var(--orbit-space-2xl)" }}>
        <Link href={hub.accountHref}><DsButton variant="primary">{hub.accountLinkLabel}</DsButton></Link>
        <Link href={hub.settingsHref}><DsButton variant="secondary">{hub.settingsLinkLabel}</DsButton></Link>
      </div>

      <Link href="/today" className="orbit-body-sm" style={{ color: "#a67c3a", fontWeight: 700 }}>
        ← {hub.backToApp}
      </Link>
    </ProductPageScreen>
  );
}
