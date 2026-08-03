import { render, screen } from "@testing-library/react";
import { ProductNarrativeBlock } from "@/components/product-ui/ProductJourneyScene";
import { TODAY_DOMAIN_ICON_MAP } from "@/design-system/icons/DsIcons";
import { domainIconForChapterId } from "@/lib/todayReadingDomainIcon";
import { mapSphereToDomain } from "@/lib/todayDomainSignal";

describe("Reading domain icons (FOUNDATION_UI §16.6 A1)", () => {
  it("renders an icon for sphere-work beside the kicker", () => {
    const DomainIcon = domainIconForChapterId("sphere-work");
    expect(DomainIcon).not.toBeNull();
    render(
      <ProductNarrativeBlock
        id="sphere-work"
        kicker="Работа"
        kickerIcon={
          DomainIcon ? (
            <span data-testid="today-reading-domain-icon-sphere-work">
              <DomainIcon />
            </span>
          ) : null
        }
        surface="plain"
        paragraphs={["Одна задача до обеда."]}
      />,
    );
    expect(screen.getByTestId("today-reading-domain-icon-sphere-work").querySelector("svg")).not.toBeNull();
  });

  it("maps sphere-work_decisions to work icon", () => {
    expect(mapSphereToDomain("work_decisions")).toBe("work");
    expect(domainIconForChapterId("sphere-work_decisions")).toBe(TODAY_DOMAIN_ICON_MAP.work);
  });

  it("omits icon for non-sphere chapters", () => {
    expect(domainIconForChapterId("opening")).toBeNull();
    render(
      <ProductNarrativeBlock id="opening" kicker="Суть дня" surface="plain" paragraphs={["Тон дня."]} />,
    );
    expect(screen.queryByTestId("today-reading-domain-icon-opening")).toBeNull();
    expect(screen.getByText("Суть дня")).toBeInTheDocument();
  });
});
