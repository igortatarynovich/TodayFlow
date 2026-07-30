import { fireEvent, render, screen, act } from "@testing-library/react";
import { PracticeLiveSession } from "@/components/practices/session/PracticeLiveSession";
import {
  PRACTICE_SESSION_DRAFT_KEY,
  readPracticeSessionDraft,
} from "@/lib/practicesPage/practiceSessionDraft";

describe("PracticeLiveSession", () => {
  beforeEach(() => {
    localStorage.clear();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
    localStorage.clear();
  });

  it("runs timer, opens check-in, and saves to today", async () => {
    const onSave = jest.fn().mockResolvedValue(undefined);
    const onClose = jest.fn();

    render(
      <PracticeLiveSession
        locale="ru"
        practiceId="p1"
        title="Дыхание"
        instruction="Медленный вдох"
        durationMinutes={1}
        isAuthenticated
        onClose={onClose}
        onSaveToToday={onSave}
      />,
    );

    expect(screen.getByTestId("practice-live-session")).toHaveAttribute("data-phase", "running");
    expect(screen.getByTestId("practice-session-timer")).toHaveTextContent("01:00");

    fireEvent.click(screen.getByTestId("practice-session-sound"));
    expect(screen.getByTestId("practice-music-layer")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Без звука" }));

    fireEvent.click(screen.getByTestId("practice-session-pause"));
    act(() => {
      jest.advanceTimersByTime(5000);
    });
    // paused — elapsed stays
    expect(screen.getByTestId("practice-session-timer")).toHaveTextContent("01:00");

    fireEvent.click(screen.getByTestId("practice-session-pause"));
    act(() => {
      jest.advanceTimersByTime(2000);
    });
    expect(screen.getByTestId("practice-session-timer")).toHaveTextContent("00:58");

    const draft = readPracticeSessionDraft();
    expect(draft?.practiceId).toBe("p1");
    expect(draft?.elapsedSeconds).toBeGreaterThanOrEqual(2);

    fireEvent.click(screen.getByRole("button", { name: "Завершить" }));
    expect(screen.getByTestId("practice-session-checkin")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Лучше" }));
    await act(async () => {
      fireEvent.click(screen.getByTestId("practice-session-save"));
    });

    expect(onSave).toHaveBeenCalledWith(
      expect.objectContaining({ stateAfter: "better", elapsedSeconds: expect.any(Number) }),
    );
    expect(screen.getByTestId("practice-session-saved")).toBeInTheDocument();
    expect(localStorage.getItem(PRACTICE_SESSION_DRAFT_KEY)).toBeNull();
  });
});
