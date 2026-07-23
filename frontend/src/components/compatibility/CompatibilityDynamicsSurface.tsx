"use client";

import Link from "next/link";
import { useMemo, useState, type ReactNode } from "react";
import { DsBody, DsButton } from "@/design-system";
import { stripCompatibilityDisplayGarbage } from "@/lib/compatibilityCopySanitize";
import {
  ProductJourneyScene,
  ProductNarrativeBlock,
  ProductNarrativeScroll,
  type ProductNarrativeChapter,
} from "@/components/product-ui/ProductJourneyScene";
import journeyStyles from "@/components/product-ui/ProductJourneyScene.module.css";

export type SignCompatProductSurface = {
  score_tagline: string;
  subscores: {
    attraction: number;
    stability: number;
    conflicts: number;
    sexuality: number;
  };
  overview_paragraphs: string[];
  blocks: Array<{
    key: string;
    title: string;
    subtitle: string;
    takeaway: string;
    detail: string;
    risk: string;
    action: string;
    tips?: string[];
  }>;
  roles: {
    you_bullets: string[];
    partner_bullets: string[];
  };
  scenarios: Array<{
    id: string;
    title: string;
    bullets: string[];
  }>;
};

type Props = {
  pairDisplay: string;
  youColumnLabel: string;
  partnerColumnLabel: string;
  score: number;
  productSurface: SignCompatProductSurface;
  readingLead?: string | null;
  personalizedCard?: ReactNode;
  extraParagraphs?: string[];
  paragraphsDetailTitle?: string;
  showParagraphsUpsell?: boolean;
  /** Если родитель уже показал заголовок пары — не дублируем верхнюю карточку. */
  omitIntroHero?: boolean;
};

const SUB_LABELS: Array<{ key: keyof SignCompatProductSurface["subscores"]; label: string }> = [
  { key: "attraction", label: "Притяжение" },
  { key: "stability", label: "Стабильность" },
  { key: "conflicts", label: "Конфликты" },
  { key: "sexuality", label: "Сексуальность" },
];

const ECHO_OPTIONS = [
  { id: "yes" as const, label: "Да", title: "да, это про нас" },
  { id: "partial" as const, label: "Частично", title: "частично" },
  { id: "no" as const, label: "Нет", title: "нет" },
];

function ensurePeriod(text: string): string {
  const t = text.replace(/\s+/g, " ").trim();
  if (!t) return "";
  return /[.!?…]$/.test(t) ? t : `${t}.`;
}

function initialFromPair(pairDisplay: string): [string, string] {
  const parts = pairDisplay.split(/\s*[×xX]\s*/);
  const a = (parts[0] || "?").trim();
  const b = (parts[1] || "?").trim();
  return [(a.charAt(0) || "?").toUpperCase(), (b.charAt(0) || "?").toUpperCase()];
}

function QuietScoreMeta({
  score,
  tagline,
  productSurface,
}: {
  score: number;
  tagline: string;
  productSurface: SignCompatProductSurface;
}) {
  const metrics = SUB_LABELS.map(
    (row) => `${row.label} ${productSurface.subscores[row.key]}%`,
  ).join(" · ");
  return (
    <div data-testid="compat-dynamics-score-meta">
      <p className={journeyStyles.pairScoreQuiet}>
        Общий индекс: {score}%
        {tagline ? ` · ${tagline}` : ""}
      </p>
      <p className={journeyStyles.pairSub}>{metrics}</p>
    </div>
  );
}

