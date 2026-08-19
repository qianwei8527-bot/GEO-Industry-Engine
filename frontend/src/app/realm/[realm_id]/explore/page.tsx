"use client";

import { useParams } from "next/navigation";
import RealmOwnerShell from "@/components/realm-owner/realm-owner-shell";

export default function RealmExplorePage() {
  const params = useParams<{ realm_id?: string | string[] }>();
  const realmId = Array.isArray(params.realm_id) ? params.realm_id[0] : params.realm_id || "";
  return <RealmOwnerShell realmId={realmId} />;
}