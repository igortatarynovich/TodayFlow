import { render, screen } from "@testing-library/react";
import { ProfileMyDaysBlock } from "@/components/profile/ProfileMyDaysBlock";
import { saveDayContinuity } from "@/lib/todayDayContinuity";

describe("ProfileMyDaysBlock", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("shows empty state and link to Today", async () => {
    render(<ProfileMyDaysBlock />);
    expect(await screen.findByTestId("profile-my-days")).toBeInTheDocument();
    expect(screen.getByText(/Заверши день в Today/)).toBeInTheDocument();
    expect(screen.getByTestId("profile-my-days-today-link")).toHaveAttribute("href", "/today");
  });

  it("lists up to three closed days with focus and outcome", async () => {
    saveDayContinuity({
      dateISO: "2026-06-22",
      mainFocus: "Разговор с командой",
      outcome: "partial",
      closedAt: "2026-06-22T20:00:00.000Z",
    });
    saveDayContinuity({
      dateISO: "2026-06-21",
      mainFocus: "Один шаг по проекту",
      outcome: "done",
      closedAt: "2026-06-21T20:00:00.000Z",
    });

    render(<ProfileMyDaysBlock />);

    expect(await screen.findByTestId("profile-my-days-row-2026-06-22")).toBeInTheDocument();
    expect(screen.getByText("Разговор с командой")).toBeInTheDocument();
    expect(screen.getByText("Частично")).toBeInTheDocument();
    expect(screen.getByText("Сделал")).toBeInTheDocument();
  });
});
