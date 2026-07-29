import { act, fireEvent, render, screen } from "@testing-library/react";
import { RitualTarotPickExperience } from "@/components/today/ritual/RitualTarotPickExperience";

const pic = {
  src: "/images/cards/tarot/web/back-576x960.webp",
  avifSrcSet: "",
  webpSrcSet: "/images/cards/tarot/web/back-576x960.webp 576w",
  width: 576,
  height: 960,
};

jest.mock("@/lib/tarotCardAssets", () => ({
  TAROT_CARD_PIXEL_WIDTH: 576,
  TAROT_CARD_PIXEL_HEIGHT: 960,
  tarotCardDisplayHeightPx: (w: number) => Math.round((w * 960) / 576),
  tarotCardBackPicture: () => pic,
  tarotCardFacePicture: () => ({
    ...pic,
    src: "/images/cards/tarot/web/faces/07-576x960.webp",
  }),
}));

jest.mock("@/lib/api", () => ({
  postJson: jest.fn(async () => []),
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
    expect(screen.getByTestId("ritual-tarot-pick-grid")).toHaveAttribute("data-pick-mode", "deck");

    act(() => {
      fireEvent.click(screen.getByTestId("ritual-tarot-deck-commit"));
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
