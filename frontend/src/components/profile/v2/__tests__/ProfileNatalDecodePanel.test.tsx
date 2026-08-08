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
      cta: "Открыть расшифровку натальной карты — целостная история из планет, углов и чисел.",
      note: "Собирается один раз. Повторно не генерируется, пока не изменятся данные карты.",
    });
    render(<ProfileNatalDecodePanel />);
    await waitFor(() => {
      expect(screen.getByTestId("profile-natal-decode-generate")).toBeInTheDocument();
    });
    expect(screen.getByTestId("profile-natal-decode-generate")).toHaveAttribute(
      "data-motion",
      "attention-breathe",
    );
    expect(screen.getByText(/один раз/i)).toBeInTheDocument();
  });

  it("hydrates ready decode from GET without generate CTA", async () => {
    getJson.mockResolvedValue({
      access: "ready",
      can_generate: false,
      status: "grounded",
      pattern_thesis: "Готовая история карты.",
      sections: [
        {
          id: "mind",
          title: "Ум",
          thesis: "Тезис",
          because_core: "Связь с ядром",
        },
      ],
      note: "Карта уже расшифрована — это готовая история, не кнопка «ещё раз».",
    });
    render(<ProfileNatalDecodePanel />);
    await waitFor(() => {
      expect(screen.getByTestId("profile-natal-decode-result")).toBeInTheDocument();
    });
    expect(screen.queryByTestId("profile-natal-decode-generate")).not.toBeInTheDocument();
    expect(screen.queryByTestId("profile-natal-decode-refresh")).not.toBeInTheDocument();
    expect(screen.getByText(/готовая история/i)).toBeInTheDocument();
  });

  it("plays pattern one-shot when grounded and stops CTA breathe", async () => {
    const user = userEvent.setup();
    getJson.mockResolvedValue({ access: "offer", can_generate: true, cta: "Открыть" });
    postJson.mockResolvedValue({
      status: "grounded",
      pattern_thesis: "Главный узор — стеллиум в рабочем секторе.",
      sections: [{ id: "mind", title: "Дело", thesis: "Тезис", because_core: "Ядро" }],
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
    expect(screen.queryByTestId("profile-natal-decode-refresh")).not.toBeInTheDocument();
  });

  it("does not re-fire pattern-sweep after profileMotionOnce is consumed", async () => {
    const user = userEvent.setup();
    getJson.mockResolvedValue({ access: "offer", can_generate: true, cta: "Открыть" });
    postJson.mockResolvedValue({
      status: "grounded",
      pattern_thesis: "Узор один.",
      sections: [{ id: "mind", title: "Дело", thesis: "Тезис", because_core: "Ядро" }],
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

    // Second mount: GET already ready — no generate CTA, pattern once already consumed.
    getJson.mockResolvedValue({
      access: "ready",
      can_generate: false,
      status: "grounded",
      pattern_thesis: "Узор один.",
      sections: [{ id: "mind", title: "Дело", thesis: "Тезис", because_core: "Ядро" }],
    });
    render(<ProfileNatalDecodePanel />);
    await waitFor(() => {
      expect(screen.getByTestId("profile-natal-decode-pattern")).toBeInTheDocument();
    });
    expect(screen.queryByTestId("profile-natal-decode-generate")).not.toBeInTheDocument();
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
