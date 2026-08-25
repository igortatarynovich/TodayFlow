import { fireEvent, render, screen } from "@testing-library/react";
import { PracticesStateCycleScreen } from "@/components/practices/stateCycle/PracticesStateCycleScreen";

describe("PracticesStateCycleScreen", () => {
  it("renders need chips in canon order and recommended card", async () => {
    const onNeedChange = jest.fn();
    const onFormatChange = jest.fn();

    render(
      <PracticesStateCycleScreen
        locale="ru"
        activeNeed="calm"
        onNeedChange={onNeedChange}
        activeFormat={null}
        onFormatChange={onFormatChange}
        recommended={{
          id: "p1",
          href: "/practices/p1",
          title: "Объёмное воображение",
          description: "Мягкая практика для внутреннего видения.",
          minutes: 12,
          formatId: "visualization",
        }}
        momentCards={[
          {
            id: "p2",
            href: "/practices/p2",
            title: "Снять напряжение",
            description: "",
            minutes: 7,
            formatId: "breath",
          },
        ]}
        practiceOfDay={{
          id: "p3",
          href: "/practices/p3",
          title: "Дыхание 4–7–8",
          description: "Успокаивает нервную систему.",
          minutes: 4,
          formatId: "breath",
        }}
        practiceOfDaySource="personalized"
      />,
    );

    expect(screen.getByTestId("practices-state-cycle")).toBeInTheDocument();
    const needs = screen.getByTestId("practices-need-chips");
    expect(needs.textContent).toMatch(
      /Успокоиться.*Собраться.*Восстановиться.*Почувствовать тело.*Понять себя.*Уснуть/,
    );
    expect(screen.getByTestId("practices-recommended")).toHaveTextContent("Объёмное воображение");
    expect(screen.getByText("Начать")).toBeInTheDocument();
    expect(screen.getByTestId("practices-moment")).toHaveTextContent("Снять напряжение");
    expect(screen.getByTestId("practices-of-day")).toHaveTextContent("Дыхание 4–7–8");
    expect(screen.queryByTestId("practices-continue")).not.toBeInTheDocument();
    expect(screen.queryByTestId("practices-my")).not.toBeInTheDocument();
    expect(await screen.findByTestId("practices-music-hub")).toHaveTextContent("Музыкальное сопровождение");
    expect(screen.getByTestId("practices-music-hub")).toHaveTextContent("С голосом");

    fireEvent.click(screen.getByRole("button", { name: "Понять себя" }));
    expect(onNeedChange).toHaveBeenCalledWith("understand");

    fireEvent.click(screen.getByRole("button", { name: /Йога/ }));
    expect(onFormatChange).toHaveBeenCalledWith("yoga");
  });

  it("shows continue and my library only when data present", () => {
    render(
      <PracticesStateCycleScreen
        locale="ru"
        activeNeed="sleep"
        onNeedChange={() => {}}
        activeFormat={null}
        onFormatChange={() => {}}
        recommended={null}
        continueSession={{
          href: "/practices/p9?run=1",
          title: "Вечернее отпускание",
          minutesDone: 4,
          minutesTotal: 7,
        }}
        momentCards={[]}
        practiceOfDay={null}
        myItems={[{ id: "p9", href: "/practices/p9", title: "Вечернее отпускание" }]}
      />,
    );

    expect(screen.getByTestId("practices-continue")).toHaveAttribute("href", "/practices/p9?run=1");
    expect(screen.getByTestId("practices-continue")).toHaveTextContent("Вечернее отпускание");
    expect(screen.getByTestId("practices-my")).toHaveTextContent("Мои практики");
  });

  it("paints hub chrome immediately without catalog cards", () => {
    render(
      <PracticesStateCycleScreen
        locale="ru"
        activeNeed="calm"
        onNeedChange={() => {}}
        activeFormat={null}
        onFormatChange={() => {}}
        recommended={null}
        momentCards={[]}
        practiceOfDay={null}
      />,
    );

    expect(screen.getByTestId("practices-state-cycle")).toBeInTheDocument();
    expect(screen.getByTestId("practices-need-chips")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Практики" })).toBeInTheDocument();
    expect(screen.queryByTestId("practices-recommended")).not.toBeInTheDocument();
  });
});
