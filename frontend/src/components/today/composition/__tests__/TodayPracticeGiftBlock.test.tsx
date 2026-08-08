import { render, screen, fireEvent } from "@testing-library/react";
import { TodayPracticeGiftBlock } from "@/components/today/composition/TodayPracticeGiftBlock";

jest.mock("@/lib/todayStoryFrameArt", () => ({
  resolveTodayStoryFrameArt: () => "/images/praktiki_banner.png",
}));

describe("TodayPracticeGiftBlock", () => {
  it("frames practice as a gift with start CTA", () => {
    const onPracticeAction = jest.fn();
    render(
      <TodayPracticeGiftBlock
        title="5 минут тишины"
        detail="Сядь удобно и подыши."
        duration="5 мин"
        practiceStarted={false}
        practiceCompleted={false}
        onPracticeAction={onPracticeAction}
      />,
    );
    expect(screen.getByTestId("today-zone-practice-gift")).toBeInTheDocument();
    expect(screen.getByText(/Практика дня · подарок/i)).toBeInTheDocument();
    expect(screen.getByText("5 минут тишины")).toBeInTheDocument();
    fireEvent.click(screen.getByTestId("today-tool-practice"));
    expect(onPracticeAction).toHaveBeenCalled();
    expect(screen.getByTestId("today-tool-practice")).toHaveTextContent(/Начать практику · 5 мин/);
  });

  it("shows started confirmation then complete CTA", () => {
    render(
      <TodayPracticeGiftBlock
        title="5 минут тишины"
        practiceStarted
        practiceCompleted={false}
        onPracticeAction={jest.fn()}
      />,
    );
    expect(screen.getByTestId("today-practice-gift-started")).toBeInTheDocument();
    expect(screen.getByTestId("today-tool-practice")).toHaveTextContent(/Завершить практику/);
  });
});
