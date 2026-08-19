import RealmOwnerSectionPage from "@/components/realm-owner/realm-owner-section-page";

export default function RealmProjectsPage({ params }: { params: { realm_id: string } }) {
  return <RealmOwnerSectionPage realmId={params.realm_id} section="projects" />;
}
