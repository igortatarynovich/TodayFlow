import { render, screen } from "@testing-library/react";
import { NumberIcon } from "@/components/visualIdentity/NumberIcon";
import { numberDigitAssetPath, resolveNumberDigits } from "@/lib/visualIdentity/registry";

describe("NumberIcon", () => {
  it("renders asset digits at requested size", () => {
    render(<NumberIcon value={7} size={32} />);
    const symbol = screen.getByTestId("number-symbol");
    expect(symbol).toHaveAttribute("data-visual", "asset");
    expect(symbol).toHaveAttribute("data-value", "7");
    expect(symbol).toHaveStyle({ height: "32px" });
    const img = symbol.querySelector("img");
    expect(img).toHaveAttribute("src", "/images/icons/numbers/7.webp");
  });

  it("composes master numbers from digit assets", () => {
    render(<NumberIcon value={11} size={28} />);
    const imgs = screen.getByTestId("number-symbol").querySelectorAll("img");
    expect(imgs).toHaveLength(2);
    expect(imgs[0]).toHaveAttribute("src", "/images/icons/numbers/1.webp");
    expect(imgs[1]).toHaveAttribute("src", "/images/icons/numbers/1.webp");
  });

  it("returns null for empty placeholders", () => {
    const { container } = render(<NumberIcon value="—" />);
    expect(container.firstChild).toBeNull();
  });
});

describe("number registry", () => {
  it("maps digits 1–9 to public WebP paths", () => {
    expect(numberDigitAssetPath("5")).toBe("/images/icons/numbers/5.webp");
    expect(resolveNumberDigits("22")).toEqual(["2", "2"]);
    expect(resolveNumberDigits(0)).toBeNull();
  });
});
