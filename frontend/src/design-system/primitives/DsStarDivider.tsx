import { joinClass } from "@/design-system/utils/joinClass";
import { IconStar } from "@/design-system/icons/DsIcons";
import fk from "@/design-system/primitives/dsFormKit.module.css";

type DsStarDividerProps = {
  className?: string;
  testId?: string;
};

export function DsStarDivider({ className, testId }: DsStarDividerProps) {
  return (
    <div className={joinClass(fk.starDivider, className)} data-testid={testId} role="separator">
      <hr className={fk.starDividerLine} />
      <span className={fk.starDividerIcon} aria-hidden>
        <IconStar />
      </span>
      <hr className={fk.starDividerLine} />
    </div>
  );
}
