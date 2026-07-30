import { render, screen } from "@testing-library/react";
import { GuestProductPitch } from "../GuestProductPitch";
import { GUEST_TODAY_PITCH, GUEST_PROFILE_PITCH } from "../guestProductPitches";

describe("GuestProductPitch", () => {
  it("renders Today pitch content for crawlers", () => {
    const pitch = GUEST_TODAY_PITCH;
    render(
      <GuestProductPitch
        eyebrow={pitch.eyebrow}
        title={pitch.title}
        lead={pitch.lead}
        parts={pitch.parts}
        needs={pitch.needs}
        primaryHref={pitch.ctaPrimaryHref}
        primaryLabel={pitch.ctaPrimary}
        secondaryLabel={pitch.ctaSecondary}
      />,
    );
    expect(screen.getByRole("heading", { name: pitch.title })).toBeInTheDocument();
    expect(screen.getByText(/не общий гороскоп/)).toBeInTheDocument();
    expect(screen.getByText("Тема")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: pitch.ctaPrimary })).toHaveAttribute(
      "href",
      pitch.ctaPrimaryHref,
    );
  });

  it("renders Profile pitch without production placeholder language", () => {
    const pitch = GUEST_PROFILE_PITCH;
    render(
      <GuestProductPitch
        eyebrow={pitch.eyebrow}
        title={pitch.title}
        lead={pitch.lead}
        parts={pitch.parts}
        primaryHref={pitch.ctaPrimaryHref}
        primaryLabel={pitch.ctaPrimary}
      />,
    );
    expect(screen.queryByText(/стабильное состояние/i)).not.toBeInTheDocument();
    expect(screen.getByText(/Цельная история/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: pitch.ctaPrimary })).toHaveAttribute(
      "href",
      "/onboarding/invite",
    );
  });
});
