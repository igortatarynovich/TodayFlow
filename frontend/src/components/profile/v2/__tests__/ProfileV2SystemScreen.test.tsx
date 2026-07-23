import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
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
  astro: { sun_sign: "virgo", sun_element: "earth" },
  numerology: { life_path: 7 },
  baseline: { archetype_seed: "explorer" },
  profile_contract_v1: {
    contract_version: "v1",
    recognition_line: "Ты первым видишь структуру.",
    identity_core: "Длинное ядро.",
    strengths: ["ясная система"],
    growth_zones: ["спешка ломает точность"],
    relationship_style: "Сначала доверие, потом открытость.",
    money_style: "",
    decision_style: "Сначала тело, потом структура.",
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
        insight: "Сила в точности, но спешка всё сбивает.",
        grounded_on: [{ label: "Рост: спешка" }],
        help: "Один тихий проход перед решением.",
        living_evidence: ["опять поторопился"],
        source_fields: ["growth_zones", "helps"],
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
  profile_matrix_v0: {
    revealed_slots: {
      cultural_catalog: {
        color: "изумрудный",
        traditions: [{ label: "Китайский", value: "Лошадь" }],
        stones: [],
      },
      natal_structure: {
        angles: { ascendant: { sign: "Leo" } },
        houses: Array.from({ length: 12 }, (_, i) => ({ cusp: i + 1 })),
      },
      emotional_style: "Чувствует глубже.",
      helps: ["тишина"],
      tensions_growth: { growth_zones: ["спешка"] },
    },
  },
} as never;

const live = buildProfileV2LiveContext({
  coreProfile: journeyCore,
  cum: { confidence: { overall: 0.68 } } as never,
  thriveAreas: baseModel.thriveAreas,
});

function renderJourney(extra?: Partial<Parameters<typeof ProfileV2SystemScreen>[0]>) {
  return render(
    <ProfileV2SystemScreen
      model={baseModel}
      live={live}
      coreProfile={journeyCore}
      onOpenBirthData={() => {}}
      deep={{
        natalPreview: null,
        previewError: null,
        onReloadPreview: () => {},
        lifeMapSections: [],
      }}
      lifeSpheres={[
        {
          id: "mission",
          title: "Миссия",
          accent: "#c9a96e",
          how: "как",
          need: "нужно",
          risk: "риск",
          turnsOn: "включает",
          turnsOff: "",
          helps: "",
          inSystem: "",
        },
        {
          id: "growth",
          title: "Рост",
          accent: "#8b6a3e",
          how: "как",
          need: "нужно",
          risk: "риск",
          turnsOn: "включает",
          turnsOff: "",
          helps: "",
          inSystem: "",
        },
      ]}
      {...extra}
    />,
  );
}

