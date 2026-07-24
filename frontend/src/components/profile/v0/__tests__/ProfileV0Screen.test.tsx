import { render, screen } from "@testing-library/react";
import { ProfileV0Screen } from "@/components/profile/v0/ProfileV0Screen";
import type { ProfileV0ViewModel } from "@/lib/profilePage/buildProfileV0Data";

const baseModel: ProfileV0ViewModel = {
  header: {
    displayName: "Igor",
    archetypeLabel: "Sage",
    sunSignDisplay: "Водолей",
    lifePath: 7,
    poeticCaption: "Системное мышление",
    tagline: null,
    intro: "Ты лучше всего раскрываешься там, где есть понимание смысла.",
    metaLine: null,
    qualities: [{ title: "Ясность", subtitle: "структура" }],
  },
  who: {
    archetypeLabel: "Sage",
    whyManifest: "Потому что путь семёрки тянет к глубине.",
    layerHint: "Это не приговор — опора для решений.",
    whyInsights: [],
  },
  numbers: null,
  socialMirror: {
    lead: "Люди видят в тебе спокойствие.",
    observations: ["Сдержанный"],
    runtimeGenerated: false,
    expand: { firstImpression: null, broadcast: null, blindSpot: null },
  },
  love: null,
  money: null,
  action: null,
  deepDiveHref: "/profile/chart",
};

describe("ProfileV0Screen", () => {
  it("renders portrait band, social mirror, thin Maps CTA (PR-4), and portal without name entity", async () => {
    render(<ProfileV0Screen model={baseModel} onOpenBirthData={() => {}} />);
    expect(screen.getByTestId("profile-portrait-section")).toBeInTheDocument();
    expect(screen.getByText(baseModel.socialMirror!.lead)).toBeInTheDocument();
    expect(screen.queryByText("Имя")).not.toBeInTheDocument();
    expect(screen.queryByTestId("profile-living-maps-section")).not.toBeInTheDocument();
    expect(screen.queryByTestId("profile-maps-preview")).not.toBeInTheDocument();
    const mapsCta = screen.getByTestId("profile-maps-thin-cta");
    expect(mapsCta).toHaveTextContent(/Как жизнь меняется/);
    expect(screen.getByRole("link", { name: /Карты и наблюдения/i })).toHaveAttribute(
      "href",
      "/maps/mood",
    );
    expect(screen.getByText("Следующий уровень")).toBeInTheDocument();
    expect(screen.getByText("Войти")).toBeInTheDocument();
  });
});
