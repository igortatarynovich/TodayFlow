/**
 * @jest-environment jsdom
 */
import { render, screen, waitFor } from "@testing-library/react";
import { TodayGlanceAct } from "@/components/today/composition/TodayGlanceAct";

jest.mock("@/lib/todayDayFacts", () => ({
  fetchDayFacts: jest.fn(async () => ({
    glance_timeline: [],
    is_fallback: false,
    degraded: false,
  })),
}));

describe("TodayGlanceAct story frame", () => {
  it("renders typography-first slots without requiring five glass panels", async () => {
    render(
      <TodayGlanceAct
        dateISO="2026-08-05"
        dayTexture="День спокойного отпускания"
        thesis={null}
        energyLine="Спокойная убывающая энергия"
        energyCause="фаза Луны"
        dailyFocus={{
          dailyFocusId: "focus-1",
          title: "Мягкий фокус",
          prioritize: "одно важное дело",
          avoid: "спор ради спора",
        }}
        teasers={[
          {
            id: "symbols",
            label: "Символы",
            hook: "Карта и число",
          },
        ]}
      />,
    );

    expect(screen.getByTestId("today-glance-today")).toHaveTextContent("Сегодня");
    expect(screen.getByTestId("today-glance-thesis")).toHaveTextContent("День спокойного отпускания");
    expect(screen.getByTestId("today-glance-energy-text")).toHaveTextContent("Спокойная убывающая энергия");
    expect(screen.getByTestId("today-glance-focus-title")).toHaveTextContent("Мягкий фокус");
    expect(screen.getByTestId("today-glance-focus-prioritize")).toBeInTheDocument();
    expect(screen.getByTestId("today-glance-focus-avoid")).toBeInTheDocument();
    expect(screen.getByTestId("today-glance-teaser-symbols")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByTestId("today-slot-glance-nearest")).toBeInTheDocument();
    });

    // Theme + energy are plain frames (testids preserved); only teaser uses DsCard glass.
    expect(screen.getByTestId("today-glance-glass").tagName.toLowerCase()).toBe("div");
    expect(screen.getByTestId("today-glance-energy").tagName.toLowerCase()).toBe("div");
  });
});
