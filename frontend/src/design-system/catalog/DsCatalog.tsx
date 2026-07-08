"use client";

import { dsAppNavItemsRu } from "@/components/product-ui/productWebShellChrome";
import {
  DsBody,
  DsButton,
  DsCaption,
  DsCard,
  DsCheckbox,
  DsChipField,
  DsClassifier,
  DsDisplayTitle,
  DsEyebrow,
  DsFeatureTile,
  DsHeadline,
  DsInsightRow,
  DsInsightTile,
  DsMobileTabBar,
  DsOrbitalViz,
  DsPulseCard,
  DsRitualGate,
  DsRitualGateSection,
  DsSearchField,
  DsStatusBadge,
  DsSubtitle,
  DsTextField,
  DsThemePanel,
  DsTitle,
  DsFeatureIcon,
  IconCalendar,
  IconMoon,
  IconSparkles,
} from "@/design-system";
import { DS_FIGMA_MAP } from "@/design-system/registry/figmaMap";
import cat from "@/design-system/catalog/dsCatalog.module.css";

function CatalogSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className={cat.section}>
      <DsEyebrow>{title}</DsEyebrow>
      <div className={cat.divider} />
      {children}
    </section>
  );
}

function ColorSwatch({ name, token }: { name: string; token: string }) {
  return (
    <div className={cat.colorSwatch}>
      <div className={cat.colorChip} style={{ background: `var(${token})` }} />
      <p className={cat.colorLabel}>
        {name}
        <br />
        <code>{token}</code>
      </p>
    </div>
  );
}

function SpacingBlock({ label, size }: { label: string; size: string }) {
  return (
    <div className={cat.spacingBlock}>
      <div className={cat.spacingBar} style={{ width: size, height: size }} />
      <DsCaption>{label}</DsCaption>
    </div>
  );
}

