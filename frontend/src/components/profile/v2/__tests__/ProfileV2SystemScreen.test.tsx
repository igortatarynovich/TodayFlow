import { render, screen } from "@testing-library/react";
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
  it("renders five-zone disclosure ladder from Figma profile-v2-system", () => {
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
    expect(screen.getByText("Профиль как живая карта")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Факты" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Характер" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Направление" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Живая история" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Небо" })).toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-sky-section")).toBeInTheDocument();
    expect(screen.getByText("МОИ ДНИ · ПОСЛЕДНЯЯ НЕДЕЛЯ")).toBeInTheDocument();
    expect(screen.getByText("Исследователь")).toBeInTheDocument();
    expect(screen.getByText("ясная система")).toBeInTheDocument();
    expect(screen.getAllByText(/лабрадорит/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/68%/).length).toBeGreaterThan(0);
  });
});
