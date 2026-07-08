import { render } from "@testing-library/react";
import { ElementAtmosphere } from "@/components/visualIdentity/ElementAtmosphere";

describe("ElementAtmosphere", () => {
  it("applies element pattern overlay for fire atmosphere", () => {
    const { container } = render(
      <ElementAtmosphere element="Fire">
        <p>Inner</p>
      </ElementAtmosphere>,
    );

    const wrap = container.firstElementChild as HTMLElement;
    expect(wrap).toHaveAttribute("data-element", "Fire");
    expect(wrap.style.getPropertyValue("--tf-element-pattern")).toContain("/images/icons/elements/fire.svg");
  });
});
