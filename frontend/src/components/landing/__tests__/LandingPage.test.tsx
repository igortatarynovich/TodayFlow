import { render, screen } from "@testing-library/react";
import { LandingPage } from "@/components/landing/LandingPage";
import { PRODUCT_WEB_LANDING_SECTION_IDS } from "@/components/product-ui/productWebLandingContent";

describe("LandingPage", () => {
  it("renders scenario screens as viewport sections with all-anchor top nav (SoT v4)", () => {
    render(<LandingPage signupHref="/onboarding/welcome?fresh=1" loginHref="/auth?mode=login" />);

    expect(screen.getByTestId("landing-page")).toBeInTheDocument();
    expect(screen.getByTestId("landing-orbit-viz")).toBeInTheDocument();
    expect(screen.getByTestId("landing-hero-plate")).toBeInTheDocument();
    expect(screen.getByTestId("landing-service-plate-tarot")).toBeInTheDocument();
    expect(screen.getByTestId("landing-service-plate-compatibility")).toBeInTheDocument();
    expect(screen.getByTestId("landing-service-plate-practices")).toBeInTheDocument();
    expect(screen.getByTestId("landing-today-plate")).toBeInTheDocument();
    expect(screen.getByTestId("landing-cta-plate")).toBeInTheDocument();
    for (const id of PRODUCT_WEB_LANDING_SECTION_IDS) {
      const el = document.getElementById(id);
      expect(el).not.toBeNull();
      expect(el).toHaveAttribute("data-landing-screen", id);
    }
    expect(screen.getByTestId("landing-section-tarot")).toBeInTheDocument();
    expect(screen.getByTestId("landing-section-compatibility")).toBeInTheDocument();
    expect(screen.getByTestId("landing-section-practices")).toBeInTheDocument();
    expect(screen.getByTestId("landing-section-today")).toBeInTheDocument();
    expect(screen.getByTestId("landing-section-why")).toBeInTheDocument();
    expect(screen.getByTestId("landing-section-cta")).toBeInTheDocument();

    expect(screen.getByRole("heading", { name: /todayflow видит не только твой день/i })).toBeInTheDocument();
    expect(screen.getByText(/твой today каждое утро/i)).toBeInTheDocument();
    expect(screen.getByText(/зачем возвращаются/i)).toBeInTheDocument();

    // Top nav → landing sections (not product routes)
    expect(screen.getAllByRole("link", { name: /^таро$/i }).some((el) => el.getAttribute("href") === "#tarot")).toBe(
      true,
    );
    expect(
      screen
        .getAllByRole("link", { name: /^совместимость$/i })
        .some((el) => el.getAttribute("href") === "#compatibility"),
    ).toBe(true);
    expect(
      screen.getAllByRole("link", { name: /как это работает/i }).some((el) => el.getAttribute("href") === "#today"),
    ).toBe(true);
    expect(
      screen.getAllByRole("link", { name: /почему возвращаются/i }).some((el) => el.getAttribute("href") === "#why"),
    ).toBe(true);

    // In-section CTAs open product pages
    expect(screen.getByRole("link", { name: /открыть таро/i })).toHaveAttribute("href", "/tarot");
    expect(screen.getByRole("link", { name: /проверить пару/i })).toHaveAttribute("href", "/compatibility");
  });
});