describe("ProfileV2SystemScreen journey rewire", () => {
  it("renders five journey scenes; matrix does not become PersonStory gallery", async () => {
    const user = userEvent.setup();
    renderJourney();

    expect(screen.getByTestId("profile-v2-system")).toBeInTheDocument();
    expect(screen.queryByTestId("profile-v2-person-story")).not.toBeInTheDocument();

    // Hero: archetype name as H1, recognition line separate, ≤3 markers
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(/Исследователь/i);
    expect(screen.getByTestId("profile-v2-recognition-line")).toHaveTextContent("структуру");
    const markers = screen.getByTestId("profile-v2-identity-markers");
    expect(markers.querySelectorAll(":scope > *").length).toBeLessThanOrEqual(3);
    expect(markers).toHaveTextContent("Дева");
    expect(markers).toHaveTextContent("Земля");
    expect(markers).toHaveTextContent("Путь 7");

    // Why + insight + effort in primary scroll (effort ungated)
    expect(screen.getByTestId("profile-v2-why")).toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-why-anchor-lp")).toHaveTextContent("Число пути");
    expect(screen.getByTestId("profile-v2-insight")).toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-insight-node")).toHaveTextContent("Ясность vs скорость");
    expect(screen.getByTestId("profile-v2-insight-living")).toHaveTextContent("поторопился");
    expect(screen.getByTestId("profile-v2-effort")).toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-effort-vector")).toHaveTextContent("тихий проход");

    // Bridge immediately after effort — no catalog/natal between
    const root = screen.getByTestId("profile-v2-system");
    const order = [
      "profile-v2-recognition",
      "profile-v2-why",
      "profile-v2-insight",
      "profile-v2-effort",
      "profile-v2-bridge",
    ];
    const ids = order.map((id) => root.querySelector(`#${id}`));
    expect(ids.every(Boolean)).toBe(true);
    for (let i = 1; i < ids.length; i += 1) {
      const prev = ids[i - 1]!;
      const next = ids[i]!;
      expect(
        Boolean(prev.compareDocumentPosition(next) & Node.DOCUMENT_POSITION_FOLLOWING),
      ).toBe(true);
    }

    expect(screen.getByTestId("profile-v2-open-today")).toHaveAttribute("href", "/today");

    // Catalog / natal not in main journey — only after explore open
    expect(screen.queryByTestId("profile-v2-progressive-details")).not.toBeInTheDocument();
    expect(screen.queryByTestId("profile-v2-natal")).not.toBeInTheDocument();
    expect(screen.queryByText(/12 куспид/i)).not.toBeInTheDocument();
    expect(screen.queryByTestId("profile-v2-chapter-cultural_catalog")).not.toBeInTheDocument();

    // No three mandatory strengths/tensions/helps sections
    expect(screen.queryByTestId("profile-v2-chapter-strengths")).not.toBeInTheDocument();
    expect(screen.queryByTestId("profile-v2-chapter-tensions_growth")).not.toBeInTheDocument();
    expect(screen.queryByTestId("profile-v2-chapter-helps")).not.toBeInTheDocument();

    await user.click(screen.getByTestId("profile-v2-open-explore"));
    expect(await screen.findByTestId("profile-v2-explore-body")).toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-progressive-details")).toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-detail-cultural_catalog")).toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-natal")).toBeInTheDocument();
    expect(screen.queryByText(/Шаг 6/i)).not.toBeInTheDocument();
  });

  it("omits living evidence when absent and still shows effort without explore", () => {
    const sparseCore = {
      ...journeyCore,
      insight_nodes_v0: {
        nodes: [
          {
            id: "n1",
            kind: "tension",
            title: "Ясность vs скорость",
            insight: "Сила в точности.",
            grounded_on: [{ label: "Рост" }],
            help: "Один проход.",
            living_evidence: [],
          },
        ],
      },
      profile_matrix_v0: undefined,
    } as never;

    render(
      <ProfileV2SystemScreen
        model={baseModel}
        live={buildProfileV2LiveContext({ coreProfile: sparseCore, cum: null })}
        coreProfile={sparseCore}
        onOpenBirthData={() => {}}
      />,
    );

    expect(screen.getByTestId("profile-v2-insight")).toBeInTheDocument();
    expect(screen.queryByTestId("profile-v2-insight-living")).not.toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-effort")).toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-bridge")).toBeInTheDocument();
  });

  it("does not invent fake progress percentages on effort", () => {
    renderJourney();
    expect(screen.getByTestId("profile-v2-effort").textContent).not.toMatch(/%/);
  });

  it("keeps hero to one name, one recognition line, and ≤3 markers", () => {
    renderJourney();
    const hero = screen.getByTestId("profile-v2-recognition");
    expect(within(hero).getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByTestId("profile-v2-recognition-line")).toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-identity-markers").querySelectorAll(":scope > *").length).toBeLessThanOrEqual(3);
  });

  it("renders why as claim anchors plus synthesis, not cusp dump", () => {
    renderJourney();
    const why = screen.getByTestId("profile-v2-why");
    expect(within(why).getByText(/Число пути/i)).toBeInTheDocument();
    expect(within(why).getByText(/Солнце в Деве/i)).toBeInTheDocument();
    expect(why.textContent).not.toMatch(/12 куспид/i);
  });

  it("renders one insight node cascade, not strengths/tensions/helps chapters", () => {
    renderJourney();
    expect(screen.getByTestId("profile-v2-insight-node")).toBeInTheDocument();
    expect(screen.getByTestId("profile-v2-insight-help")).toBeInTheDocument();
    expect(screen.queryByTestId("profile-v2-chapter-strengths")).not.toBeInTheDocument();
    expect(screen.queryByTestId("profile-v2-chapter-tensions_growth")).not.toBeInTheDocument();
    expect(screen.queryByTestId("profile-v2-chapter-helps")).not.toBeInTheDocument();
  });
});

describe("PROFILE_V2_COPY lexicon gate", () => {
  it("forbids day-state words in production Profile V2 copy", () => {
    const blob = JSON.stringify({ PROFILE_V2_COPY, PROFILE_V2_DEPTH_NAV });
    for (const token of PROFILE_V2_FORBIDDEN_LEXICON) {
      expect(blob).not.toContain(token);
    }
  });

  it("depth nav is five journey steps without Шаг 6 natal", () => {
    expect(PROFILE_V2_DEPTH_NAV).toHaveLength(5);
    expect(PROFILE_V2_DEPTH_NAV.map((s) => s.id)).toEqual([
      "recognition",
      "why",
      "insight",
      "effort",
      "bridge",
    ]);
  });
});
