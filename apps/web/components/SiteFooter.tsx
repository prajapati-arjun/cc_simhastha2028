import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";

const FOOTER_LINKS = [
  { href: "/events", key: "events" },
  { href: "/temples", key: "temples" },
  { href: "/ghats", key: "ghats" },
  { href: "/map", key: "map" },
  { href: "/emergency", key: "emergency" },
  { href: "/lost-found/status", key: "lostFound" },
  { href: "/missing-person/status", key: "missingPerson" },
] as const;

export function SiteFooter() {
  const t = useTranslations("nav");
  const tc = useTranslations("common");

  return (
    <footer className="mt-auto border-t border-surface-border bg-surface-subtle">
      <div className="container-app py-8">
        <nav aria-label="Footer">
          <ul className="flex flex-wrap gap-x-4 gap-y-1">
            {FOOTER_LINKS.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="touch-target rounded-md px-1 text-sm text-primary-700 underline underline-offset-2"
                >
                  {t(item.key)}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <p className="mt-6 text-sm text-ink-secondary">
          {tc("appName")} — {tc("appTagline")}
        </p>
        <p className="mt-1 text-xs text-ink-muted">{tc("prototypeFooterNote")}</p>
      </div>
    </footer>
  );
}

export default SiteFooter;
