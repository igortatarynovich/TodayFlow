import { render, screen } from "@testing-library/react";
import { ProfileLivingMapsSection } from "@/components/profile/ProfileLivingMapsSection";

describe("ProfileLivingMapsSection", () => {
  it("renders canon section band and maps preview", async () => {
    render(<ProfileLivingMapsSection variant="quickMap" />);
    expect(screen.getByTestId("profile-living-maps-section")).toBeInTheDocument();
    expect(screen.getByText("Как меняется моя жизнь")).toBeInTheDocument();
    expect(screen.getByText(/без ручной статистики/i)).toBeInTheDocument();
    expect(await screen.findByTestId("profile-maps-preview")).toBeInTheDocument();
    // Editorial DS pattern: section titles are styled <p>, not heading elements.
    expect(screen.getByText("Мои карты")).toBeInTheDocument();
  });
});
