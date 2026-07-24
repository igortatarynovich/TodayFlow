import { act, fireEvent, render, screen } from "@testing-library/react";
import { RitualTarotPickExperience } from "@/components/today/ritual/RitualTarotPickExperience";

jest.mock("@/lib/tarotCardAssets", () => ({
  TAROT_CARD_PIXEL_WIDTH: 192,
  TAROT_CARD_PIXEL_HEIGHT: 320,
  tarotCardBackSrc: () => "/images/cards/tarot/back.png",
  tarotCardFaceSrc: (id: number) => `/images/cards/tarot/${id}.png`,
}));

describe("RitualTarotPickExperience · MotionFlip", () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it("plays MotionFlip on reveal after pick (not resume)", () => {
    const onCommitMain = jest.fn();
    const onContinue = jest.fn();

    render(
      <RitualTarotPickExperience
        anchorCardId={7}
        resumeCommittedId={null}
        cardTitleRu="Отшельник"
        tagLabels={["фокус"]}
        onCommitMain={onCommitMain}
        onContinue={onContinue}
        reduceMotion
        startAtGrid
        allowSkipAnimation={false}
      />,
    );

    expect(screen.getByTestId("ritual-tarot-pick-grid")).toBeInTheDocument();
    const cards = screen.getAllByRole("button");

    act(() => {
      fireEvent.click(cards[0]!);
      jest.runOnlyPendingTimers();
    });

    expect(screen.getByTestId("ritual-tarot-motion-flip")).toBeInTheDocument();
    expect(onCommitMain).toHaveBeenCalledWith(7);
    expect(screen.getByText("Отшельник")).toBeInTheDocument();
  });

  it("shows face immediately when mounting already revealed", () => {
    render(
      <RitualTarotPickExperience
        anchorCardId={7}
        resumeCommittedId={7}
        cardTitleRu="Отшельник"
        tagLabels={[]}
        onCommitMain={jest.fn()}
        onContinue={jest.fn()}
        reduceMotion
      />,
    );

    expect(screen.getByTestId("ritual-tarot-motion-flip")).toHaveAttribute("data-flipped", "true");
    expect(screen.queryByTestId("ritual-tarot-pick-grid")).not.toBeInTheDocument();
  });
});
