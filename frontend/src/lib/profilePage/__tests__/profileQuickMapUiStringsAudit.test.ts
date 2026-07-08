import { buildLifeMapSections } from "@/lib/profilePage/buildProfilePlanetaryData";
import { buildProfileFrameworkCards } from "@/lib/profilePage/buildProfileFrameworkCards";
import {
  buildProfileChartFrameworkInput,
  buildProfileQuickMapViewModel,
} from "@/lib/profilePage/buildProfileQuickMapData";
import { buildProfileV0ViewModel } from "@/lib/profilePage/buildProfileV0Data";
import { buildProfileLifeSpheresFromChart } from "@/lib/profilePage/profileLifeSpheres";
import { IGOR_SAGE_7_FIXTURE } from "@/lib/profilePage/fixtures/igorSage7ProfileFixture";
import {
  findLifeSphereHouseCopyOverlaps,
  findPortraitHouseCopyOverlaps,
  findQuickMapUiDuplicates,
} from "@/lib/profilePage/profileQuickMapUiStringsAudit";

describe("profileQuickMapUiStringsAudit", () => {
  it("has no overlapping Quick Map copy for Igor fixture", () => {
    const v0 = buildProfileV0ViewModel({
      core: IGOR_SAGE_7_FIXTURE,
      displayName: "Igor",
    });

    const frameworkCards = buildProfileFrameworkCards({
      sunLayer: { bullets: ["Системное мышление и независимость."] } as never,
      moonLayer: { bullets: ["В восстановлении нужна тишина."] } as never,
      risingLayer: { bullets: ["Сдержанный первый контакт."] } as never,
      risingSign: "Дева",
      risingHint: "Асцендент уточняется по времени рождения.",
      mcSign: "Близнецы",
      sunSignDisplay: "Водолей",
      lifePath: 7,
      lifePathBody: "Поиск смысла и глубины.",
      archetypeLabel: "Sage",
      archetypeBody: "Архетип мудреца.",
    });

    const quickMap = buildProfileQuickMapViewModel(
      v0,
      buildProfileChartFrameworkInput({
        sunSignDisplay: "Водолей",
        risingSign: "Дева",
        mcSign: "Близнецы",
        lifePath: 7,
        archetypeLabel: "Sage",
        chartCards: frameworkCards,
      }),
    );

    const duplicates = findQuickMapUiDuplicates(quickMap);
    if (duplicates.length) {
      // eslint-disable-next-line no-console
      console.log("Quick Map duplicates:", duplicates);
    }
    expect(duplicates).toEqual([]);
    expect(quickMap.pageLabel).toBe("Профиль");
    if (quickMap.identitySummary && quickMap.frameworkLead) {
      expect(quickMap.frameworkLead).not.toEqual(quickMap.identitySummary);
    }
  });

  it("keeps portrait spheres distinct from natal house summaries", () => {
    const v0 = buildProfileV0ViewModel({
      core: IGOR_SAGE_7_FIXTURE,
      displayName: "Igor",
    });
    const lifeMapSections = buildLifeMapSections(null);
    const overlaps = findPortraitHouseCopyOverlaps(v0, lifeMapSections);
    expect(overlaps).toEqual([]);
  });

  it("frames love and money spheres as portrait layers", () => {
    const v0 = buildProfileV0ViewModel({
      core: IGOR_SAGE_7_FIXTURE,
      displayName: "Igor",
    });
    expect(v0.love?.style).toMatch(/^В отношениях/i);
    expect(v0.money?.approach).toMatch(/^В реализации/i);
  });

  it("flags verbatim house copy in sphere how", () => {
    const spheres = [
      {
        id: "love",
        title: "Любовь",
        accent: "#000",
        how: "В отношениях дословная копия текста дома без перефразирования и смысловой рамки.",
        need: "",
        risk: "",
        turnsOn: "",
        turnsOff: "",
        helps: "",
        inSystem: "",
      },
    ];
    const lifeMapSections = [
      {
        house: 7,
        title: "7 дом",
        routeTitle: "7",
        href: "#",
        accent: "#000",
        summary: "дословная копия текста дома без перефразирования и смысловой рамки.",
      },
    ];
    expect(findLifeSphereHouseCopyOverlaps(spheres, lifeMapSections)).toHaveLength(1);
  });
});
