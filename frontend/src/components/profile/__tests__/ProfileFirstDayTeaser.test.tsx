import { render, screen } from "@testing-library/react";
import { ProfileFirstDayTeaser } from "@/components/profile/ProfileFirstDayTeaser";
import type { ProfileV0ViewModel } from "@/lib/profilePage/buildProfileV0Data";

const baseModel: ProfileV0ViewModel = {
  header: {
    displayName: "Victoria",
    archetypeLabel: "Sage",
    sunSignDisplay: "Солнце в Водолее",
    lifePath: 7,
    poeticCaption: null,
    tagline: "Системное мышление",
    intro: "Ты лучше всего раскрываешься там, где есть понимание смысла.",
    qualities: [{ title: "Ясность", subtitle: "структура" }],
  },
  who: null,
  numbers: null,
  socialMirror: null,
  love: null,
  money: null,
  action: null,
  deepDiveHref: "/profile/chart",
};

describe("ProfileFirstDayTeaser", () => {
  it("renders portrait band, living maps section, and portal CTA", async () => {
    render(
      <ProfileFirstDayTeaser
        model={baseModel}
        intentTheme="clarity"
        realityState="stable"
        onOpenFullPortrait={() => {}}
      />,
    );

    expect(screen.getByTestId("profile-first-day-teaser")).toBeInTheDocument();
    expect(screen.getByTestId("profile-portrait-section")).toBeInTheDocument();
    expect(screen.getByText("Кто я")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Sage" })).toBeInTheDocument();
    expect(screen.queryByText("Victoria")).not.toBeInTheDocument();
    expect(screen.getByTestId("profile-living-maps-section")).toBeInTheDocument();
    expect(await screen.findByTestId("profile-maps-preview")).toBeInTheDocument();
    expect(screen.getByTestId("profile-first-day-portal")).toBeInTheDocument();
    expect(screen.getByText("Следующий уровень")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Вернуться в Today" })).toHaveAttribute("href", "/today");
  });
});
