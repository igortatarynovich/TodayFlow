import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ProfileNatalDecodePanel } from "@/components/profile/v2/ProfileNatalDecodePanel";
import { resetProfileMotionOnceForTests } from "@/lib/profile/profileMotionOnce";

const getJson = jest.fn();
const postJson = jest.fn();

jest.mock("@/lib/api", () => ({
  getJson: (...args: unknown[]) => getJson(...args),
  postJson: (...args: unknown[]) => postJson(...args),
}));

describe("ProfileNatalDecodePanel", () => {
  beforeEach(() => {
    getJson.mockReset();
    postJson.mockReset();
    resetProfileMotionOnceForTests();
  });

  it("shows offer CTA when can_generate", async () => {
    getJson.mockResolvedValue({
      access: "offer",
      can_generate: true,
      cta: "Открыть расшифровку натальной карты — как структура карты объясняет твоё ядро.",
      note: "Генерируется только по явному запросу. Не второй портрет.",
    });
    render(<ProfileNatalDecodePanel />);
    await waitFor(() => {
      expect(screen.getByTestId("profile-natal-decode-generate")).toBeInTheDocument();
    });
    expect(screen.getByTestId("profile-natal-decode-generate")).toHaveAttribute(
      "data-motion",
      "attention-breathe",
    );
    expect(screen.getByText(/Не второй портрет/i)).toBeInTheDocument();
  });

  it("plays pattern one-shot when grounded and stops CTA breathe", async () => {
    const user = userEvent.setup();
    getJson.mockResolvedValue({ access: "offer", can_generate: true, cta: "Открыть" });
    postJson.mockResolvedValue({
      status: "grounded",
      pattern_thesis: "Главный узор — стеллиум в рабочем секторе.",
      sections: [{ id: "work", title: "Дело", thesis: "Тезис" }],
    });
    render(<ProfileNatalDecodePanel />);
    await waitFor(() => {
      expect(screen.getByTestId("profile-natal-decode-generate")).toBeInTheDocument();
    });
    await user.click(screen.getByTestId("profile-natal-decode-generate"));
    await waitFor(() => {
      expect(screen.getByTestId("profile-natal-decode-result")).toBeInTheDocument();
    });
    expect(screen.getByTestId("profile-natal-decode-pattern")).toHaveAttribute(
      "data-motion",
      "pattern-sweep",
    );
    expect(screen.queryByTestId("profile-natal-decode-generate")).not.toBeInTheDocument();
  });

  it("does not re-fire pattern-sweep after profileMotionOnce is consumed", async () => {
    const user = userEvent.setup();
    getJson.mockResolvedValue({ access: "offer", can_generate: true, cta: "Открыть" });
    postJson.mockResolvedValue({
      status: "grounded",
      pattern_thesis: "Узор один.",
      sections: [{ id: "work", title: "Дело", thesis: "Тезис" }],
    });
    const { unmount } = render(<ProfileNatalDecodePanel />);
    await waitFor(() => {
      expect(screen.getByTestId("profile-natal-decode-generate")).toBeInTheDocument();
    });
    await user.click(screen.getByTestId("profile-natal-decode-generate"));
    await waitFor(() => {
      expect(screen.getByTestId("profile-natal-decode-pattern")).toHaveAttribute(
        "data-motion",
        "pattern-sweep",
      );
    });
    unmount();

    // Second mount with already-grounded result path: offer still can_generate but
    // generate again after remount — once key stays consumed.
    render(<ProfileNatalDecodePanel />);
    await waitFor(() => {
      expect(screen.getByTestId("profile-natal-decode-generate")).toBeInTheDocument();
    });
    await user.click(screen.getByTestId("profile-natal-decode-generate"));
    await waitFor(() => {
      expect(screen.getByTestId("profile-natal-decode-pattern")).toBeInTheDocument();
    });
    expect(screen.getByTestId("profile-natal-decode-pattern")).not.toHaveAttribute(
      "data-motion",
      "pattern-sweep",
    );
  });

  it("shows blocked copy when cannot generate", async () => {
    getJson.mockResolvedValue({
      access: "blocked",
      can_generate: false,
      cta: "Сначала нужен устойчивый портрет характера.",
      reason: "identity_core_required",
    });
    render(<ProfileNatalDecodePanel />);
    await waitFor(() => {
      expect(screen.getByTestId("profile-natal-decode-blocked")).toBeInTheDocument();
    });
    expect(screen.queryByTestId("profile-natal-decode-generate")).not.toBeInTheDocument();
  });
});
