import { render, screen } from "@testing-library/react";
import { ProfilePortraitSection } from "@/components/profile/ProfilePortraitSection";

describe("ProfilePortraitSection", () => {
  it("renders canon portrait section band and children", () => {
    render(
      <ProfilePortraitSection variant="quickMap">
        <p>Hero content</p>
      </ProfilePortraitSection>,
    );
    expect(screen.getByTestId("profile-portrait-section")).toBeInTheDocument();
    expect(screen.getByText("Кто я")).toBeInTheDocument();
    expect(screen.getByText(/почти не меняется/i)).toBeInTheDocument();
    expect(screen.getByText("Hero content")).toBeInTheDocument();
  });
});
