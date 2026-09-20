"use client";

import EntityForm from "@/components/admin/EntityForm";

export default function AdmineventsEditPage({
  params,
}: {
  params: { id: string };
}) {
  return <EntityForm entityKey="events" recordId={Number(params.id)} />;
}
