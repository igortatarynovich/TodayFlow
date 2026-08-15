import { render, screen } from "@testing-library/react";
import { ZodiacIcon } from "@/components/visualIdentity/ZodiacIcon";

describe("ZodiacIcon", () => {
  it("renders asset-mode zodiac symbol at requested size", () => {
    render(<ZodiacIcon sign="Aquarius" size={24} stroke="currentColor" />);
    const symbol = screen.getByTestId("zodiac-symbol");
    expect(symbol).toBeInTheDocument();
    expect(symbol).toHaveStyle({ width: "24px", height: "24px" });
  });

  it("resolves RU zodiac names", () => {
    render(<ZodiacIcon sign="Водолей" size={20} />);
    expect(screen.getByTestId("zodiac-symbol")).toBeInTheDocument();
  });

  it("renders illustration variant from painterly portraits", () => {
    render(<ZodiacIcon sign="Leo" size={32} variant="illustration" />);
    const symbol = screen.getByTestId("zodiac-symbol");
    expect(symbol).toHaveAttribute("data-visual", "illustration");
    expect(symbol.querySelector("img")).toHaveAttribute("src", expect.stringContaining("/images/zodiac/leo.webp"));
  });

  it("returns null for unknown signs", () => {
    const { container } = render(<ZodiacIcon sign="Ophiuchus" />);
    expect(container.firstChild).toBeNull();
  });
});
