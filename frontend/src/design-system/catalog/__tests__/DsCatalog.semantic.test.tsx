import { render, screen } from "@testing-library/react";
import { DsCatalog } from "@/design-system/catalog/DsCatalog";

describe("DsCatalog · Task 2.9 semantic layers", () => {
  it("mounts and shows semantic layers specimen", () => {
    render(<DsCatalog />);
    expect(screen.getByTestId("ds-catalog")).toBeInTheDocument();
    expect(screen.getByText(/Semantic layers/i)).toBeInTheDocument();
    expect(screen.getByTestId("ds-quote")).toBeInTheDocument();
    expect(screen.getAllByTestId("ds-callout").length).toBeGreaterThanOrEqual(3);
  });
});