export function DsCatalog() {
  return (
    <div className={cat.page} data-testid="ds-catalog">
      <header className={cat.hero}>
        <DsDisplayTitle size="lg">TodayFlow Design System</DsDisplayTitle>
        <DsBody muted>
          Product UI V1 — зеркало Figma <code>TodayFlow_DesignSystem</code>. Меняйте токены в{" "}
          <code>todayflow-foundation.css</code>, компоненты в <code>@/design-system</code>.
        </DsBody>
      </header>

      <CatalogSection title="1. Typography">
        <div className={cat.typeGrid}>
          <DsDisplayTitle size="xl">Display XL</DsDisplayTitle>
          <DsDisplayTitle size="lg">Display L</DsDisplayTitle>
          <DsHeadline>H1 Headline</DsHeadline>
          <DsTitle>H2 Title</DsTitle>
          <DsSubtitle>H3 Subtitle</DsSubtitle>
          <DsBody size="lg">Body L — operating system for self-knowledge.</DsBody>
          <DsBody>Body M — operating system for self-knowledge.</DsBody>
          <DsBody size="sm">Body S — operating system for self-knowledge.</DsBody>
          <DsCaption>Caption — operating system for self-knowledge.</DsCaption>
        </div>
      </CatalogSection>

      <CatalogSection title="2. Colors">
        <div className={cat.colorGrid}>
          <ColorSwatch name="Page" token="--tf-page" />
          <ColorSwatch name="Cream 300" token="--tf-cream-300" />
          <ColorSwatch name="Gold" token="--tf-accent-gold" />
          <ColorSwatch name="Ink" token="--tf-ink" />
          <ColorSwatch name="Dark" token="--tf-surface-dark" />
          <ColorSwatch name="Success" token="--tf-semantic-success" />
          <ColorSwatch name="Alert" token="--tf-semantic-alert" />
          <ColorSwatch name="Error" token="--tf-semantic-error" />
        </div>
      </CatalogSection>

      <CatalogSection title="3. Spacing">
        <div className={cat.spacingRow}>
          <SpacingBlock label="space-2 · 8px" size="var(--tf-ds-space-2)" />
          <SpacingBlock label="space-4 · 16px" size="var(--tf-ds-space-4)" />
          <SpacingBlock label="space-6 · 24px" size="var(--tf-ds-space-6)" />
          <SpacingBlock label="space-8 · 32px" size="var(--tf-ds-space-8)" />
        </div>
      </CatalogSection>

      <CatalogSection title="4. Card Styles">
        <div className={cat.cardGrid}>
          <DsCard variant="standard">
            <DsTitle>Daily Intention</DsTitle>
            <DsBody muted>A warm minimal space for your recurring reflections.</DsBody>
            <DsStatusBadge>Active journey</DsStatusBadge>
          </DsCard>
          <DsCard variant="glass">
            <DsTitle>Frosted Clarity</DsTitle>
            <DsBody muted>Translucent layers for overlaying insights.</DsBody>
          </DsCard>
          <DsCard variant="orbital">
            <DsTitle>Cosmic Map</DsTitle>
            <DsBody muted>Background concentric rings represent cycles.</DsBody>
          </DsCard>
          <DsCard variant="feature">
            <DsTitle>Sacred Growth</DsTitle>
            <DsBody>Full-bleed warm gradient for high-priority features.</DsBody>
          </DsCard>
          <DsCard variant="dark">
            <DsTitle>Theme of the Day</DsTitle>
            <DsBody muted>Dark insight surface for hero themes.</DsBody>
          </DsCard>
          <DsCard variant="insight">
            <DsTitle>Insight Card</DsTitle>
            <DsBody muted>Light bordered card for secondary insights.</DsBody>
          </DsCard>
        </div>
      </CatalogSection>

      <CatalogSection title="5. Interaction Elements">
        <div className={cat.row}>
          <DsButton>Primary</DsButton>
          <DsButton variant="secondary">Secondary</DsButton>
          <DsButton variant="ghost">Ghost</DsButton>
          <DsButton variant="destructive">Destructive</DsButton>
          <DsButton disabled>Disabled</DsButton>
        </div>
      </CatalogSection>

      <CatalogSection title="6. Forms & Selection">
        <div className={cat.formGrid}>
          <DsTextField label="Personal Archetype" value="The Explorer" />
          <DsSearchField placeholder="Search practices…" icon={<IconSparkles />} />
          <DsChipField label="Sep 24, 2024" icon={<IconCalendar />} />
          <DsCheckbox checked aria-label="Remember my daily ritual" />
        </div>
      </CatalogSection>

      <CatalogSection title="7. System Classifiers">
        <div className={cat.row}>
          <DsClassifier label="Full Moon" icon={<IconMoon />} />
          <DsClassifier label="The Tower" icon={<IconSparkles />} />
          <DsClassifier label="Life Path 7" />
        </div>
      </CatalogSection>

      <CatalogSection title="9. Orbital Systems">
        <DsOrbitalViz
          nodes={[
            { id: "sun", label: "Sun", icon: <IconSparkles />, style: { top: "18%", left: "68%" } },
            { id: "moon", label: "Moon", icon: <IconMoon />, style: { top: "32%", left: "14%" } },
          ]}
        />
      </CatalogSection>

      <CatalogSection title="Mobile · Ritual Gates">
        <DsRitualGateSection eyebrow="Откройте свой день" hint="Выберите карту и число, чтобы день стал личным">
          <DsRitualGate kind="tarot" title="Карта дня" hint="Нажмите, чтобы открыть" />
          <DsRitualGate kind="number" title="Число дня" hint="Нажмите, чтобы раскрыть" />
        </DsRitualGateSection>
        <DsPulseCard label="Энергия дня" value="Спокойная концентрация" hint="Откроется после ритуала" />
        <DsInsightRow label="Тема" title="Внутренняя ясность" body="Короткий инсайт дня." />
        <div className={cat.mobilePreview}>
          <DsMobileTabBar
            items={dsAppNavItemsRu().map((item) => ({
              href: item.href,
              label: item.label,
              icon: <item.icon />,
            }))}
            activeHref="/today"
          />
        </div>
      </CatalogSection>

      <CatalogSection title="Web · Tiles">
        <div className={cat.cardGrid}>
          <DsFeatureTile
            icon={<DsFeatureIcon name="compass" />}
            title="Living Map"
            body="Dynamic visualization of your cosmic blueprint."
          />
          <DsInsightTile label="Tarot" title="The Star" visual={<span>✦</span>} />
        </div>
        <DsThemePanel eyebrow="Theme of the Day" title="Inner Clarity" tags={["Solitude", "Synthesis"]} body="Structured introspection." />
      </CatalogSection>

      <CatalogSection title="Registry · Figma → Code">
        <pre className={cat.registry}>{JSON.stringify(DS_FIGMA_MAP, null, 2)}</pre>
      </CatalogSection>
    </div>
  );
}
