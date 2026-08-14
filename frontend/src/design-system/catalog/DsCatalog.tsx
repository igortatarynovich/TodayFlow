"use client";

import { useId, useState } from "react";
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
  DsContentCard,
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
  DsLinearProgress,
  DsListPanel,
  DsListRow,
  DsMetric,
  DsMetricCard,
  DsMobileTabBar,
  DsNumber,
  DsOrbitalViz,
  DsOverlaySheet,
  DsPlanet,
  DsPulseCard,
  DsQuote,
  DsRadialMeter,
  DsRitualGate,
  DsRitualGateSection,
  DsSearchField,
  DsSectionHeader,
  DsSpectrum,
  DsStarDivider,
  DsStatusBadge,
  DsSubtitle,
  DsSurface,
  DsTarotFace,
  DsTextField,
  DsThemePanel,
  DsTitle,
  DsWaveMeter,
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
  const [overlayOpen, setOverlayOpen] = useState(false);
  const overlayTitleId = useId();

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
          §15.8 specimen — 100% sheet roles. Color from <code>--tf-*</code> / <code>--day-*</code>, not kit neon.
        </DsBody>
        <div className={cat.cardGrid} style={{ marginTop: "1rem" }} data-testid="form-kit-surfaces">
          {(["none", "subtle", "solid", "glass", "accent", "overlay"] as const).map((tone) => (
            <DsSurface key={tone} tone={tone} className={cat.formKitSurface}>
              <DsCaption>{tone}</DsCaption>
              <DsBody size="sm">{tone === "overlay" ? "Sheets only — opaque" : "Surface tone"}</DsBody>
            </DsSurface>
          ))}
        </div>
      </CatalogSection>

      <CatalogSection title="Form Kit · Buttons & FAB">
        <DsCaption>Primary / Secondary / Ghost / Icon × lg · md · sm + FAB</DsCaption>
        <div className={cat.row} style={{ marginTop: "0.75rem", flexWrap: "wrap", gap: "0.75rem" }}>
          <DsButton size="lg">Primary L</DsButton>
          <DsButton size="md">Primary M</DsButton>
          <DsButton size="sm">Primary S</DsButton>
          <DsButton variant="secondary" size="lg">
            Secondary L
          </DsButton>
          <DsButton variant="secondary" size="md">
            Secondary M
          </DsButton>
          <DsButton variant="ghost" size="md">
            Ghost
          </DsButton>
          <DsButton variant="icon" size="md" aria-label="Icon">
            →
          </DsButton>
          <DsFab ariaLabel="FAB md" size="md">
            →
          </DsFab>
          <DsFab ariaLabel="FAB sm" size="sm">
            →
          </DsFab>
          <DsFab ariaLabel="FAB lg" size="lg">
            →
          </DsFab>
        </div>
      </CatalogSection>

      <CatalogSection title="Form Kit · Chips">
        <DsCaption>Status (semantic --tf-* only) · category+icon · time · selection · signal</DsCaption>
        <div className={cat.row} style={{ marginTop: "0.75rem" }} data-testid="form-kit-chips">
          <DsChip variant="status" statusTone="good">
            High energy
          </DsChip>
          <DsChip variant="status" statusTone="warn">
            Caution
          </DsChip>
          <DsChip variant="status" statusTone="risk">
            Trap
          </DsChip>
          <DsChip variant="status" statusTone="neutral">
            Neutral
          </DsChip>
          <DsChip icon={<IconSparkles className={cat.inlineIcon} />}>Love</DsChip>
          <DsChip icon={<IconCalendar className={cat.inlineIcon} />}>Work</DsChip>
          <DsChip variant="time">09:00</DsChip>
          <DsChip variant="time" selected>
            13:40
          </DsChip>
          <DsChip variant="selection" selected icon={<IconMoon className={cat.inlineIcon} />}>
            Today
          </DsChip>
          <DsChip icon={<DsPlanet planet="moon" size={16} />}>Moon</DsChip>
          <DsChip icon={<DsPlanet planet="mars" size={16} />}>Mars</DsChip>
          <DsChip variant="ghost">Ghost</DsChip>
        </div>
      </CatalogSection>

      <CatalogSection title="Form Kit · Energy meters">
        <DsCaption>Metric · Radial · Dots · Linear · Wave (semantic) · Spectrum</DsCaption>
        <div
          className={cat.row}
          style={{ marginTop: "0.75rem", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}
          data-testid="form-kit-meters"
        >
          <DsMetric value="78%" label="Energy" />
          <DsRadialMeter value={78} />
          <DsDotMeter value={4} />
          <div style={{ flex: "1 1 8rem", minWidth: "8rem" }}>
            <DsLinearProgress value={78} label="Energy progress" />
          </div>
          <div style={{ flex: "1 1 8rem", minWidth: "8rem" }}>
            <DsWaveMeter value={78} showLabel />
          </div>
          <div style={{ flex: "1 1 10rem", minWidth: "10rem" }}>
            <DsSpectrum value={0.62} lowLabel="Low" highLabel="High" />
          </div>
        </div>
        <DsStarDivider />
      </CatalogSection>

      <CatalogSection title="Form Kit · Avatars & visuals">
        <div className={cat.row} style={{ alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
          <DsAvatar label="You" size="lg" />
          <DsAvatar label="Partner" size="lg" />
          <DsAvatar label="A" size="sm" />
          <DsZodiac sign="leo" size={36} />
          <DsNumber value={7} size={36} />
          <DsAngle angle="asc" size={36} />
          <DsPlanet planet="neptune" size={48} />
          <DsTarotFace src="/images/cards/tarot/web/faces/00-768x1280.avif" alt="Tarot specimen" />
        </div>
      </CatalogSection>

      <CatalogSection title="Form Kit · Section header & Quote">
        <DsSectionHeader
          eyebrow="Explore"
          title="Living maps"
          action={
            <DsButton variant="ghost" size="sm">
              View all
            </DsButton>
          }
          withDivider
          testId="form-kit-section-header"
        />
        <DsQuote highlight kicker="Insight" testId="form-kit-quote-highlight">
          Ясность сегодня — не скорость, а точный выбор опоры.
        </DsQuote>
      </CatalogSection>

      <CatalogSection title="Form Kit · Compositions">
        <div className={cat.cardGrid} data-testid="form-kit-compositions">
          <DsHeroBlock
            tone="glass"
            eyebrow="Clarity in focus"
            title="Сегодня держит ясность"
            body="Hero — крупный блок с bleed и FAB."
            bleed={<DsPlanet planet="neptune" size={120} />}
            chips={
              <DsChipCluster>
                <DsChip variant="status" statusTone="good">
                  Focus
                </DsChip>
              </DsChipCluster>
            }
            fab={<DsFab ariaLabel="Open" size="sm">→</DsFab>}
          />
          <DsWindowCard
            tone="solid"
            title="Best window"
            startLabel="13:40"
            endLabel="16:20"
            spectrum={<DsSpectrum value={0.55} />}
          />
          <DsMetricCard
            tone="solid"
            value="78%"
            label="Energy"
            meter={
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", width: "5.5rem" }}>
                <DsRadialMeter value={78} size={72} />
                <DsWaveMeter value={78} />
              </div>
            }
          />
          <DsContentCard
            tone="subtle"
            eyebrow="Note"
            body="Content block — prose + chips, not a metric twin."
            chips={<DsChip>tag</DsChip>}
          />
          <DsActionCard
            tone="accent"
            title="See your full day"
            action={
              <>
                <DsButton size="lg">Open</DsButton>
                <DsFab ariaLabel="Continue" size="md">
                  →
                </DsFab>
              </>
            }
          />
        </div>
        <DsListPanel tone="glass" title="List panel · celestial signals">
          <DsListRow
            leading={<DsPlanet planet="moon" size={36} />}
            title="Moon in Virgo"
            subtitle="Detail before speed"
            onClick={() => undefined}
          />
          <DsListRow
            leading={<DsPlanet planet="mars" size={36} />}
            title="Mars in Capricorn"
            subtitle="Push with structure"
            onClick={() => undefined}
          />
        </DsListPanel>
        <div style={{ marginTop: "1rem" }}>
          <DsButton variant="secondary" size="sm" onClick={() => setOverlayOpen(true)}>
            Open OverlaySheet
          </DsButton>
        </div>
        {overlayOpen ? (
          <DsOverlaySheet
            titleId={overlayTitleId}
            title="Overlay sheet"
            kicker="Form Kit"
            body="Opaque overlay tone — never glass over imagery."
            closeLabel="Close"
            onClose={() => setOverlayOpen(false)}
            testId="form-kit-overlay-sheet"
          />
        ) : null}
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
