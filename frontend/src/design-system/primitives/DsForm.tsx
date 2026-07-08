import type { ReactNode } from "react";
import { joinClass } from "@/design-system/utils/joinClass";
import p from "@/design-system/primitives/dsPrimitives.module.css";

export function DsTextField({
  label,
  value,
  placeholder,
  className,
}: {
  label: string;
  value?: string;
  placeholder?: string;
  className?: string;
}) {
  return (
    <label className={joinClass(p.field, className)}>
      <span className={p.inputLabel}>{label}</span>
      <div className={p.input}>
        <input
          className={p.searchInput}
          defaultValue={value}
          placeholder={placeholder}
          aria-label={label}
        />
      </div>
    </label>
  );
}

export function DsSearchField({
  placeholder,
  icon,
  className,
}: {
  placeholder: string;
  icon?: ReactNode;
  className?: string;
}) {
  return (
    <div className={joinClass(p.search, className)}>
      {icon}
      <input className={p.searchInput} placeholder={placeholder} aria-label={placeholder} />
    </div>
  );
}

export function DsChipField({
  label,
  icon,
  className,
}: {
  label: string;
  icon?: ReactNode;
  className?: string;
}) {
  return (
    <div className={joinClass(p.chip, className)}>
      {icon}
      <span>{label}</span>
    </div>
  );
}

export function DsClassifier({
  label,
  icon,
  className,
}: {
  label: string;
  icon?: ReactNode;
  className?: string;
}) {
  return (
    <span className={joinClass(p.classifier, className)}>
      {icon}
      {label}
    </span>
  );
}

export function DsCheckbox({
  checked,
  onChange,
  className,
  disabled,
  "aria-label": ariaLabel,
}: {
  checked?: boolean;
  onChange?: (checked: boolean) => void;
  className?: string;
  disabled?: boolean;
  "aria-label"?: string;
}) {
  return (
    <input
      type="checkbox"
      className={joinClass(p.checkbox, className)}
      checked={checked}
      disabled={disabled}
      aria-label={ariaLabel}
      onChange={(e) => onChange?.(e.target.checked)}
    />
  );
}