export function CompatibilityDynamicsSurface({
  pairDisplay,
  youColumnLabel,
  partnerColumnLabel,
  score,
  productSurface,
  personalizedCard,
  extraParagraphs,
  paragraphsDetailTitle = "Дополнительный текст",
  showParagraphsUpsell,
  readingLead,
  omitIntroHero,
}: Props) {
  const [blockEcho, setBlockEcho] = useState<Partial<Record<string, "yes" | "partial" | "no">>>({});
  const [initialA, initialB] = useMemo(() => initialFromPair(pairDisplay), [pairDisplay]);

  const storyChapters = useMemo((): ProductNarrativeChapter[] => {
    const chapters: ProductNarrativeChapter[] = [];
    const overview = productSurface.overview_paragraphs
      .map((p) => ensurePeriod(stripCompatibilityDisplayGarbage(p)))
      .filter(Boolean);
    if (overview.length) {
      chapters.push({
        id: "opening",
        kicker: "Как звучит эта связь",
        paragraphs: overview,
      });
    }
    if (readingLead?.trim()) {
      const lead = ensurePeriod(readingLead);
      if (lead && !overview.some((o) => o.includes(lead.slice(0, 24)))) {
        if (chapters[0]) {
          chapters[0] = {
            ...chapters[0],
            paragraphs: [lead, ...chapters[0].paragraphs],
          };
        } else {
          chapters.push({ id: "opening", kicker: "Как звучит эта связь", paragraphs: [lead] });
        }
      }
    }
    return chapters;
  }, [productSurface.overview_paragraphs, readingLead]);

  const layerStep = omitIntroHero ? 1 : 2;
  const moveStep = layerStep + 1;
  const bridgeStep = moveStep + 1;

  return (
    <div className="compat-desktop-shell compat-desktop-stack" data-testid="compat-dynamics-surface">
      {!omitIntroHero ? (
        <ProductJourneyScene
          step={1}
          title="Пара"
          lead="Не «насколько вы подходите», а как вы цепляетесь, где спотыкаетесь и что с этим делать."
          motif="insight"
          testId="compat-dynamics-pair"
        >
          <div className={journeyStyles.pairHero}>
            <div className={journeyStyles.avatarGroup} aria-hidden>
              <span className={journeyStyles.avatar}>{initialA}</span>
              <span className={`${journeyStyles.avatar} ${journeyStyles.avatarOverlap}`}>{initialB}</span>
            </div>
            <div className={journeyStyles.pairMeta}>
              <p className={journeyStyles.pairTitle}>{pairDisplay}</p>
              <QuietScoreMeta
                score={score}
                tagline={productSurface.score_tagline}
                productSurface={productSurface}
              />
            </div>
          </div>
        </ProductJourneyScene>
      ) : (
        <QuietScoreMeta
          score={score}
          tagline={productSurface.score_tagline}
          productSurface={productSurface}
        />
      )}

      <ProductJourneyScene
        step={layerStep}
        title="История связи"
        lead="Рассказ о том, как вы звучите вместе — и почему именно так."
        motif="why"
        testId="compat-dynamics-story"
      >
        {storyChapters.length ? (
          <ProductNarrativeScroll
            theme={productSurface.score_tagline || pairDisplay}
            chapters={storyChapters}
            softWhy={readingLead ? ensurePeriod(readingLead) : null}
            softWhyLabel="Главная мысль"
            testId="compat-dynamics-narrative-scroll"
          />
        ) : (
          <DsBody muted>Пока мало сигналов для полного рассказа — уточни знаки или даты.</DsBody>
        )}

        <div className={journeyStyles.actionRow} style={{ flexDirection: "column", alignItems: "stretch", gap: "0.85rem" }}>
          {productSurface.blocks.map((block) => {
            const paragraphs = [
              ensurePeriod(block.takeaway),
              ensurePeriod(block.detail),
              block.risk?.trim() ? ensurePeriod(`Риск — ${block.risk}`) : "",
              block.action?.trim() ? ensurePeriod(`Как действовать — ${block.action}`) : "",
              ...(block.key === "sexuality" && block.tips?.length
                ? block.tips.map((tip) => ensurePeriod(tip))
                : []),
            ].filter(Boolean);

            return (
              <ProductNarrativeBlock
                key={block.key}
                id={block.key}
                kicker={block.title}
                lead={block.subtitle || null}
                paragraphs={paragraphs}
                accent={block.key === "sexuality" ? "dual" : "default"}
                collapseAfter={2}
                testId={`compat-dynamics-block-${block.key}`}
              >
                <div>
                  <p className={journeyStyles.pairSub} style={{ marginBottom: "0.45rem", fontWeight: 600 }}>
                    Это про вас?
                  </p>
                  <div className={journeyStyles.tabRow}>
                    {ECHO_OPTIONS.map((opt) => (
                      <button
                        key={opt.id}
                        type="button"
                        title={opt.title}
                        className={`${journeyStyles.tabChip} ${
                          blockEcho[block.key] === opt.id ? journeyStyles.tabChipActive : ""
                        }`.trim()}
                        onClick={() => setBlockEcho((prev) => ({ ...prev, [block.key]: opt.id }))}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                  {blockEcho[block.key] ? (
                    <p className={journeyStyles.pairSub} style={{ marginTop: "0.55rem" }}>
                      {blockEcho[block.key] === "yes"
                        ? block.key === "sexuality"
                          ? "Тогда сексуальный слой у вас реально силён — держите рядом ясность про желание, темп и границы."
                          : "Зафиксировали попадание — опирайтесь на формулировки блока в реальных сценах."
                        : blockEcho[block.key] === "partial"
                          ? "Частичное попадание нормально: добирайте контекст через конкретные ситуации, не через знаки."
                          : "Ок — используйте блок как гипотезу и проверяйте по фактам и другим слоям выше."}
                    </p>
                  ) : null}
                </div>
              </ProductNarrativeBlock>
            );
          })}
        </div>
      </ProductJourneyScene>

      {personalizedCard}

      <ProductJourneyScene
        step={moveStep}
        title="Кто как ведёт себя"
        lead={`Роли ниже — про темп и защиту, не про пол. «Ты» (${youColumnLabel}) и партнёр (${partnerColumnLabel}).`}
        motif="effort"
        testId="compat-dynamics-roles"
      >
        <ProductNarrativeBlock
          id="roles"
          kicker="Два темпа в одной паре"
          accent="dual"
          testId="compat-dynamics-roles-block"
        >
          <div className={journeyStyles.dualPanels}>
            <div className={journeyStyles.dualPanel}>
              <p className={journeyStyles.dualPanelTitle}>Ты</p>
              {productSurface.roles.you_bullets.map((line) => (
                <p key={line.slice(0, 40)} className={journeyStyles.dualPanelBody}>
                  {line}
                </p>
              ))}
            </div>
            <div className={journeyStyles.dualPanel}>
              <p className={journeyStyles.dualPanelTitle}>Партнёр</p>
              {productSurface.roles.partner_bullets.map((line) => (
                <p key={line.slice(0, 40)} className={journeyStyles.dualPanelBody}>
                  {line}
                </p>
              ))}
            </div>
          </div>
        </ProductNarrativeBlock>

        {productSurface.scenarios.length ? (
          <div className={journeyStyles.actionRow} style={{ flexDirection: "column", alignItems: "stretch", gap: "0.75rem" }}>
            {productSurface.scenarios.map((group) => (
              <ProductNarrativeBlock
                key={group.id}
                id={`scenario-${group.id}`}
                kicker={group.title}
                paragraphs={group.bullets.map(ensurePeriod).filter(Boolean)}
                accent="support"
                collapseAfter={3}
                testId={`compat-dynamics-scenario-${group.id}`}
              />
            ))}
          </div>
        ) : null}

        {extraParagraphs && extraParagraphs.length ? (
          <ProductNarrativeBlock
            id="extra"
            kicker={paragraphsDetailTitle}
            paragraphs={extraParagraphs.map(ensurePeriod).filter(Boolean)}
            collapseAfter={2}
            testId="compat-dynamics-extra"
          >
            {showParagraphsUpsell ? (
              <DsBody size="sm" muted>
                Полный текст и более точный слой — в совместимости по профилям и датам с городом.
              </DsBody>
            ) : null}
          </ProductNarrativeBlock>
        ) : null}
      </ProductJourneyScene>

      <ProductJourneyScene
        step={bridgeStep}
        title="Продолжение"
        lead="Если ситуация про решение — в Guidance. Если паттерн — в профиль. Другие уровни пары — рядом."
        motif="bridge"
        bridge
        testId="compat-dynamics-bridge"
      >
        <div className={journeyStyles.actionRow}>
          <DsButton href="/tarot?from=compatibility">Разобрать ситуацию</DsButton>
          <DsButton href="/profile" variant="secondary">
            Понять себя
          </DsButton>
          <DsButton href="/compatibility" variant="secondary">
            Другие уровни
          </DsButton>
        </div>
        <Link href="/compatibility" className={journeyStyles.bridgeLink}>
          Вернуться к выбору направления
        </Link>
      </ProductJourneyScene>
    </div>
  );
}
