import type { ReactNode } from "react";
import { Link } from "@/i18n/navigation";

/** Breadcrumb — Directory > Detail trail on detail pages. */
export function Breadcrumb({
  items,
}: {
  items: { href?: string; label: string }[];
}) {
  return (
    <nav aria-label="Breadcrumb" className="mb-4">
      <ol className="flex flex-wrap items-center gap-1 text-sm text-ink-secondary">
        {items.map((item, index) => (
          <li key={item.label} className="flex items-center gap-1">
            {index > 0 ? <span aria-hidden="true">/</span> : null}
            {item.href ? (
              <Link href={item.href} className="link-inline">
                {item.label}
              </Link>
            ) : (
              <span aria-current="page">{item.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}

/** Standard page heading block: H1 + optional intro + optional meta slot. */
export function PageHeading({
  title,
  intro,
  meta,
}: {
  title: string;
  intro?: string;
  meta?: ReactNode;
}) {
  return (
    <div className="mb-6">
      <h1>{title}</h1>
      {intro ? <p className="mt-2 max-w-3xl text-ink-secondary">{intro}</p> : null}
      {meta ? <div className="mt-3">{meta}</div> : null}
    </div>
  );
}

/** Content section with a heading, used on detail pages. */
export function DetailSection({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="mt-8">
      <h2 className="text-xl font-semibold md:text-2xl">{title}</h2>
      <div className="mt-2 text-ink-primary">{children}</div>
    </section>
  );
}
