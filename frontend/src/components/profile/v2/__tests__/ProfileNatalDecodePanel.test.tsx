import { render, screen, waitFor } from "@testing-library/react";
import { ProfileNatalDecodePanel } from "@/components/profile/v2/ProfileNatalDecodePanel";

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
    expect(screen.getByText(/Не второй портрет/i)).toBeInTheDocument();
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
