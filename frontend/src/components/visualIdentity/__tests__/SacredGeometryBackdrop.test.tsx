import { render, screen } from "@testing-library/react";
import { SacredGeometryBackdrop } from "@/components/visualIdentity/SacredGeometryBackdrop";

describe("SacredGeometryBackdrop", () => {
  it("renders today preset for Hero Medium composition", () => {
    render(<SacredGeometryBackdrop emphasis="soft" preset="today" />);

    const backdrop = screen.getByTestId("foundation-geometry-backdrop");
    expect(backdrop).toHaveAttribute("data-geometry-preset", "today");

    const layers = backdrop.querySelector("[data-geometry-preset='today']");
    expect(layers).toBeTruthy();
    expect(layers?.querySelector("circle")).toBeTruthy();
    expect(layers?.querySelector("pattern")).toBeNull();
  });

  it("renders portal grid for strong portal composition", () => {
    render(<SacredGeometryBackdrop emphasis="strong" preset="portal" tone="dark" />);

    const backdrop = screen.getByTestId("foundation-geometry-backdrop");
    expect(backdrop).toHaveAttribute("data-geometry-preset", "portal");
    expect(backdrop.className).toMatch(/dark/);

    const layers = backdrop.querySelector("[data-geometry-preset='portal']");
    expect(layers).toHaveAttribute("data-geometry-tone", "dark");
    expect(layers?.querySelector("pattern")).toBeTruthy();
  });

  it("renders profile sacred rings without grid", () => {
    render(<SacredGeometryBackdrop emphasis="soft" preset="profile" />);

    const layers = screen.getByTestId("foundation-geometry-backdrop").querySelector("[data-geometry-preset='profile']");
    expect(layers?.querySelectorAll("circle").length).toBeGreaterThanOrEqual(2);
    expect(layers?.querySelector("pattern")).toBeNull();
  });

  it("resolves portal preset from strong emphasis when preset omitted", () => {
    render(<SacredGeometryBackdrop emphasis="strong" />);
    expect(screen.getByTestId("foundation-geometry-backdrop")).toHaveAttribute("data-geometry-preset", "portal");
  });
});
