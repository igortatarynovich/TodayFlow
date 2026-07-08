import { render, screen } from "@testing-library/react";
import { LandingPage } from "@/components/landing/LandingPage";

describe("LandingPage", () => {
  it("renders Product UI web landing sections", () => {
    render(<LandingPage signupHref="/onboarding/welcome?fresh=1" loginHref="/auth?mode=login" />);

    expect(screen.getByTestId("landing-page")).toBeInTheDocument();
    expect(screen.getByText(/узнай паттерны/i)).toBeInTheDocument();
    expect(screen.getByTestId("landing-orbit-viz")).toBeInTheDocument();
    expect(screen.getByTestId("landing-feature-map")).toBeInTheDocument();
    expect(screen.getByTestId("landing-fragment-tarot")).toHaveTextContent(/отшельник/i);
    expect(screen.getByText(/твоя карта ждёт/i)).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: /начать карту/i }).length).toBeGreaterThan(0);
    expect(screen.getByRole("link", { name: /смотреть фильм/i })).toBeInTheDocument();
  });
});
