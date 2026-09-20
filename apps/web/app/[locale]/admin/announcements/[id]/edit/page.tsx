"use client";

import EntityForm from "@/components/admin/EntityForm";

export default function AdminannouncementsEditPage({
  params,
}: {
  params: { id: string };
}) {
  return <EntityForm entityKey="announcements" recordId={Number(params.id)} />;
}
