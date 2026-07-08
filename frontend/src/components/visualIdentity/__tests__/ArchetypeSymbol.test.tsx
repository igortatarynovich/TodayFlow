import { render, screen } from "@testing-library/react";
import { ArchetypeSymbol } from "../ArchetypeSymbol";

describe("ArchetypeSymbol", () => {
  it("renders asset-backed symbol slot with mask tint", () => {
    render(<ArchetypeSymbol seed="Architect" size={80} className="profile-symbol" stroke="#5b4630" />);
    const symbol = screen.getByTestId("archetype-symbol");
    expect(symbol).toHaveClass("profile-symbol");
    expect(symbol).toHaveStyle({
      width: "80px",
      height: "80px",
      backgroundColor: "rgb(91, 70, 48)",
    });
    expect(symbol.style.maskImage).toContain("/images/icons/archetypes/architect.svg");
  });

  it("falls back to unknown slug for unrecognized seeds", () => {
    render(<ArchetypeSymbol seed="Личный архетип" size={48} />);
    const symbol = screen.getByTestId("archetype-symbol");
    expect(symbol.style.maskImage).toContain("/images/icons/archetypes/unknown.svg");
  });

  it("renders expanded archetype set (seeker)", () => {
    render(<ArchetypeSymbol seed="Seeker" size={56} />);
    expect(screen.getByTestId("archetype-symbol").style.maskImage).toContain("/images/icons/archetypes/seeker.svg");
  });
});
