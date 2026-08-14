"use client";

import { dsAppNavItemsRu } from "@/components/product-ui/productWebShellChrome";
import {
  DsActionCard,
  DsAngle,
  DsAvatar,
  DsBody,
  DsButton,
  DsCallout,
  DsCaption,
  DsCard,
  DsCheckbox,
  DsChip,
  DsChipCluster,
  DsChipField,
  DsClassifier,
  DsDisplayTitle,
  DsDotMeter,
  DsEmph,
  DsEyebrow,
  DsFab,
  DsFeatureTile,
  DsHeadline,
  DsHeroBlock,
  DsInsightRow,
  DsInsightTile,
  DsListRow,
  DsMetricCard,
  DsMobileTabBar,
  DsNumber,
  DsOrbitalViz,
  DsPlanet,
  DsPulseCard,
  DsQuote,
  DsRadialMeter,
  DsRitualGate,
  DsRitualGateSection,
  DsSearchField,
  DsSpectrum,
  DsStarDivider,
  DsStatusBadge,
  DsSubtitle,
  DsSurface,
  DsTextField,
  DsThemePanel,
  DsTitle,
  DsWindowCard,
  DsZodiac,
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
          <ColorSwatch name="Ink primary" token="--tf-ink" />
          <ColorSwatch name="Ink secondary" token="--tf-ink-secondary" />
          <ColorSwatch name="Ink quiet" token="--tf-ink-quiet" />
          <ColorSwatch name="Ink accent" token="--tf-ink-accent" />
          <ColorSwatch name="Ink action" token="--tf-ink-action" />
          <ColorSwatch name="Page" token="--tf-page" />
          <ColorSwatch name="Gold CTA" token="--tf-accent-gold" />
          <ColorSwatch name="Success" token="--tf-semantic-success" />
        </div>
      </CatalogSection>

      <CatalogSection title="2b. Semantic layers">
        <DsQuote kicker="Сегодня">Иногда лучший следующий шаг — перестать искать идеальный.</DsQuote>
        <div className={cat.cardGrid} style={{ marginTop: "1.25rem" }}>
          <DsCallout tone="insight" label="main" icon="spark" title="Сегодня не стоит принимать решение быстро.">
            <p>
              Импульс и осторожность сейчас находятся в конфликте. Выбери{" "}
              <DsEmph>стабильность</DsEmph>, а не скорость.
            </p>
          </DsCallout>
          <DsCallout
            tone="avoid"
            label="attention"
            icon="flag"
            title="Ты можешь перепутать желание ускориться с необходимостью действовать."
          />
          <DsCallout tone="help" label="help" icon="sun" title="Разговор окажется важнее действий." />
          <DsCallout tone="practice" label="next_step" icon="arrowDown" title="Сделай один короткий шаг до обеда.">
            <p>Практика — не список задач. Один конкретный жест.</p>
          </DsCallout>
        </div>
        <DsBody size="sm" tone="quiet" className={cat.registry}>
          Tone (rail) и label (capsule) — независимые оси. Primary CTA остаётся золотой; action-ink — только
          ссылки/интерактивный текст.
        </DsBody>
      </CatalogSection>

      <CatalogSection title="Form Kit · Surfaces (tone only)">
        <DsBody size="sm" muted>
          §15.8 — <code>DsSurface</code> = visual shell; <code>DsCard</code> = pad/gap on a tone. Color from{" "}
          <code>--tf-*</code> / <code>--day-*</code>, not the kit sheet neon.
        </DsBody>
        <div className={cat.cardGrid} style={{ marginTop: "1rem" }}>
          {(["none", "subtle", "solid", "glass", "accent"] as const).map((tone) => (
            <DsSurface key={tone} tone={tone} className={cat.formKitSurface}>
              <DsCaption>{tone}</DsCaption>
              <DsBody size="sm">Surface tone</DsBody>
            </DsSurface>
          ))}
        </div>
      </CatalogSection>

      <CatalogSection title="Form Kit · Primitives">
        <div className={cat.row}>
          <DsChip icon={<DsPlanet planet="moon" size={16} />}>Moon</DsChip>
          <DsChip variant="status">High energy</DsChip>
          <DsFab ariaLabel="Continue">→</DsFab>
          <DsAvatar label="A" />
          <DsZodiac sign="leo" size={28} />
          <DsNumber value={7} size={28} />
          <DsAngle angle="asc" size={28} />
        </div>
        <div className={cat.row} style={{ marginTop: "1rem", alignItems: "center" }}>
          <DsRadialMeter value={78} />
          <DsDotMeter value={4} />
          <div style={{ flex: 1, minWidth: "12rem" }}>
            <DsSpectrum value={0.62} lowLabel="Low" highLabel="High" />
          </div>
        </div>
        <DsStarDivider />
      </CatalogSection>

      <CatalogSection title="Form Kit · Compositions">
        <div className={cat.cardGrid}>
          <DsHeroBlock
            eyebrow="Clarity in focus"
            title="Сегодня держит ясность"
            body="Короткий день-бриф без локальной кожи."
            bleed={<DsPlanet planet="neptune" size={120} />}
            chips={<DsChipCluster><DsChip>Focus</DsChip></DsChipCluster>}
            fab={<DsFab ariaLabel="Open" size="sm">→</DsFab>}
          />
          <DsWindowCard
            title="Best window"
            startLabel="13:40"
            endLabel="16:20"
            spectrum={<DsSpectrum value={0.55} />}
          />
          <DsMetricCard value="78%" label="Energy" meter={<DsRadialMeter value={78} size={72} />} />
          <DsActionCard title="See your full day" action={<DsButton>Open</DsButton>} />
        </div>
        <DsCard tone="glass" size="compact">
          <DsListRow
            leading={<DsPlanet planet="moon" size={36} />}
            title="Moon in Virgo"
            subtitle="Detail before speed"
            onClick={() => undefined}
          />
        </DsCard>
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
          <DsCard variant="glass" size="compact">
            <DsTitle>Today Block</DsTitle>
            <DsBody muted>Compact Surface B pad — ScreenFlow panels without consumer overrides.</DsBody>
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
