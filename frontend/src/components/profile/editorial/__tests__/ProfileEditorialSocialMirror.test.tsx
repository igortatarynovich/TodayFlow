import { render, screen } from "@testing-library/react";
import { ProfileEditorialSocialMirror } from "@/components/profile/editorial/ProfileEditorialSocialMirror";
import type { ProfileV0SocialMirrorCard } from "@/lib/profilePage/buildProfileV0SphereCards";

const mirror: ProfileV0SocialMirrorCard = {
  lead: "Люди часто воспринимают тебя как спокойного аналитика.",
  observations: ["Сдержанный", "Внимательный"],
  runtimeGenerated: false,
  expand: {
    firstImpression: "Первое впечатление — собранность.",
    broadcast: null,
    blindSpot: null,
  },
};

describe("ProfileEditorialSocialMirror", () => {
  it("renders social mirror without name entity", () => {
    render(<ProfileEditorialSocialMirror mirror={mirror} />);
    expect(screen.getByText(mirror.lead)).toBeInTheDocument();
    expect(screen.getByText("Сдержанный")).toBeInTheDocument();
    expect(screen.queryByText("Имя")).not.toBeInTheDocument();
    expect(screen.queryByText("Подробнее об имени")).not.toBeInTheDocument();
  });
});
