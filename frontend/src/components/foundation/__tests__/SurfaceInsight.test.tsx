import { render, screen } from "@testing-library/react";
import { SurfaceInsight, SurfaceInsightBody } from "@/components/foundation/SurfaceInsight";

describe("SurfaceInsight", () => {
  it("renders Surface B insight panel with eyebrow and body", () => {
    render(
      <SurfaceInsight eyebrow="Профиль" variant="warm" data-testid="surface-insight">
        <SurfaceInsightBody>Текст подсказки</SurfaceInsightBody>
      </SurfaceInsight>,
    );

    expect(screen.getByTestId("surface-insight")).toBeInTheDocument();
    expect(screen.getByText("Профиль")).toBeInTheDocument();
    expect(screen.getByText("Текст подсказки")).toBeInTheDocument();
  });
});
