import { useTranslations } from "next-intl";
import { CardBase } from "@/components/Card";
import StatusBadge from "@/components/StatusBadge";
import type { Accommodation } from "./accommodationApi";

/**
 * Co-located with the accommodation feature rather than added to the shared
 * `components/Card.tsx` (other agents are editing shared components
 * concurrently this sprint). Reuses `CardBase` / `StatusBadge` by import only.
 */
export function AccommodationCard({ item }: { item: Accommodation }) {
  const t = useTranslations("accommodation");

  return (
    <CardBase
      title={item.name}
      badge={
        // PRD section 17: officially verified entries must be visibly
        // distinguished from third-party/commercial ones - the badge is
        // always rendered, never colour-only, and shown for both states.
        item.verified ? (
          <StatusBadge label={t("verified")} tone="success" />
        ) : (
          <StatusBadge label={t("unverified")} tone="neutral" />
        )
      }
    >
      <p className="text-sm font-medium text-ink-primary">
        {t(`type.${item.accommodation_type}`)}
        {item.price_tier ? ` · ${t(`priceTier.${item.price_tier}`)}` : ""}
      </p>
      {item.address ? (
        <p className="text-sm text-ink-secondary">{item.address}</p>
      ) : null}
      {item.contact_phone ? (
        <p className="text-sm text-ink-secondary">
          {t("contact")}:{" "}
          <a
            href={`tel:${item.contact_phone.replace(/[^+\d]/g, "")}`}
            className="link-inline"
          >
            {item.contact_phone}
          </a>
        </p>
      ) : null}
      {item.description ? (
        <p className="text-sm text-ink-secondary">{item.description}</p>
      ) : null}
    </CardBase>
  );
}

export default AccommodationCard;
