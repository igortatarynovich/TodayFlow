"use client";

import Link from "next/link";
import {
  PRODUCT_WEB_LANDING_FINAL,
  PRODUCT_WEB_LANDING_FOOTER,
  PRODUCT_WEB_LANDING_GUEST_SECTION,
  PRODUCT_WEB_LANDING_GUEST_TRIALS,
  PRODUCT_WEB_LANDING_HERO,
  PRODUCT_WEB_LANDING_ORBIT_NODES,
  PRODUCT_WEB_LANDING_TESTIMONIALS,
  PRODUCT_WEB_LANDING_TODAY_PROMISE,
} from "@/components/product-ui/productWebLandingContent";
import { ProductWebGuestNav } from "@/components/product-ui/ProductWebGuestNav";
import { buildAppNavLinks } from "@/lib/appNavConfig";
import {
  DsBody,
  DsButton,
  DsDisplayTitle,
  DsEyebrow,
  DsFeatureTile,
  DsMarketingPage,
  DsMarketingSection,
  DsOrbitalNode,
  DsOrbitalViz,
  DsQuoteTile,
  DsSectionTitle,
  DsThemeAsideRow,
  DsThemePanel,
  DsFeatureIcon,
  IconActivity,
  IconEye,
  IconMountain,
  IconRoute,
  IconSparkles,
  IconSun,
  IconTarot,
  IconUsers,
} from "@/design-system";
import l from "@/design-system/layouts/dsLayouts.module.css";

type Props = {
  signupHref: string;
  loginHref: string;
  compatibilityHref?: string;
};

const ORBIT_NODE_ICONS = {
  sun: IconSun,
  moon: IconEye,
  path: IconRoute,
  star: IconSparkles,
  sage: IconMountain,
} as const;

const GUEST_TRIAL_ICONS = {
  tarot: IconTarot,
  users: IconUsers,
  activity: IconActivity,
} as const;

const PROMISE_CARD_ICONS = {
  theme: IconSun,
  focus: IconEye,
  memory: IconSparkles,
} as const;

