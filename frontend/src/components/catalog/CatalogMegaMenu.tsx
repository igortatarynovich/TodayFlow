"use client";

import { Fragment, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { t } from "@/lib/i18n";
import { catalogNavigation, getProduct, getProductDetailPath } from "@/data/catalog";

export default function CatalogMegaMenu() {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;
    const handleClick = (event: MouseEvent) => {
      if (!containerRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    window.addEventListener("mousedown", handleClick);
    return () => window.removeEventListener("mousedown", handleClick);
  }, [open]);

  return (
    <div className="tf-catalog-wrapper" ref={containerRef}>
      <button type="button" className="tf-catalog-trigger" onClick={() => setOpen((prev) => !prev)}>
        {t("layout.nav.catalog", "Catalog")}
      </button>
      {open && (
        <div className="tf-catalog-menu">
          {catalogNavigation.columns.map((column) => (
            <div key={column.slug} className="tf-catalog-column">
              <div className="tf-catalog-column-heading">
                <div>
                  <h4>{t(column.title_key)}</h4>
                  <p>{t(column.description_key)}</p>
                </div>
                {column.href && (
                  <Link href={column.href} className="tf-catalog-column-link">
                    {t("catalog.nav.column_link")}
                  </Link>
                )}
              </div>
              {column.sections.map((section) => (
                <Fragment key={section.slug}>
                  <h5>{t(section.title_key)}</h5>
                  <ul>
                    {section.items.map((item) => {
                      const product = item.product_id ? getProduct(item.product_id) : undefined;
                      if (!product) return null;
                      return (
                        <li key={product.id}>
                          <Link href={getProductDetailPath(product.id)}>
                            <span>{t(product.title_key)}</span>
                            {product.badge && <span className="tf-catalog-badge">{t(`catalog.badge.${product.badge}`, product.badge)}</span>}
                          </Link>
                        </li>
                      );
                    })}
                  </ul>
                </Fragment>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
