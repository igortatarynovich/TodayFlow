"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { t, getLocale } from "@/lib/i18n";
import { isAppProductRoute } from "@/lib/sectionAtmosphere";
import { isProductWebFullPageRoute } from "@/lib/productWebShell";
import { buildAppNavLinks } from "@/lib/appNavConfig";
import { useAuth } from "@/lib/useAuth";

export function Footer() {
  const pathname = usePathname();
  const { isAuthenticated } = useAuth();
  const locale = getLocale();
  const chromeLocale = locale === "ru" ? "ru" : "en";
  const productNavLinks = buildAppNavLinks(chromeLocale, isAuthenticated ? "authenticated" : "guest");
  if (isProductWebFullPageRoute(pathname)) return null;
  const currentYear = new Date().getFullYear();
  const minimal = isAppProductRoute(pathname);

  if (minimal) {
    return (
      <footer className={`orbit-footer orbit-footer--minimal ${pathname?.startsWith("/tarot") ? "orbit-footer--tarot" : ""}`}>
        <div className="orbit-footer__container">
          <p className="orbit-footer__mantra orbit-mantra">
            {t("footer.mantra", "Pause · Sense · Integrate")}
          </p>
          <div className="orbit-footer__copyright">
            © {currentYear} TodayFlow
          </div>
        </div>
      </footer>
    );
  }

  return (
    <footer className="orbit-footer">
      <div className="orbit-footer__container">
        <div className="orbit-footer__main">
          <div className="orbit-footer__links">
            <div className="orbit-footer__column">
              <h3 className="orbit-footer__column-title">{t("footer.product.title", "Product")}</h3>
              <nav className="orbit-footer__column-nav">
                <Link href="/" className="orbit-footer__link">
                  {t("footer.product.home", "Home")}
                </Link>
                {productNavLinks.map((link) => (
                  <Link key={link.href} href={link.href} className="orbit-footer__link">
                    {link.label}
                  </Link>
                ))}
                <Link href="/pricing" className="orbit-footer__link">
                  {t("footer.product.subscriptions", "Subscriptions")}
                </Link>
              </nav>
            </div>
          </div>

          <div className="orbit-footer__cta">
            <h3 className="orbit-footer__cta-title">{t("footer.newsletter.title", "Stay Updated")}</h3>
            <p className="orbit-footer__cta-text">
              {t("footer.newsletter.text", "Subscribe to the newsletter to receive personal insights and updates")}
            </p>
            <form
              className="orbit-footer__newsletter"
              onSubmit={(e) => {
                e.preventDefault();
              }}
            >
              <input
                type="email"
                placeholder={t("footer.newsletter.placeholder", "Your email")}
                className="orbit-footer__newsletter-input"
                required
              />
              <button type="submit" className="orbit-button orbit-button-primary orbit-button-xs">
                {t("footer.newsletter.subscribe", "Subscribe")}
              </button>
            </form>
          </div>
        </div>

        <div className="orbit-footer__bottom">
          <p className="orbit-footer__mantra orbit-mantra">
            {t("footer.mantra", "Pause · Sense · Integrate")}
          </p>
          <div className="orbit-footer__copyright">
            © {currentYear} TodayFlow. {t("footer.copyright", "All rights reserved.")}
          </div>
        </div>

        <div className="orbit-footer__versions">
          <span className="orbit-soft">TodayFlow MVP 0.1</span>
          <span className="orbit-soft">Content v1.0.0 · i18n v1.0.0</span>
        </div>
      </div>
    </footer>
  );
}
