import MapPageClient from "@/components/map/MapPageClient";
import type { MapFeature } from "@/components/map/types";
import { getEmergencyServices, getGhats, getTemples } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function MapPage({
  searchParams,
}: {
  searchParams: { focus?: string };
}) {
  const [temples, ghats, emergency] = await Promise.all([
    getTemples({ limit: 100 }),
    getGhats({ limit: 100 }),
    getEmergencyServices(),
  ]);

  const features: MapFeature[] = [];
  const errors: string[] = [];

  if (temples.ok) {
    for (const temple of temples.data.items) {
      if (temple.latitude === null || temple.longitude === null) continue;
      features.push({
        key: `temple:${temple.slug}`,
        layer: "temples",
        name: temple.name,
        latitude: temple.latitude,
        longitude: temple.longitude,
        href: `/temples/${temple.slug}`,
        meta: temple.short_description ?? undefined,
      });
    }
  } else {
    errors.push(temples.error);
  }

  if (ghats.ok) {
    for (const ghat of ghats.data.items) {
      if (ghat.latitude === null || ghat.longitude === null) continue;
      features.push({
        key: `ghat:${ghat.slug}`,
        layer: "ghats",
        name: ghat.name,
        latitude: ghat.latitude,
        longitude: ghat.longitude,
        href: `/ghats/${ghat.slug}`,
        meta: ghat.description ?? undefined,
      });
    }
  } else {
    errors.push(ghats.error);
  }

  if (emergency.ok) {
    for (const service of emergency.data.items) {
      if (service.latitude === null || service.longitude === null) continue;
      features.push({
        key: `emergency:${service.id}`,
        layer: "emergency",
        name: service.name,
        latitude: service.latitude,
        longitude: service.longitude,
        href: "/emergency",
        meta: service.notes ?? undefined,
      });
    }
  } else {
    errors.push(emergency.error);
  }

  return (
    <MapPageClient
      features={features}
      focusKey={searchParams.focus}
      loadError={errors.length > 0 ? errors.join("; ") : null}
    />
  );
}
