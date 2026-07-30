import { render, screen } from "@testing-library/react";
import { GuestTodayDemoSsr } from "@/components/demo/GuestTodayDemoSsr";

describe("GuestTodayDemoSsr", () => {
  it("renders Theme Focus Practice Memory and invite CTA", () => {
    render(<GuestTodayDemoSsr />);
    expect(screen.getByTestId("demo-today-ssr")).toBeInTheDocument();
    expect(screen.getByText("Тема")).toBeInTheDocument();
    expect(screen.getByText("Фокус")).toBeInTheDocument();
    expect(screen.getByText("Практика")).toBeInTheDocument();
    expect(screen.getByText("Память о вчера")).toBeInTheDocument();
    expect(screen.getByTestId("demo-today-cta")).toHaveAttribute("href", "/onboarding/invite");
    expect(screen.getByText(/После первого Today вечером/)).toBeInTheDocument();
  });
});
