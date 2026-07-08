import { render, screen } from "@testing-library/react";
import { ProfileMapsPreviewBlock } from "@/components/profile/ProfileMapsPreviewBlock";
import { saveDayContinuity } from "@/lib/todayDayContinuity";

describe("ProfileMapsPreviewBlock", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("shows empty ghost strip before first closed day", async () => {
    render(<ProfileMapsPreviewBlock />);
    expect(await screen.findByTestId("profile-maps-preview")).toBeInTheDocument();
    expect(screen.getByText(/первая точка/i)).toBeInTheDocument();
  });

  it("renders explore card grid with hub and map links", async () => {
    render(<ProfileMapsPreviewBlock />);
    const grid = await screen.findByTestId("profile-maps-explore-grid");
    expect(grid).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Все карты/i })).toHaveAttribute("href", "/tracking/progress");
    expect(screen.getByRole("link", { name: /Настроение/i })).toHaveAttribute("href", "/maps/mood");
    expect(screen.getByRole("link", { name: /Энергия/i })).toHaveAttribute("href", "/maps/energy");
    expect(screen.getByRole("link", { name: /Обещания/i })).toHaveAttribute("href", "/maps/promise");
    expect(screen.getByRole("link", { name: /Привычки/i })).toHaveAttribute("href", "/habits");
    expect(screen.getByRole("link", { name: /^Ритм/i })).toHaveAttribute("href", "/tracking/calendar");
  });

  it("renders seed dots after evening closes", async () => {
    saveDayContinuity({
      dateISO: "2026-06-22",
      mainFocus: "Отдых",
      outcome: "done",
      closedAt: "2026-06-22T20:00:00.000Z",
    });

    render(<ProfileMapsPreviewBlock />);

    expect(await screen.findByTestId("profile-maps-seed-2026-06-22")).toBeInTheDocument();
    expect(screen.getByText(/Один закрытый день/i)).toBeInTheDocument();
  });
});
