"use client";

import { ProfileExpandableSection } from "@/components/profile/ProfileExpandableSection";
import { ProfileSurfaceTile } from "@/components/profile/ProfileSurface";
import type { CombinedPlanetaryProfile } from "@/components/profile/profilePanelTypes";
import type { LifePathEntry } from "@/lib/zodiacKnowledge";

export type ProfilePatternItem = {
  title: string;
  description: string;
  lifeSign: string;
  risk: string;
  helps: string;
  confidence: string;
  sources: string;
};

function buildPatterns(
  combined: CombinedPlanetaryProfile | null,
  lifePath: LifePathEntry | null | undefined,
): ProfilePatternItem[] {
  const out: ProfilePatternItem[] = [];
  if (combined?.explanation?.trim()) {
    out.push({
      title: "Как ты обычно собираешь картину",
      description: combined.explanation.trim(),
      lifeSign: combined.manifestation?.trim() || "Проявится в повторяющихся сценариях дня и в темах, к которым ты возвращаешься.",
      risk: combined.risk?.trim() || combined.tension?.trim() || "Риск — застревать в объяснении вместо одного следующего шага.",
      helps: combined.strength?.trim() || "Опирайся на то, что уже даёт ясность без перегруза.",
      confidence: combined.explanation.length > 220 ? "средняя" : "базовая",
      sources: "карта рождения",
    });
  }
  if (combined?.tension?.trim()) {
    out.push({
      title: "Как ты реагируешь на стресс",
      description: combined.tension.trim(),
      lifeSign: combined.constraintLine?.trim() || "Часто видно в теле, сне и в том, как ты срываешь договорённости с собой.",
      risk: combined.magicLine?.trim() || "Риск уходить в туман, откладывание или жёсткий контроль.",
      helps: combined.growthLine?.trim() || "Мягкий режим и один понятный якорь дня снижают накал.",
      confidence: "средняя",
      sources: "карта рождения",
    });
  }
  if (combined?.firstContact?.trim() || combined?.expressionLine?.trim()) {
    out.push({
      title: "Как ты входишь в отношения и контакт",
      description: [combined.firstContact, combined.expressionLine].filter(Boolean).join(" "),
      lifeSign: "Заметно в первых фразах, в дистанции и в том, как быстро ты доверяешь.",
      risk: combined.rebellionLine?.trim() || "Риск — резко обрывать или, наоборот, терять границы ради близости.",
      helps: combined.strength?.trim() || "Прямой, короткий контакт и ясные ожидания.",
      confidence: "средняя",
      sources: "карта рождения",
    });
  }
  if (lifePath?.pattern?.trim()) {
    out.push({
      title: "Как ты принимаешь решения",
      description: lifePath.pattern.trim(),
      lifeSign: lifePath.manifestation?.[0]?.trim() || "Проявляется в том, что ты откладываешь или, наоборот, рвёшься действовать.",
      risk: lifePath.watchouts?.[0]?.trim() || "Риск действовать из давления, когда внутри ещё нет ясности.",
      helps: lifePath.growth?.trim() || "Заранее выбрать минимальный следующий шаг.",
      confidence: "средняя",
      sources: "карта рождения · число пути",
    });
  }
  if (combined?.mind?.trim()) {
    out.push({
      title: "Как с тобой лучше говорить",
      description: combined.mind.trim(),
      lifeSign: "Слышно в переписке и в том, когда ты «включаешься» на диалог.",
      risk: "Длинные абстрактные рассуждения без опоры на факты могут выключать.",
      helps: "Короткие формулировки, один вопрос за раз, пространство на паузу.",
      confidence: "базовая",
      sources: "карта рождения",
    });
  }
  if (out.length === 0) {
    out.push({
      title: "Паттерны появятся из карты и поведения",
      description:
        "Сейчас система может вывести устойчивые сценарии, когда в ответе карты есть связный срез планет и аспектов. Чем больше ответов в Today и вечерних фиксаций, тем больше строк здесь опирается на поведение, а не только на рождение.",
      lifeSign: "Пока ориентируйся на раздел «Карта рождения» и «Живой слой».",
      risk: "—",
      helps: "Отмечай день и закрывай вечер — так быстрее появятся повторяемые линии.",
      confidence: "низкая",
      sources: "ожидает данных",
    });
  }
  return out.slice(0, 9);
}

export function ProfilePatternsSection({
  combinedPlanetaryProfile,
  lifePathLayer,
}: {
  combinedPlanetaryProfile: CombinedPlanetaryProfile | null;
  lifePathLayer: LifePathEntry | null | undefined;
}) {
  const items = buildPatterns(combinedPlanetaryProfile, lifePathLayer);
  return (
    <div style={{ display: "grid", gap: "0.85rem" }}>
      <ProfileExpandableSection
        id="profile-patterns-intro"
        title="Паттерны"
        subtitle="Это не натальная карта. Здесь — синтез того, как ты обычно действуешь, реагируешь и восстанавливаешься."
        defaultOpen
      >
        <div style={{ display: "grid", gap: "0.75rem" }}>
          {items.map((item) => (
            <ProfileSurfaceTile key={item.title}>
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
                {item.title}
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.75 }}>
                {item.description}
              </p>
              <div style={{ marginTop: "0.65rem", display: "grid", gap: "0.45rem", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}>
                <div>
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", fontWeight: 700 }}>
                    Как видно в жизни
                  </p>
                  <p className="orbit-body-xs" style={{ margin: "0.25rem 0 0", color: "#475569", lineHeight: 1.65 }}>
                    {item.lifeSign}
                  </p>
                </div>
                <div>
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", fontWeight: 700 }}>
                    Риск
                  </p>
                  <p className="orbit-body-xs" style={{ margin: "0.25rem 0 0", color: "#475569", lineHeight: 1.65 }}>
                    {item.risk}
                  </p>
                </div>
                <div>
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", fontWeight: 700 }}>
                    Что помогает
                  </p>
                  <p className="orbit-body-xs" style={{ margin: "0.25rem 0 0", color: "#475569", lineHeight: 1.65 }}>
                    {item.helps}
                  </p>
                </div>
              </div>
              <p className="orbit-body-xs" style={{ margin: "0.65rem 0 0", color: "#94a3b8" }}>
                Уверенность: {item.confidence}. Источники: {item.sources}.
              </p>
            </ProfileSurfaceTile>
          ))}
        </div>
      </ProfileExpandableSection>
    </div>
  );
}
