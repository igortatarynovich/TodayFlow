import { fireEvent, render, screen } from "@testing-library/react";
import { FlippableCard } from "@/components/tarot/FlippableCard";
import type { TarotCard } from "@/lib/types";

const card = {
  id: 0,
  name: "Шут",
  upright: "Начало",
  reversed: "Хаос",
  keywords: ["старт"],
  correspondences: { element: "air" },
} as TarotCard;

describe("FlippableCard", () => {
  beforeEach(() => {
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: jest.fn().mockImplementation((query: string) => ({
        matches: query.includes("prefers-reduced-motion"),
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });
  });

  it("uses MotionFlip and reveals face on click (reduced motion)", () => {
    const onFlip = jest.fn();
    render(<FlippableCard card={card} orientation="upright" onFlip={onFlip} />);

    expect(screen.getByTestId("tarot-flippable-motion-flip")).toHaveAttribute("data-flipped", "false");
    expect(screen.getByText("Нажми, чтобы открыть")).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText("Открыть карту"));

    expect(screen.getByTestId("tarot-flippable-motion-flip")).toHaveAttribute("data-flipped", "true");
    expect(onFlip).toHaveBeenCalledTimes(1);
  });
});
