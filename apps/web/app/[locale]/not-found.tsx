import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";

export default function LocaleNotFound() {
  const t = useTranslations("states");
  const tc = useTranslations("common");
  return (
    <div className="container-app section-y text-center">
      <h1>{t("notFoundTitle")}</h1>
      <p className="mt-2 text-ink-secondary">{t("notFoundBody")}</p>
      <div className="mt-6 flex justify-center">
        <Link href="/" className="btn-primary">
          {tc("back")}
        </Link>
      </div>
    </div>
  );
}
