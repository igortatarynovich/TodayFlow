import { render, screen } from "@testing-library/react";
import { ProfileQuickMapScreen } from "@/components/profile/quickMap/ProfileQuickMapScreen";
import type { ProfileQuickMapViewModel } from "@/lib/profilePage/buildProfileQuickMapData";

const baseModel: ProfileQuickMapViewModel = {
  pageLabel: "Карта личности",
  archetype: "Sage",
  identitySummary: "Ты лучше всего раскрываешься там, где есть понимание смысла.",
  strengthens: ["понятные правила", "интеллектуальная свобода"],
  drains: ["хаос", "постоянные срочные задачи"],
  decisionStyle: "Сначала структура, потом шаг.",
  perceivedAs: ["спокойный", "умный"],
  thriveAreas: ["Карьера", "Аналитика"],
  lifeMission: "Научиться не только понимать мир, но и воплощать идеи.",
  frameworkTitle: "Почему портрет сложился так",
  frameworkLead: "Архетип, знак и число пути складываются в один сценарий.",
  frameworkAnchors: [{ id: "sun", label: "Солнце в Водолее" }],
  frameworkCards: [
    {
      id: "sun",
      title: "Солнце",
      anchor: "в Водолее",
      body: "Системное мышление.",
    },
  ],
};

describe("ProfileQuickMapScreen", () => {
  it("renders Quick Map layers and collapsed deep section", () => {
    render(
      <ProfileQuickMapScreen
        model={baseModel}
        onOpenBirthData={() => {}}
        deep={{
          natalPreview: null,
          previewError: null,
          onReloadPreview: () => {},
          lifeMapSections: [],
        }}
      />,
    );

    expect(screen.getByTestId("profile-quick-map")).toBeInTheDocument();
    expect(screen.getByTestId("profile-portrait-section")).toBeInTheDocument();
    expect(screen.getByText("Кто я")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Sage" })).toBeInTheDocument();
    expect(screen.getByText("Что тебя усиливает")).toBeInTheDocument();
    expect(screen.getByText("понятные правила")).toBeInTheDocument();
    expect(screen.getByText("Почему портрет сложился так")).toBeInTheDocument();
    expect(screen.getByText("Следующий уровень")).toBeInTheDocument();
    expect(screen.getByText("Карта личности")).toBeInTheDocument();
    expect(screen.getByTestId("profile-portal-deep")).toBeInTheDocument();
    expect(screen.getByTestId("profile-maps-preview")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Перейти в Today" })).toHaveAttribute("href", "/today");
  });

  it("supports shape audit mode for textless visual QA", () => {
    process.env.NEXT_PUBLIC_PROFILE_SHAPE_AUDIT = "1";
    render(
      <ProfileQuickMapScreen
        model={baseModel}
        onOpenBirthData={() => {}}
        deep={{
          natalPreview: null,
          previewError: null,
          onReloadPreview: () => {},
          lifeMapSections: [],
        }}
      />,
    );

    expect(screen.getByTestId("profile-quick-map").className).toMatch(/quickMapShapeAudit/);
    delete process.env.NEXT_PUBLIC_PROFILE_SHAPE_AUDIT;
  });

  it("renders life spheres when provided", () => {
    render(
      <ProfileQuickMapScreen
        model={baseModel}
        onOpenBirthData={() => {}}
        lifeSpheres={[
          {
            id: "love",
            title: "Любовь",
            accent: "#d16a8d",
            how: "В отношениях ты ищешь ясность.",
            need: "Честный контакт.",
            risk: "Контроль.",
            turnsOn: "Спокойствие.",
            turnsOff: "Пассивная агрессия.",
            helps: "Короткие договорённости.",
            inSystem: "Today и Compatibility.",
          },
        ]}
      />,
    );

    expect(screen.getByText("Сферы жизни")).toBeInTheDocument();
    expect(screen.getByText("Любовь")).toBeInTheDocument();
    expect(screen.getByText("В отношениях ты ищешь ясность.")).toBeInTheDocument();
  });
});
