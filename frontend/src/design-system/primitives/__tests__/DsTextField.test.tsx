import { render, screen, fireEvent } from "@testing-library/react";
import { DsTextField } from "@/design-system/primitives/DsForm";

describe("DsTextField", () => {
  it("supports controlled value + onChange", () => {
    const onChange = jest.fn();
    render(
      <DsTextField
        label="Своё обещание"
        value="утро"
        onChange={onChange}
        data-testid="ds-text"
      />,
    );
    const input = screen.getByTestId("ds-text");
    expect(input).toHaveValue("утро");
    fireEvent.change(input, { target: { value: "утро без спешки" } });
    expect(onChange).toHaveBeenCalledWith("утро без спешки");
  });

  it("keeps uncontrolled catalog demos working without onChange", () => {
    render(<DsTextField label="Personal Archetype" value="The Explorer" />);
    expect(screen.getByDisplayValue("The Explorer")).toBeInTheDocument();
  });
});
