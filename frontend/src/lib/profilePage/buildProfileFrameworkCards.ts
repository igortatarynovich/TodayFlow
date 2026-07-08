import type { ProfileFrameworkCard } from "./buildProfileQuickMapData";
import type { PlanetInSignEntry } from "@/lib/zodiacKnowledge";
import { layerSignLabel } from "./buildProfilePlanetaryData";

function pillarSentence(layer: PlanetInSignEntry | null | undefined, fallback: string) {
  const line = layer?.bullets?.[0]?.trim();
  return line || fallback;
}

function signAnchor(prefix: string, signLabel: string | null | undefined): string | null {
  if (!signLabel?.trim()) return null;
  return `${prefix} ${signLabel.trim()}`;
}

export function buildProfileFrameworkCards(input: {
  sunLayer: PlanetInSignEntry | null | undefined;
  moonLayer: PlanetInSignEntry | null | undefined;
  risingLayer: PlanetInSignEntry | null | undefined;
  risingSign: string | null;
  risingHint: string;
  mcSign: string | null;
  sunSignDisplay: string | null;
  lifePath: number | null;
  lifePathBody: string | null;
  archetypeLabel: string;
  archetypeBody: string | null;
}): ProfileFrameworkCard[] {
  const sunSign = input.sunSignDisplay ?? layerSignLabel(input.sunLayer, "");
  const risingSign = input.risingSign ?? layerSignLabel(input.risingLayer, "");

  const cards: ProfileFrameworkCard[] = [
    {
      id: "sun",
      title: "Солнце",
      anchor: signAnchor("в", sunSign || null),
      body: pillarSentence(input.sunLayer, "Солнце показывает, как ты проявляешь себя в мире."),
    },
    {
      id: "rising",
      title: "Асцендент",
      anchor: signAnchor("в", risingSign || null),
      body: pillarSentence(input.risingLayer, input.risingHint),
    },
    {
      id: "moon",
      title: "Луна",
      anchor: signAnchor("в", layerSignLabel(input.moonLayer, "") || null),
      body: pillarSentence(input.moonLayer, "Луна описывает, как ты чувствуешь и восстанавливаешься."),
    },
    {
      id: "mc",
      title: "MC",
      anchor: signAnchor("в", input.mcSign),
      body: input.mcSign
        ? "MC показывает, как ты реализуешь себя в карьере и публичной роли."
        : "MC уточняется по времени рождения — это линия достижений и видимого пути.",
    },
    {
      id: "archetype",
      title: "Архетип",
      anchor: input.archetypeLabel,
      body: input.archetypeBody?.trim() || "Архетип собирает повторяющийся сценарий личности.",
    },
  ];

  if (input.lifePath != null) {
    cards.push({
      id: "life_path",
      title: "Число пути",
      anchor: String(input.lifePath),
      body: input.lifePathBody?.trim() || "Число пути задаёт долгий ритм развития и главную тему.",
    });
  }

  return cards.filter((card) => card.body.trim());
}
