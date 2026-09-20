"use client";

import EntityForm from "@/components/admin/EntityForm";

export default function AdminghatsEditPage({
  params,
}: {
  params: { id: string };
}) {
  return <EntityForm entityKey="ghats" recordId={Number(params.id)} />;
}