export function ProductWebLanding({
  signupHref,
  loginHref,
  compatibilityHref = "/compatibility",
}: Props) {
  const year = new Date().getFullYear();
  const guestNavLinks = buildAppNavLinks("ru", "guest");

  const orbitNodes: DsOrbitalNode[] = PRODUCT_WEB_LANDING_ORBIT_NODES.map((node) => {
    const Icon = ORBIT_NODE_ICONS[node.id as keyof typeof ORBIT_NODE_ICONS] ?? IconSparkles;
    return {
      ...node,
      icon: <Icon />,
    };
  });

  return (
    <DsMarketingPage
      nav={
        <ProductWebGuestNav
          ctaHref={signupHref}
          ctaLabel={PRODUCT_WEB_LANDING_HERO.primaryCta}
          locale="ru"
        />
      }
      footer={
        <footer className={l.footer}>
          <div className={l.footerTop}>
            <div>
              <DsDisplayTitle as="p" size="sm">
                TodayFlow
              </DsDisplayTitle>
              <DsBody size="sm" muted>
                {PRODUCT_WEB_LANDING_FOOTER.tagline}
              </DsBody>
            </div>
            <div className={l.footerColumns}>
              <div>
                <DsEyebrow>Попробовать</DsEyebrow>
                {guestNavLinks.map((link) => (
                  <Link key={link.href} href={link.href} className={l.footerLink}>
                    {link.label}
                  </Link>
                ))}
              </div>
              <div>
                <DsEyebrow>Компания</DsEyebrow>
                {PRODUCT_WEB_LANDING_FOOTER.companyLinks.map((link) => (
                  <Link key={link.label} href={link.href} className={l.footerLink}>
                    {link.label}
                  </Link>
                ))}
              </div>
            </div>
          </div>
          <div className={l.footerBottom}>
            <p className={l.copyright}>© {year} TodayFlow. Все права защищены.</p>
            <div className={l.socialLinks}>
              <span>INSTAGRAM</span>
              <span>TWITTER</span>
              <span>JOURNAL</span>
            </div>
          </div>
        </footer>
      }
    >
      <DsMarketingSection testId="landing-page">
        <div className={l.heroSection}>
          <div className={l.heroCopy}>
            <div>
              <DsDisplayTitle id="landing-hero-title">
                {PRODUCT_WEB_LANDING_HERO.titleLead}
                <br />
                {PRODUCT_WEB_LANDING_HERO.titleTail}
              </DsDisplayTitle>
              <DsBody size="lg" muted>
                {PRODUCT_WEB_LANDING_HERO.subtitle}
              </DsBody>
            </div>
            <div className={l.heroCtas}>
              <DsButton href={signupHref}>{PRODUCT_WEB_LANDING_HERO.primaryCta}</DsButton>
              <DsButton href={compatibilityHref} variant="secondary">
                {PRODUCT_WEB_LANDING_HERO.secondaryCta}
              </DsButton>
              <DsButton href={loginHref} variant="secondary">
                {PRODUCT_WEB_LANDING_HERO.loginCta}
              </DsButton>
            </div>
          </div>
          <DsOrbitalViz nodes={orbitNodes} testId="landing-orbit-viz" />
        </div>
      </DsMarketingSection>

      <DsMarketingSection tight aria-labelledby="landing-guest-title">
        <div className={l.centerStack}>
          <DsEyebrow>{PRODUCT_WEB_LANDING_GUEST_SECTION.eyebrow}</DsEyebrow>
          <DsSectionTitle id="landing-guest-title">{PRODUCT_WEB_LANDING_GUEST_SECTION.title}</DsSectionTitle>
          <DsBody muted>{PRODUCT_WEB_LANDING_GUEST_SECTION.lead}</DsBody>
        </div>
        <div className={l.grid3}>
          {PRODUCT_WEB_LANDING_GUEST_TRIALS.map((trial) => {
            const Icon = GUEST_TRIAL_ICONS[trial.icon] ?? IconSparkles;
            return (
              <div key={trial.id} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                <DsFeatureTile
                  testId={`landing-guest-${trial.id}`}
                  icon={<Icon />}
                  title={trial.title}
                  body={trial.body}
                />
                <DsButton href={trial.href} variant="secondary">
                  {trial.cta}
                </DsButton>
              </div>
            );
          })}
        </div>
      </DsMarketingSection>

      <DsMarketingSection>
        <DsThemePanel
          variant="marketing"
          titleId="landing-today-promise"
          eyebrow={PRODUCT_WEB_LANDING_TODAY_PROMISE.eyebrow}
          title={PRODUCT_WEB_LANDING_TODAY_PROMISE.title}
          tags={[...PRODUCT_WEB_LANDING_TODAY_PROMISE.tags]}
          body={PRODUCT_WEB_LANDING_TODAY_PROMISE.body}
          aside={
            <>
              {PRODUCT_WEB_LANDING_TODAY_PROMISE.cards.map((card) => {
                const Icon = PROMISE_CARD_ICONS[card.id as keyof typeof PROMISE_CARD_ICONS] ?? IconSparkles;
                return (
                  <DsThemeAsideRow
                    key={card.id}
                    testId={`landing-promise-${card.id}`}
                    icon={<Icon />}
                    label={card.label}
                    value={card.value}
                  />
                );
              })}
            </>
          }
        />
      </DsMarketingSection>

      <DsMarketingSection>
        <div className={l.centerStack}>
          <DsSectionTitle id="landing-testimonials">{PRODUCT_WEB_LANDING_TESTIMONIALS.title}</DsSectionTitle>
          <div className={l.grid3}>
            {PRODUCT_WEB_LANDING_TESTIMONIALS.items.map((item) => (
              <DsQuoteTile key={item.name} quote={item.quote} name={item.name} role={item.role} />
            ))}
          </div>
        </div>
      </DsMarketingSection>

      <DsMarketingSection>
        <div className={l.centerStack}>
          <DsDisplayTitle id="landing-final-cta" size="lg">
            {PRODUCT_WEB_LANDING_FINAL.title}
          </DsDisplayTitle>
          <DsBody muted>{PRODUCT_WEB_LANDING_FINAL.subtitle}</DsBody>
          <DsButton href={signupHref}>{PRODUCT_WEB_LANDING_FINAL.cta}</DsButton>
        </div>
      </DsMarketingSection>
    </DsMarketingPage>
  );
}
