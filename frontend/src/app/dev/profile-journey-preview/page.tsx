"use client";

import { useMemo, useState } from "react";
import { ProfileV2SystemScreen } from "@/components/profile/v2/ProfileV2SystemScreen";
import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";
import { buildProfileV2LiveContext } from "@/lib/profilePage/buildProfileV2LiveContext";
import type { ProfileQuickMapViewModel } from "@/lib/profilePage/buildProfileQuickMapData";
import type { CoreProfile } from "@/lib/types";

/**
 * Visual QA fixture for Profile Journey V2 (atmosphere, constellation, natal engraving).
 * Production: empty stub. Local / non-production Next builds only.
 */
export default function ProfileJourneyPreviewPage() {
  const isDev = process.env.NODE_ENV !== "production";
  const [theme, setTheme] = useState<"light" | "dark">("light");

  const model = useMemo((): ProfileQuickMapViewModel => {
    return {
      pageLabel: "Карта личности",
      archetype: "Мудрец",
      identitySummary: "Держит смысл через ясный фокус и прямой контакт с тишиной.",
      strengthens: ["ясная система", "глубокий анализ"],
      drains: ["спешка", "хаос"],
      decisionStyle: "Сначала тело, потом структура.",
      perceivedAs: ["нужна ясность", "держит фокус"],
      thriveAreas: ["точность", "глубина", "ритм"],
      lifeMission: "Собрать ясность в систему, которая помогает другим.",
      frameworkTitle: "Почему портрет сложился так",
      frameworkLead: "Архетип и карта складываются в один сценарий.",
      frameworkAnchors: [
        { id: "sun", label: "Солнце в Водолее — очень длинная подпись для проверки переноса" },
        { id: "moon", label: "Луна в Весах" },
        { id: "rising", label: "Асцендент в Раке" },
        { id: "mc", label: "MC в Козероге" },
        { id: "lp", label: "Число пути 7" },
        { id: "archetype", label: "Архетип Мудрец" },
      ],
      frameworkCards: [
        {
          id: "sun",
          title: "Солнце",
          anchor: "sun",
          body: "Свет через систему и дистанцию. Нужен воздух, чтобы не сгореть в чужих сроках.",
        },
        {
          id: "moon",
          title: "Луна",
          anchor: "moon",
          body: "Эмоции ищут гармонию и справедливый обмен, а не громкую сцену.",
        },
      ],
    };
  }, []);

  const coreProfile = useMemo((): CoreProfile => {
    return {
      profile_version: "preview",
      generated_at: "2026-07-23T00:00:00Z",
      is_ready: true,
      missing_fields: [],
      profile_hash: "preview-fixture",
      person: { display_name: "Preview", locale: "ru" },
      astro: { sun_sign: "aquarius", sun_element: "air" },
      numerology: { life_path: 7 },
      baseline: { archetype_seed: "sage" },
      profile_contract_v1: {
        contract_version: "v1",
        recognition_line: "Ты видишь структуру раньше, чем другие замечают хаос.",
        identity_core: "Длинное ядро портрета для проверки вертикального ритма сцены.",
        strengths: ["ясная система"],
        growth_zones: ["спешка ломает точность"],
        relationship_style: "Сначала доверие, потом открытость.",
        money_style: "",
        decision_style: "Сначала тело, потом структура.",
        recurring_patterns: ["нужна ясность"],
        helps: ["тишина перед решением"],
      },
      portrait_why_v0: {
        title: "Почему портрет такой: свет, луна и путь складываются в одну линию.",
        selected_by: [
          {
            id: "archetype_from_life_path",
            class: "selected_by",
            label: "Архетип Мудреца — рассчитан из числа пути 7",
          },
        ],
        portrait_influenced_by: [
          { id: "sun", class: "portrait_influenced_by", label: "Солнце в Водолее" },
          { id: "moon", class: "portrait_influenced_by", label: "Луна в Весах" },
        ],
        honesty_line: "Повторы проявятся со временем — это не баг профиля.",
      },
      insight_nodes_v0: {
        nodes: [
          {
            id: "n1",
            kind: "tension",
            title: "Ясность vs скорость — длинный заголовок для проверки переноса",
            insight:
              "Сила в точности и дистанции, но спешка всё сбивает: появляется шум вместо одной чистой линии.",
            grounded_on: [{ label: "Рост: спешка" }, { label: "Солнце в Водолее" }],
            help: "Один тихий проход перед решением — без чужих дедлайнов в голове.",
            living_evidence: ["опять поторопился и потерял ясность"],
            source_fields: ["growth_zones", "helps"],
          },
        ],
      },
      effort_vector_v0: {
        effort_vector: "Один тихий проход перед решением — защитить фокус до обеда.",
      },
      bridge_line_v0: {
        bridge_line: "Особенность уже ясна. Today продолжает путь без спешки.",
        leads_to: "today",
      },
      profile_matrix_v0: {
        revealed_slots: {
          cultural_catalog: {
            color: "изумрудный",
            traditions: [{ label: "Китайский", value: "Лошадь" }],
            stones: [],
          },
        },
      },
    } as unknown as CoreProfile;
  }, []);

  const natalPreview = useMemo((): NatalChartPreview => {
    const signs = [
      "Aquarius",
      "Pisces",
      "Aries",
      "Taurus",
      "Gemini",
      "Cancer",
      "Leo",
      "Virgo",
      "Libra",
      "Scorpio",
      "Sagittarius",
      "Capricorn",
    ];
    return {
      positions: {
        sun: { sign: "Aquarius", house: 8, degree: 14, longitude: 314 },
        moon: { sign: "Libra", house: 4, degree: 22, longitude: 202 },
        mercury: { sign: "Aquarius", house: 8, degree: 3, longitude: 303 },
        venus: { sign: "Capricorn", house: 7, degree: 18, longitude: 288 },
        mars: { sign: "Scorpio", house: 5, degree: 9, longitude: 219 },
        jupiter: { sign: "Cancer", house: 1, degree: 2, longitude: 92 },
        saturn: { sign: "Pisces", house: 9, degree: 27, longitude: 357 },
      },
      houses: signs.map((sign, i) => ({
        house: i + 1,
        sign,
        degree: i * 2,
        cusp_longitude: (i * 30 + 90) % 360,
      })),
      ascendant: { sign: "Cancer", degree: 12, longitude: 102 },
      aspects: {
        callouts: [
          {
            aspect_id: "sun_trine_moon",
            bodies: "Sun-Moon",
            label: "Трин",
            keywords: ["гармония"],
            description: "Свет и чувство говорят на одном языке.",
            tension_level: "low",
            polarity: "harmonious",
            degrees_apart: 120,
            orb_delta: 2,
            strength: "medium",
          },
          {
            aspect_id: "mars_square_saturn",
            bodies: "Mars-Saturn",
            label: "Квадрат",
            keywords: ["трение"],
            description: "Импульс встречает форму.",
            tension_level: "high",
            polarity: "challenging",
            degrees_apart: 90,
            orb_delta: 3,
            strength: "strong",
          },
        ],
      },
    };
  }, []);

  const live = useMemo(
    () =>
      buildProfileV2LiveContext({
        coreProfile,
        cum: { confidence: { overall: 0.72 } } as never,
        thriveAreas: model.thriveAreas,
      }),
    [coreProfile, model.thriveAreas],
  );

  if (!isDev) {
    return (
      <main style={{ padding: "2rem", fontFamily: "system-ui" }}>
        <p>Preview available only outside production builds.</p>
      </main>
    );
  }

  return (
    <main
      data-theme={theme}
      data-testid="profile-journey-preview"
      style={{
        minHeight: "100vh",
        background: theme === "dark" ? "#121018" : "#f7f4ee",
        color: theme === "dark" ? "#f5f0e8" : "#2a2520",
        padding: "1.25rem clamp(1rem, 3vw, 2rem) 3rem",
      }}
    >
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "0.75rem",
          alignItems: "center",
          marginBottom: "1.25rem",
        }}
      >
        <strong style={{ fontFamily: "Georgia, serif", fontSize: "1.125rem" }}>
          Profile Journey visual QA
        </strong>
        <button type="button" onClick={() => setTheme((t) => (t === "light" ? "dark" : "light"))}>
          Theme: {theme}
        </button>
      </div>
      <ProfileV2SystemScreen
        model={model}
        live={live}
        coreProfile={coreProfile}
        onOpenBirthData={() => undefined}
        deepExpanded
        deep={{
          natalPreview,
          previewError: null,
          onReloadPreview: () => undefined,
          lifeMapSections: [],
          coreNumerology: coreProfile.numerology,
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
      />
    </main>
  );
}
