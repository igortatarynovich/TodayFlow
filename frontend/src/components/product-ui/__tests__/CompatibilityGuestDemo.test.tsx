import { render, screen } from "@testing-library/react";
import { CompatibilityGuestDemo } from "../CompatibilityGuestDemo";

describe("CompatibilityGuestDemo", () => {
  it("shows demo dynamics and CTAs for guests", () => {
    render(<CompatibilityGuestDemo locale="ru" />);
    expect(screen.getByTestId("compatibility-guest-demo")).toBeInTheDocument();
    expect(screen.getByText("Главная динамика")).toBeInTheDocument();
    expect(screen.getByText("Сильная сторона")).toBeInTheDocument();
    expect(screen.getByText("Зона напряжения")).toBeInTheDocument();
    expect(screen.getByText("Практический совет")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Проверить свою пару" })).toHaveAttribute(
      "href",
      "/compatibility/analyze",
    );
  });
});
