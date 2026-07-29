"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  PRODUCT_WEB_LANDING_FINAL,
  PRODUCT_WEB_LANDING_FOOTER,
  PRODUCT_WEB_LANDING_HERO,
  PRODUCT_WEB_LANDING_NAV,
  PRODUCT_WEB_LANDING_ORBIT_NODES,
  PRODUCT_WEB_LANDING_RETURN_REASONS,
  PRODUCT_WEB_LANDING_SECTION_IDS,
  PRODUCT_WEB_LANDING_SERVICE_SECTIONS,
  PRODUCT_WEB_LANDING_TODAY_PROMISE,
} from "@/components/product-ui/productWebLandingContent";
import { ProductWebGuestNav } from "@/components/product-ui/ProductWebGuestNav";
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
  DsSectionTitle,
  DsThemeAsideRow,
  DsThemePanel,
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
};

const ORBIT_NODE_ICONS = {
  sun: IconSun,
  moon: IconEye,
  path: IconRoute,
  star: IconSparkles,
  sage: IconMountain,
} as const;

const SERVICE_ICONS = {
  tarot: IconTarot,
  users: IconUsers,
  activity: IconActivity,
} as const;

const RETURN_REASON_ICONS = {
  morning: IconSun,
  memory: IconSparkles,
  "today-not-portrait": IconEye,
} as const;

const PROMISE_CARD_ICONS = {
  theme: IconSun,
  focus: IconEye,
  memory: IconSparkles,
} as const;

function useLandingActiveSection(): string | null {
  const [activeHref, setActiveHref] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === "undefined" || typeof IntersectionObserver === "undefined") {
      return;
    }

    const reduceMotion =
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!reduceMotion) {
      document.documentElement.style.scrollBehavior = "smooth";
    }

    const sections = PRODUCT_WEB_LANDING_SECTION_IDS.map((id) => document.getElementById(id)).filter(
      (el): el is HTMLElement => Boolean(el),
    );
    if (sections.length === 0) return;

    const visibility = new Map<string, number>();
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          visibility.set(entry.target.id, entry.isIntersecting ? entry.intersectionRatio : 0);
        }
        let bestId: string | null = null;
        let bestRatio = 0;
        visibility.forEach((ratio, id) => {
          if (ratio > bestRatio) {
            bestRatio = ratio;
            bestId = id;
          }
        });
        if (bestId) {
          const navItem = PRODUCT_WEB_LANDING_NAV.find((item) => item.id === bestId);
          setActiveHref(navItem ? navItem.href : null);
        }
      },
      {
        root: null,
        rootMargin: "-28% 0px -42% 0px",
        threshold: [0.15, 0.35, 0.55, 0.75],
      },
    );

    sections.forEach((section) => observer.observe(section));
    return () => {
      observer.disconnect();
      document.documentElement.style.scrollBehavior = "";
    };
  }, []);

  return activeHref;
}

export function ProductWebLanding({ signupHref, loginHref }: Props) {
  const year = new Date().getFullYear();
  const activeHref = useLandingActiveSection();
  const navLinks = useMemo(
    () => PRODUCT_WEB_LANDING_NAV.map(({ href, label }) => ({ href, label })),
    [],
  );

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
          links={navLinks}
          activeHref={activeHref}
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
                <DsEyebrow>Разделы</DsEyebrow>
                {PRODUCT_WEB_LANDING_NAV.map((link) => (
                  <Link key={link.href} href={link.href} className={l.footerLink}>
                    {link.label}
                  </Link>
                ))}
                <Link href="#practices" className={l.footerLink}>
                  Практики
                </Link>
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
      <DsMarketingSection id="hero" screen tone="hero" testId="landing-page" aria-labelledby="landing-hero-title">
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
              <DsButton href={loginHref} variant="secondary">
                {PRODUCT_WEB_LANDING_HERO.secondaryCta}
              </DsButton>
            </div>
          </div>
          <DsOrbitalViz nodes={orbitNodes} testId="landing-orbit-viz" />
        </div>
      </DsMarketingSection>

      {PRODUCT_WEB_LANDING_SERVICE_SECTIONS.map((service, index) => {
        const Icon = SERVICE_ICONS[service.icon] ?? IconSparkles;
        const titleId = `landing-service-${service.id}`;
        return (
          <DsMarketingSection
            key={service.id}
            id={service.id}
            screen
            tight
            tone={index % 2 === 1 ? "muted" : "default"}
            testId={`landing-section-${service.id}`}
            aria-labelledby={titleId}
          >
            <div className={l.serviceSection}>
              <div className={l.serviceCopy}>
                <DsEyebrow>{service.eyebrow}</DsEyebrow>
                <DsSectionTitle id={titleId}>{service.title}</DsSectionTitle>
                <DsBody muted>{service.body}</DsBody>
                <div className={l.heroCtas}>
                  <DsButton href={service.href}>{service.cta}</DsButton>
                </div>
              </div>
              <div className={l.serviceVisual} aria-hidden>
                <span className={l.serviceIconWrap}>
                  <Icon className={l.serviceIcon} />
                </span>
              </div>
            </div>
          </DsMarketingSection>
        );
      })}

      <DsMarketingSection id="today" screen tone="muted" testId="landing-section-today" aria-labelledby="landing-today-promise">
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

      <DsMarketingSection id="why" screen testId="landing-section-why" aria-labelledby="landing-return-reasons">
        <div className={l.centerStack}>
          <DsSectionTitle id="landing-return-reasons">{PRODUCT_WEB_LANDING_RETURN_REASONS.title}</DsSectionTitle>
          <div className={l.grid3}>
            {PRODUCT_WEB_LANDING_RETURN_REASONS.items.map((item) => {
              const Icon = RETURN_REASON_ICONS[item.id as keyof typeof RETURN_REASON_ICONS] ?? IconSparkles;
              return (
                <DsFeatureTile
                  key={item.id}
                  testId={`landing-reason-${item.id}`}
                  icon={<Icon />}
                  title={item.title}
                  body={item.body}
                />
              );
            })}
          </div>
        </div>
      </DsMarketingSection>

      <DsMarketingSection id="cta" screen tone="muted" testId="landing-section-cta" aria-labelledby="landing-final-cta">
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
