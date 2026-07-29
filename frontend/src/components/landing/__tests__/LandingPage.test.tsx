import { render, screen } from "@testing-library/react";
import { LandingPage } from "@/components/landing/LandingPage";

describe("LandingPage", () => {
  it("renders Product UI web landing sections with anchors", () => {
    render(<LandingPage signupHref="/onboarding/welcome?fresh=1" loginHref="/auth?mode=login" />);

    expect(screen.getByTestId("landing-page")).toBeInTheDocument();
    expect(screen.getByTestId("landing-orbit-viz")).toBeInTheDocument();
    expect(screen.getByTestId("landing-section-try")).toBeInTheDocument();
    expect(screen.getByTestId("landing-section-today")).toBeInTheDocument();
    expect(screen.getByTestId("landing-section-why")).toBeInTheDocument();
    expect(screen.getByTestId("landing-section-cta")).toBeInTheDocument();

    expect(screen.getByRole("heading", { name: /интересно, что/i })).toBeInTheDocument();
    expect(screen.getByText(/попробуй сейчас/i)).toBeInTheDocument();
    expect(screen.getByText(/твой today каждое утро/i)).toBeInTheDocument();
    expect(screen.getByText(/зачем возвращаются/i)).toBeInTheDocument();

    expect(screen.getAllByRole("link", { name: /создать мой today/i }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole("link", { name: /^попробовать$/i }).some((el) => el.getAttribute("href") === "#try")).toBe(
      true,
    );
    expect(
      screen.getAllByRole("link", { name: /как это работает/i }).some((el) => el.getAttribute("href") === "#today"),
    ).toBe(true);
    expect(
      screen.getAllByRole("link", { name: /почему возвращаются/i }).some((el) => el.getAttribute("href") === "#why"),
    ).toBe(true);
  });
});
