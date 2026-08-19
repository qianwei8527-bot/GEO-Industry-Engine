import PublicIntakePage from "@/components/public-intake/public-intake-page";

export default function IntakeTokenPage({
  params,
}: {
  params: { secure_token: string | string[] };
}) {
  const token = Array.isArray(params.secure_token) ? params.secure_token[0] : params.secure_token;
  return <PublicIntakePage token={token} />;
}
