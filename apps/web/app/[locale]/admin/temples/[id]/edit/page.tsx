"use client";

import EntityForm from "@/components/admin/EntityForm";

export default function AdmintemplesEditPage({
  params,
}: {
  params: { id: string };
}) {
  return <EntityForm entityKey="temples" recordId={Number(params.id)} />;
}
