import { render, screen } from "@testing-library/react";
import { ProfileV2DepthRail } from "@/components/profile/v2/ProfileV2DepthRail";
import { ProfileV2SystemScreen } from "@/components/profile/v2/ProfileV2SystemScreen";
import type { ProfileQuickMapViewModel } from "@/lib/profilePage/buildProfileQuickMapData";
import { buildProfileV2LiveContext } from "@/lib/profilePage/buildProfileV2LiveContext";

const baseModel: ProfileQuickMapViewModel = {
  pageLabel: "Карта личности",
  archetype: "Исследователь",
  identitySummary: "Держит смысл через ясный фокус и прямой контакт.",
  strengthens: ["ясная система", "глубокий анализ"],
  drains: ["спешка", "хаос"],
  decisionStyle: "Сначала тело, потом структура.",
  perceivedAs: ["лабрадорит", "оливковый"],
  thriveAreas: ["точность", "глубина", "ритм"],
  lifeMission: "Собрать ясность в систему, которая помогает другим.",
  frameworkTitle: "Почему система так решила",
  frameworkLead: "Архетип и карта складываются в один сценарий.",
  frameworkAnchors: [
    { id: "sun", label: "Солнце в Деве" },
    { id: "moon", label: "Луна в Рыбах" },
  ],
  frameworkCards: [],
};

const live = buildProfileV2LiveContext({
  coreProfile: null,
  cum: { confidence: { overall: 0.68 } } as never,
  morningRitual: {
    celestial_events: {
      daily_symbols: {
        stone: { name: "Лабрадорит", story_ru: "Держит фокус." },
        color: { name: "Оливковый" },
        totem: { name: "Сова", emoji: "🦉" },
      },
      personal_transits: [{ title: "Меркурий" }],
    },
  } as never,
  thriveAreas: baseModel.thriveAreas,
  identitySummary: baseModel.identitySummary,
});

describe("ProfileV2SystemScreen", () => {
  it("keeps a single page heading and soft zone labels in main", () => {
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
    // Zone titles are labels, not competing page headings.
    expect(document.getElementById("profile-v2-facts-title")?.tagName).toBe("P");
    expect(document.getElementById("profile-v2-character-title")).toHaveTextContent("Характер");
    expect(document.getElementById("profile-v2-direction-title")).toHaveTextContent("Направление");
    expect(document.getElementById("profile-v2-history-title")).toHaveTextContent("Наблюдения");
    expect(document.getElementById("profile-v2-sky-title")).toHaveTextContent("Небо");
    expect(screen.getByTestId("profile-v2-sky-section")).toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-depth-jump")).toBeInTheDocument();
    expect(screen.getByText(/Мои дни · последняя неделя/i)).toBeInTheDocument();
    expect(screen.getByText("Исследователь")).toBeInTheDocument();
    expect(screen.getByText("ясная система")).toBeInTheDocument();
    expect(screen.getAllByText(/лабрадорит/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/68%/).length).toBeGreaterThan(0);
    expect(screen.getByText(/Точность наблюдений/i)).toBeInTheDocument();
  });

  it("puts the depth ladder in the right rail component", () => {
    render(<ProfileV2DepthRail />);
    const rail = screen.getByTestId("profile-v2-depth-rail");
    expect(rail).toBeInTheDocument();
    expect(rail).toHaveTextContent("Факты");
    expect(rail).toHaveTextContent("Характер");
    expect(rail).toHaveTextContent("Направление");
    expect(rail).toHaveTextContent("Наблюдения");
    expect(rail).toHaveTextContent("Небо");
    expect(rail.querySelectorAll("a[href^='#profile-v2-']")).toHaveLength(5);
  });
});
