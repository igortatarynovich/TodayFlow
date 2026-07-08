import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import {
  profileV2SphereCardLine,
  profileV2SphereProgressPercent,
} from "@/lib/profilePage/profileV2SpherePresentation";

const sphere: ProfileLifeSphere = {
  id: "body",
  title: "Тело",
  accent: "#16a34a",
  how: "API-driven how line.",
  need: "Регулярный сон, еда без крайностей и честный сигнал усталости.",
  risk: "Risk template.",
  turnsOn: "Turns on template.",
  turnsOff: "Turns off.",
  helps: "Helps template.",
  inSystem: "Today.",
};

describe("profileV2SpherePresentation", () => {
  it("uses first clause of template need for card line", () => {
    expect(profileV2SphereCardLine(sphere)).toBe("Регулярный сон, еда без крайностей и честный сигнал усталости");
  });

  it("returns stable progress percent for sphere id", () => {
    expect(profileV2SphereProgressPercent("body", 68)).toBe(profileV2SphereProgressPercent("body", 68));
  });
});
