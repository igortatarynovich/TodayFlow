"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { LandingSignatureMoon } from "@/components/landing/LandingSignatureMoon";
import {
  PRODUCT_WEB_LANDING_FINAL,
  PRODUCT_WEB_LANDING_FOOTER,
  PRODUCT_WEB_LANDING_HERO,
  PRODUCT_WEB_LANDING_NAV,
  PRODUCT_WEB_LANDING_SECTION_IDS,
  PRODUCT_WEB_LANDING_SERVICE_SECTIONS,
  PRODUCT_WEB_LANDING_TODAY_PROMISE,
  PRODUCT_WEB_LANDING_TRUST,
} from "@/components/product-ui/productWebLandingContent";
import { ProductWebGuestNav } from "@/components/product-ui/ProductWebGuestNav";
import { ProductScenePlate } from "@/components/product-ui/ProductScenePlate";
import {
  DsBody,
  DsButton,
  DsDisplayTitle,
  DsEyebrow,
  DsMarketingPage,
  DsMarketingSection,
  DsSectionTitle,
  DsThemeAsideRow,
  DsThemePanel,
  IconEye,
  IconSparkles,
  IconSun,
} from "@/design-system";
import l from "@/design-system/layouts/dsLayouts.module.css";
import { VALUE_FIRST_PATHS } from "@/lib/guestProfileDraft";
import { landingServicePlate } from "@/lib/productScenePlates";

type Props = {
  loginHref: string;
};

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
              <p className={l.heroBrand}>{PRODUCT_WEB_LANDING_HERO.brand}</p>
              <DsDisplayTitle id="landing-hero-title" className={l.heroBeats}>
                {PRODUCT_WEB_LANDING_HERO.beats.map((beat) => (
                  <span key={beat} className={l.heroBeat}>
                    {beat}
                  </span>
                ))}
              </DsDisplayTitle>
              <DsBody size="lg" muted>
                {PRODUCT_WEB_LANDING_HERO.manifesto}
              </DsBody>
            </div>
            <div className={l.heroCtas} data-testid="landing-hero-ctas">
              <DsButton href={demoHref}>{PRODUCT_WEB_LANDING_HERO.primaryCtaDemo}</DsButton>
              <DsButton href={loginHref} variant="secondary">
                {PRODUCT_WEB_LANDING_HERO.loginCta}
              </DsButton>
            </div>
            <p className={l.heroLearnMore}>
              <Link href="#trust">{PRODUCT_WEB_LANDING_HERO.learnMore}</Link>
            </p>
          </div>
          <div className={l.heroVisual} data-testid="landing-hero-visual">
            <LandingSignatureMoon />
          </div>
        </div>
      </DsMarketingSection>

      <DsMarketingSection
        id="trust"
        screen
        testId="landing-section-trust"
        data-landing-screen="trust"
        aria-labelledby="landing-trust-title"
      >
        <div className={l.manifestoSection}>
          <DsEyebrow>{PRODUCT_WEB_LANDING_TRUST.eyebrow}</DsEyebrow>
          <DsDisplayTitle id="landing-trust-title" as="h2" size="lg">
            {PRODUCT_WEB_LANDING_TRUST.title}
          </DsDisplayTitle>
          <DsBody size="lg" muted>
            {PRODUCT_WEB_LANDING_TRUST.body}
          </DsBody>
          <ol className={l.manifestoList}>
            {PRODUCT_WEB_LANDING_TRUST.items.map((item) => (
              <li key={item.id} className={l.manifestoItem} data-testid={`landing-trust-${item.id}`}>
                <span className={l.manifestoIndex}>{item.kicker}</span>
                <h3 className={l.manifestoHeading}>{item.title}</h3>
                <p className={l.manifestoBody}>{item.body}</p>
              </li>
            ))}
          </ol>
        </div>
      </DsMarketingSection>

      <DsMarketingSection id="today" screen tone="muted" testId="landing-section-today" data-landing-screen="today" aria-labelledby="landing-today-promise">
        <div className={l.todaySection}>
          <ProductScenePlate
            plate="landing_today"
            frame="landingService"
            className={l.todayPlate}
            testId="landing-today-plate"
          />
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
        </div>
      </DsMarketingSection>

      {PRODUCT_WEB_LANDING_SERVICE_SECTIONS.map((service, index) => {
        const titleId = `landing-service-${service.id}`;
        const plateId = landingServicePlate(service.id);
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
            <div className={`${l.serviceSection} ${index % 2 === 1 ? l.serviceSectionFlip : ""}`.trim()}>
              <div className={l.serviceCopy}>
                <DsEyebrow>{service.eyebrow}</DsEyebrow>
                <DsSectionTitle id={titleId}>{service.title}</DsSectionTitle>
                <DsBody muted>{service.body}</DsBody>
                <div className={l.heroCtas}>
                  <DsButton href={service.href}>{service.cta}</DsButton>
                </div>
              </div>
              <div className={l.serviceVisual} aria-hidden>
                <ProductScenePlate
                  plate={plateId}
                  frame="landingService"
                  testId={`landing-service-plate-${service.id}`}
                />
              </div>
            </div>
          </DsMarketingSection>
        );
      })}

      <DsMarketingSection id="cta" screen tone="muted" testId="landing-section-cta" data-landing-screen="cta" aria-labelledby="landing-final-cta">
        <div className={l.ctaSection}>
          <ProductScenePlate
            plate="landing_cta"
            frame="landingService"
            className={l.ctaPlate}
            testId="landing-cta-plate"
          />
          <div className={l.centerStack}>
            <DsDisplayTitle id="landing-final-cta" size="lg">
              {PRODUCT_WEB_LANDING_FINAL.title}
            </DsDisplayTitle>
            <DsBody muted>{PRODUCT_WEB_LANDING_FINAL.subtitle}</DsBody>
            <DsButton href={inviteHref}>{PRODUCT_WEB_LANDING_FINAL.cta}</DsButton>
          </div>
        </div>
      </DsMarketingSection>
    </DsMarketingPage>
  );
}
