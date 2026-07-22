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

const journeyCore = {
  astro: { sun_sign: "Virgo" },
  baseline: { archetype_seed: "explorer" },
  profile_contract_v1: {
    contract_version: "v1",
    recognition_line: "Ты первым видишь структуру.",
    identity_core: "Длинное ядро.",
    strengths: ["ясная система"],
    growth_zones: ["спешка"],
    relationship_style: "",
    money_style: "",
    decision_style: "Сначала тело.",
    recurring_patterns: ["нужна ясность"],
    helps: ["тишина перед решением"],
  },
  portrait_why_v0: {
    title: "Почему портрет такой",
    selected_by: [{ id: "lp", class: "selected_by", label: "Число пути 7 → Исследователь" }],
    portrait_influenced_by: [{ id: "sun", class: "portrait_influenced_by", label: "Солнце в Деве" }],
    honesty_line: "Повторы проявятся со временем.",
  },
  insight_nodes_v0: {
    nodes: [
      {
        id: "n1",
        kind: "tension",
        title: "Ясность vs скорость",
        insight: "Сила в точности.",
        grounded_on: [{ label: "Рост: спешка" }],
        help: "Один тихий проход перед решением.",
        living_evidence: ["опять поторопился"],
      },
    ],
  },
  effort_vector_v0: {
    effort_vector: "Один тихий проход перед решением.",
  },
  bridge_line_v0: {
    bridge_line: "Особенность уже ясна. Today продолжает путь.",
    leads_to: "today",
  },
} as never;

const live = buildProfileV2LiveContext({
  coreProfile: journeyCore,
  cum: { confidence: { overall: 0.68 } } as never,
  thriveAreas: baseModel.thriveAreas,
});

describe("ProfileV2SystemScreen", () => {
  it("renders journey Steps 1–5 and demotes equal character cards", () => {
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
    expect(screen.getByRole("heading", { level: 1, name: /Исследователь/i })).toBeInTheDocument();
    expect(screen.queryAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByTestId("profile-v2-recognition-line")).toHaveTextContent("структуру");
    expect(screen.getByTestId("profile-v2-why")).toHaveTextContent("Число пути 7");
    expect(screen.getByTestId("profile-v2-insight")).toHaveTextContent("Ясность vs скорость");
    expect(screen.getByTestId("profile-v2-living-adjacent")).toHaveTextContent(
      "не доказательство",
    );
    expect(screen.getByTestId("profile-v2-effort")).toHaveTextContent("тихий проход");
    expect(screen.getByTestId("profile-v2-bridge")).toHaveTextContent("Открыть Today");
    expect(screen.getByRole("link", { name: /Открыть Today/i })).toHaveAttribute("href", "/today");
    expect(screen.getByTestId("profile-v2-character-more")).toBeInTheDocument();
    expect(document.getElementById("profile-v2-sources-title")).toHaveTextContent("Источники");
    expect(screen.queryByText(/Твой личный профиль/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Камень дня/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/68%/)).not.toBeInTheDocument();
  });

  it("omits effort and bridge when projections are null", () => {
    const sparseLive = buildProfileV2LiveContext({
      coreProfile: {
        astro: { sun_sign: "Virgo" },
        baseline: { archetype_seed: "explorer" },
        profile_contract_v1: {
          contract_version: "v1",
          recognition_line: "Ты первым видишь структуру.",
          identity_core: "Ядро.",
          strengths: [],
          growth_zones: [],
          relationship_style: "",
          money_style: "",
          decision_style: "",
          recurring_patterns: [],
        },
      } as never,
      cum: null,
    });

    render(
      <ProfileV2SystemScreen
        model={baseModel}
        live={sparseLive}
        onOpenBirthData={() => {}}
      />,
    );

    expect(screen.getByTestId("profile-v2-recognition-line")).toBeInTheDocument();
    expect(screen.queryByTestId("profile-v2-insight")).not.toBeInTheDocument();
    expect(screen.queryByTestId("profile-v2-effort")).not.toBeInTheDocument();
    expect(screen.queryByTestId("profile-v2-bridge")).not.toBeInTheDocument();
  });

  it("puts the depth ladder in the right rail component", () => {
    render(<ProfileV2DepthRail />);
    const rail = screen.getByTestId("profile-v2-depth-rail");
    expect(rail).toBeInTheDocument();
    expect(rail).toHaveTextContent("Узнавание");
    expect(rail).toHaveTextContent("Узел");
    expect(rail).toHaveTextContent("Усилие");
    expect(rail).toHaveTextContent("Дальше");
    expect(rail).toHaveTextContent("Источники");
    expect(rail.querySelectorAll("a[href^='#profile-v2-']")).toHaveLength(6);
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
