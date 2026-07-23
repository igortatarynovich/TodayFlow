import { render, screen } from "@testing-library/react";
import { ProfileV2SkySection } from "@/components/profile/v2/ProfileV2SkySection";

describe("ProfileV2SkySection constellation", () => {
  it("renders sources as constellation converging on archetype, not equal fact cards", () => {
    render(
      <ProfileV2SkySection
        natalPreview={{ positions: {}, houses: [] }}
        previewError={null}
        onReloadPreview={() => undefined}
        frameworkAnchors={[
          { id: "sun", label: "Солнце в Водолее" },
          { id: "moon", label: "Луна в Весах" },
          { id: "rising", label: "Асцендент в Раке" },
          { id: "mc", label: "MC в Козероге" },
          { id: "archetype", label: "Архетип Мудрец" },
        ]}
        frameworkCards={[]}
      />,
    );

    expect(screen.getByTestId("profile-v2-sources-constellation")).toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-sources-archetype")).toHaveTextContent("Мудрец");
    expect(screen.getByText("Источники личности")).toBeInTheDocument();
    expect(screen.getByText(/из них рождается/i)).toBeInTheDocument();
    expect(screen.queryByText("источники личности")).not.toBeInTheDocument();
    expect(document.querySelector('[class*="factGrid"]')).toBeNull();
    expect(screen.getByText("Солнце в Водолее")).toBeInTheDocument();
  });

  it("keeps long Russian labels readable on nodes", () => {
    const long = "Солнце в Водолее — очень длинная подпись для проверки переноса";
    render(
      <ProfileV2SkySection
        natalPreview={null}
        previewError={null}
        onReloadPreview={() => undefined}
        frameworkAnchors={[
          { id: "sun", label: long },
          { id: "archetype", label: "Архетип Исследователь глубины смысла" },
        ]}
      />,
    );
    expect(screen.getByText(long)).toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-sources-archetype")).toHaveTextContent(
      "Исследователь глубины смысла",
    );
  });
});
