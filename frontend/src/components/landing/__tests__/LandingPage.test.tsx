import { render, screen } from "@testing-library/react";
import { LandingPage } from "@/components/landing/LandingPage";
import { PRODUCT_WEB_LANDING_SECTION_IDS } from "@/components/product-ui/productWebLandingContent";

describe("LandingPage", () => {
  beforeAll(() => {
    HTMLCanvasElement.prototype.getContext = (() => null) as typeof HTMLCanvasElement.prototype.getContext;
  });

  it("renders brand-first screens: locked line as H1, moon signature, thesis before tools", () => {
    render(<LandingPage signupHref="/onboarding/welcome?fresh=1" loginHref="/auth?mode=login" />);

    expect(screen.getByTestId("landing-page")).toBeInTheDocument();
    expect(screen.getByTestId("landing-hero-moon")).toBeInTheDocument();
    expect(screen.queryByTestId("landing-orbit-viz")).not.toBeInTheDocument();
    expect(screen.queryByTestId("landing-hero-plate")).not.toBeInTheDocument();
    expect(screen.getByTestId("landing-today-plate")).toBeInTheDocument();
    expect(screen.getByTestId("landing-service-plate-tarot")).toBeInTheDocument();
    expect(screen.getByTestId("landing-service-plate-compatibility")).toBeInTheDocument();
    expect(screen.getByTestId("landing-service-plate-practices")).toBeInTheDocument();
    expect(screen.getByTestId("landing-cta-plate")).toBeInTheDocument();

    for (const id of PRODUCT_WEB_LANDING_SECTION_IDS) {
      const el = document.getElementById(id);
      expect(el).not.toBeNull();
      expect(el).toHaveAttribute("data-landing-screen", id);
    }
    expect(screen.queryByTestId("landing-section-why")).not.toBeInTheDocument();
    expect(screen.getByTestId("landing-section-trust")).toBeInTheDocument();
    expect(screen.getByTestId("landing-section-today")).toBeInTheDocument();
    expect(screen.getByTestId("landing-section-compatibility")).toBeInTheDocument();
    expect(screen.getByTestId("landing-section-tarot")).toBeInTheDocument();
    expect(screen.getByTestId("landing-section-practices")).toBeInTheDocument();
    expect(screen.getByTestId("landing-section-cta")).toBeInTheDocument();

    expect(
      screen.getByRole("heading", {
        name: /точные астрономические данные\.\s*столетия астрологической интерпретации\.\s*один личный взгляд\./i,
      }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: /todayflow видит не только твой день/i })).not.toBeInTheDocument();
    expect(screen.getAllByText(/NASA JPL/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/на чём стоит todayflow/i)).toBeInTheDocument();
    expect(screen.getByText(/твой today каждое утро/i)).toBeInTheDocument();
    expect(screen.queryByText(/зачем возвращаются/i)).not.toBeInTheDocument();

    expect(
      screen.getAllByRole("link", { name: /на чём стоит/i }).some((el) => el.getAttribute("href") === "#trust"),
    ).toBe(true);
    expect(
      screen.getAllByRole("link", { name: /^сегодня$/i }).some((el) => el.getAttribute("href") === "#today"),
    ).toBe(true);
    expect(
      screen
        .getAllByRole("link", { name: /^совместимость$/i })
        .some((el) => el.getAttribute("href") === "#compatibility"),
    ).toBe(true);
    expect(screen.getAllByRole("link", { name: /^таро$/i }).some((el) => el.getAttribute("href") === "#tarot")).toBe(
      true,
    );

    expect(screen.getByRole("link", { name: /открыть таро/i })).toHaveAttribute("href", "/tarot");
    expect(screen.getByRole("link", { name: /проверить пару/i })).toHaveAttribute("href", "/compatibility");
    expect(screen.queryByRole("link", { name: /посмотреть динамику вашей связи/i })).not.toBeInTheDocument();
  });
});
