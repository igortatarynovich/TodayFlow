import { render, screen } from "@testing-library/react";
import { ProfileV2DepthRail } from "@/components/profile/v2/ProfileV2DepthRail";
import { ProfileV2SystemScreen } from "@/components/profile/v2/ProfileV2SystemScreen";
import {
  PROFILE_V2_COPY,
  PROFILE_V2_DEPTH_NAV,
  PROFILE_V2_FORBIDDEN_LEXICON,
} from "@/components/profile/v2/profileV2SystemCopy";
import type { ProfileQuickMapViewModel } from "@/lib/profilePage/buildProfileQuickMapData";
import { buildProfileV2LiveContext } from "@/lib/profilePage/buildProfileV2LiveContext";

const baseModel: ProfileQuickMapViewModel = {
  pageLabel: "Карта личности",
  archetype: "Исследователь",
  identitySummary: "Держит смысл через ясный фокус и прямой контакт.",
  strengthens: ["ясная система", "глубокий анализ"],
  drains: ["спешка", "хаос"],
  decisionStyle: "Сначала тело, потом структура.",
  perceivedAs: ["нужна ясность", "держит фокус"],
  thriveAreas: ["точность", "глубина", "ритм"],
  lifeMission: "Собрать ясность в систему, которая помогает другим.",
  frameworkTitle: "Почему портрет сложился так",
  frameworkLead: "Архетип и карта складываются в один сценарий.",
  frameworkAnchors: [
    { id: "sun", label: "Солнце в Деве" },
    { id: "moon", label: "Луна в Рыбах" },
  ],
  frameworkCards: [],
};

const live = buildProfileV2LiveContext({
  coreProfile: {
    astro: { sun_sign: "Virgo" },
    baseline: { archetype_seed: "explorer" },
  } as never,
  cum: { confidence: { overall: 0.68 } } as never,
  thriveAreas: baseModel.thriveAreas,
});

describe("ProfileV2SystemScreen", () => {
  it("keeps a single page heading and PR-4 origin zones", () => {
    render(
      <ProfileV2SystemScreen
        model={baseModel}
        live={live}
        identityPills={["☉ Дева", "☽ Рыбы"]}
        onOpenBirthData={() => {}}
        deep={{
          natalPreview: null,
          previewError: null,
          onReloadPreview: () => {},
          lifeMapSections: [],
        }}
      />,
    );

    expect(screen.getByTestId("profile-v2-system")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 1, name: "Твой личный профиль" })).toBeInTheDocument();
    expect(screen.queryAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(document.getElementById("profile-v2-identity-title")).toHaveTextContent("Идентичность");
    expect(document.getElementById("profile-v2-character-title")).toHaveTextContent("Характер");
    expect(document.getElementById("profile-v2-direction-title")).toHaveTextContent("Направление");
    expect(document.getElementById("profile-v2-evidence-title")).toHaveTextContent("Обоснование");
    expect(document.getElementById("profile-v2-sources-title")).toHaveTextContent("Источники");
    expect(screen.getByTestId("profile-v2-sky-section")).toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-evidence")).toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-depth-jump")).toBeInTheDocument();
    expect(screen.queryByText(/Мои дни/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Камень дня/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Главный шаг/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/68%/)).not.toBeInTheDocument();
    expect(screen.getByText("Исследователь")).toBeInTheDocument();
    expect(screen.getByText("ясная система")).toBeInTheDocument();
    expect(screen.getByText(/Карты и наблюдения/i)).toBeInTheDocument();
  });

  it("puts the depth ladder in the right rail component", () => {
    render(<ProfileV2DepthRail />);
    const rail = screen.getByTestId("profile-v2-depth-rail");
    expect(rail).toBeInTheDocument();
    expect(rail).toHaveTextContent("Идентичность");
    expect(rail).toHaveTextContent("Характер");
    expect(rail).toHaveTextContent("Направление");
    expect(rail).toHaveTextContent("Обоснование");
    expect(rail).toHaveTextContent("Источники");
    expect(rail.querySelectorAll("a[href^='#profile-v2-']")).toHaveLength(5);
  });
});

describe("PROFILE_V2_COPY lexicon gate", () => {
  it("forbids day-state words in production Profile V2 copy", () => {
    const blob = JSON.stringify({ PROFILE_V2_COPY, PROFILE_V2_DEPTH_NAV });
    for (const token of PROFILE_V2_FORBIDDEN_LEXICON) {
      expect(blob).not.toContain(token);
    }
  });
});
