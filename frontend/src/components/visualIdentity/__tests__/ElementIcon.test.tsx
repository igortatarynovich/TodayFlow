import { render, screen } from "@testing-library/react";
import { ElementIcon } from "@/components/visualIdentity/ElementIcon";

describe("ElementIcon", () => {
  it("renders asset-mode element symbol at requested size", () => {
    render(<ElementIcon element="Fire" size={24} stroke="currentColor" />);
    const symbol = screen.getByTestId("element-symbol");
    expect(symbol).toBeInTheDocument();
    expect(symbol).toHaveStyle({ width: "24px", height: "24px" });
  });

  it("resolves RU element names", () => {
    render(<ElementIcon element="Вода" size={20} />);
    expect(screen.getByTestId("element-symbol")).toBeInTheDocument();
  });

  it("returns null for unknown elements", () => {
    const { container } = render(<ElementIcon element="Ether" />);
    expect(container.firstChild).toBeNull();
  });
});
