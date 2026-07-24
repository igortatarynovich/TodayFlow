import { render, screen } from "@testing-library/react";
import { ProductGuestShowcase } from "../ProductGuestShowcase";
import { ProductShellLoading } from "../ProductShellStates";

describe("ProductGuestShowcase", () => {
  it("renders blur preview and gate children", () => {
    render(
      <ProductGuestShowcase>
        <div>Gate card</div>
      </ProductGuestShowcase>,
    );
    expect(screen.getByTestId("product-guest-showcase")).toBeInTheDocument();
    expect(screen.getByText("Твой Today каждое утро")).toBeInTheDocument();
    expect(screen.getByText("Gate card")).toBeInTheDocument();
  });
});

describe("ProductShellLoading", () => {
  it("renders page-geometry skeleton instead of spinner-only", () => {
    render(<ProductShellLoading label="Сессия…" />);
    const status = screen.getByTestId("product-shell-loading");
    expect(status).toBeInTheDocument();
    expect(status).toHaveAttribute("aria-busy", "true");
    expect(screen.getByText("Сессия…")).toBeInTheDocument();
    expect(screen.getAllByLabelText("Loading content").length).toBeGreaterThanOrEqual(3);
  });
});
