import { render, screen } from "@testing-library/react";
import {
  DsCallout,
  DsCapsule,
  DsEmph,
  DsQuote,
  DS_CALLOUT_LABEL_COPY,
} from "@/design-system/primitives/DsCallout";

describe("DsCallout semantic layers", () => {
  it("renders tone rail and independent label capsule", () => {
    render(
      <DsCallout tone="avoid" label="attention" icon="flag" title="Не путай скорость с действием.">
        <p>Расшифровка.</p>
      </DsCallout>,
    );
    const root = screen.getByTestId("ds-callout");
    expect(root).toHaveAttribute("data-tone", "avoid");
    expect(screen.getByText(DS_CALLOUT_LABEL_COPY.attention)).toBeInTheDocument();
    expect(screen.getByText("Не путай скорость с действием.")).toBeInTheDocument();
    expect(screen.getByText("Расшифровка.")).toBeInTheDocument();
  });

  it("allows any tone × label pair", () => {
    render(<DsCallout tone="practice" label="money" title="Деньги: один счёт." />);
    expect(screen.getByTestId("ds-callout")).toHaveAttribute("data-tone", "practice");
    expect(screen.getByText(DS_CALLOUT_LABEL_COPY.money)).toBeInTheDocument();
  });

  it("renders capsule and quote helpers", () => {
    render(
      <>
        <DsCapsule label="next_step" icon="arrowDown" />
        <DsQuote kicker="Сегодня">Один спокойный шаг.</DsQuote>
        <p>
          Выбери <DsEmph>стабильность</DsEmph>.
        </p>
      </>,
    );
    expect(screen.getByText(DS_CALLOUT_LABEL_COPY.next_step)).toBeInTheDocument();
    expect(screen.getByTestId("ds-quote")).toHaveTextContent("Один спокойный шаг.");
    expect(screen.getByText("стабильность").tagName).toBe("STRONG");
  });
});
