import RealmOwnerSectionPage from "@/components/realm-owner/realm-owner-section-page";

export default function RealmToolsPage({ params }: { params: { realm_id: string } }) {
  return <RealmOwnerSectionPage realmId={params.realm_id} section="tools" />;
}
