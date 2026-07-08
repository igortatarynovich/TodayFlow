import { PropsWithChildren } from "react";

type Props = PropsWithChildren<{
  eyebrow?: string;
  title: string;
  body: string;
}>;

export function CatalogCallout({ eyebrow, title, body, children }: Props) {
  return (
    <aside className="catalog-callout">
      {eyebrow && <p className="catalog-callout-eyebrow">{eyebrow}</p>}
      <h3>{title}</h3>
      <p>{body}</p>
      {children}
    </aside>
  );
}
