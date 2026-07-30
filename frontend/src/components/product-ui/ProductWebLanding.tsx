"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
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
import { VALUE_FIRST_PATHS } from "@/lib/guestProfileDraft";

type Props = {
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

    const root = document.documentElement;
    const page = document.querySelector("[data-landing-page]");
    const navH =
      (page instanceof HTMLElement && getComputedStyle(page).getPropertyValue("--tf-ds-nav-h").trim()) ||
      "4.5rem";
    root.style.scrollPaddingTop = navH;

    const reduceMotion =
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!reduceMotion) {
      root.style.scrollBehavior = "smooth";
      root.style.scrollSnapType = "y proximity";
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
      root.style.scrollBehavior = "";
      root.style.scrollSnapType = "";
      root.style.scrollPaddingTop = "";
    };
  }, []);

  return activeHref;
}

export function ProductWebLanding({ loginHref }: Props) {
  const year = new Date().getFullYear();
  const activeHref = useLandingActiveSection();
  const navLinks = PRODUCT_WEB_LANDING_NAV.map(({ href, label }) => ({ href, label }));
  const demoHref = VALUE_FIRST_PATHS.demoToday;
  const inviteHref = VALUE_FIRST_PATHS.invite;
  const compatHref = "/compatibility";

  const orbitNodes: DsOrbitalNode[] = PRODUCT_WEB_LANDING_ORBIT_NODES.map((node) => {
    const Icon = ORBIT_NODE_ICONS[node.id as keyof typeof ORBIT_NODE_ICONS] ?? IconSparkles;
    return {
      ...node,
      icon: <Icon />,
    };
  });

  return (
    <DsMarketingPage
      data-landing-page
      nav={
        <ProductWebGuestNav
          ctaHref={demoHref}
          ctaLabel={PRODUCT_WEB_LANDING_HERO.primaryCtaDemo}
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
      <DsMarketingSection id="hero" screen tone="hero" testId="landing-page" data-landing-screen="hero" aria-labelledby="landing-hero-title">
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
              <div className={l.heroFragment} data-testid="landing-hero-fragment">
                <DsEyebrow>{PRODUCT_WEB_LANDING_HERO.fragmentEyebrow}</DsEyebrow>
                <p className={l.heroFragmentLine}>
                  <strong>{PRODUCT_WEB_LANDING_HERO.fragmentThemeLabel}.</strong>{" "}
                  {PRODUCT_WEB_LANDING_HERO.fragmentTheme}
                </p>
                <p className={l.heroFragmentLine}>
                  <strong>{PRODUCT_WEB_LANDING_HERO.fragmentFocusLabel}.</strong>{" "}
                  {PRODUCT_WEB_LANDING_HERO.fragmentFocus}
                </p>
              </div>
            </div>
            <div className={l.heroCtas} data-testid="landing-hero-ctas">
              <DsButton href={demoHref}>{PRODUCT_WEB_LANDING_HERO.primaryCtaDemo}</DsButton>
              <DsButton href={compatHref}>{PRODUCT_WEB_LANDING_HERO.primaryCtaCompat}</DsButton>
              <DsButton href={loginHref} variant="secondary">
                {PRODUCT_WEB_LANDING_HERO.loginCta}
              </DsButton>
            </div>
            <p className={l.heroTools} data-testid="landing-hero-tools">
              <span>{PRODUCT_WEB_LANDING_HERO.toolsEyebrow}: </span>
              <Link href="/tarot">{PRODUCT_WEB_LANDING_HERO.toolsTarotLabel}</Link>
              {" · "}
              <Link href="/practices">{PRODUCT_WEB_LANDING_HERO.toolsPracticesLabel}</Link>
            </p>
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
            data-landing-screen={service.id}
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

      <DsMarketingSection id="today" screen tone="muted" testId="landing-section-today" data-landing-screen="today" aria-labelledby="landing-today-promise">
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

      <DsMarketingSection id="why" screen testId="landing-section-why" data-landing-screen="why" aria-labelledby="landing-return-reasons">
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

      <DsMarketingSection id="cta" screen tone="muted" testId="landing-section-cta" data-landing-screen="cta" aria-labelledby="landing-final-cta">
        <div className={l.centerStack}>
          <DsDisplayTitle id="landing-final-cta" size="lg">
            {PRODUCT_WEB_LANDING_FINAL.title}
          </DsDisplayTitle>
          <DsBody muted>{PRODUCT_WEB_LANDING_FINAL.subtitle}</DsBody>
          <DsButton href={inviteHref}>{PRODUCT_WEB_LANDING_FINAL.cta}</DsButton>
        </div>
      </DsMarketingSection>
    </DsMarketingPage>
  );
}
