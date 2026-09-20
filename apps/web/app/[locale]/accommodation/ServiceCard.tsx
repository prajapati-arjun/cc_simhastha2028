import { useTranslations } from "next-intl";
import { CardBase } from "@/components/Card";
import StatusBadge from "@/components/StatusBadge";
import type { EssentialService } from "./accommodationApi";

export function ServiceCard({ item }: { item: EssentialService }) {
  const t = useTranslations("accommodation");

  return (
    <CardBase
      title={item.name}
      badge={
        item.verified ? (
          <StatusBadge label={t("verified")} tone="success" />
        ) : (
          <StatusBadge label={t("unverified")} tone="neutral" />
        )
      }
    >
      <p className="text-sm font-medium text-ink-primary">
        {t(`serviceCategory.${item.category}`)}
      </p>
      {item.notes ? (
        <p className="text-sm text-ink-secondary">{item.notes}</p>
      ) : null}
    </CardBase>
  );
}

export default ServiceCard;
