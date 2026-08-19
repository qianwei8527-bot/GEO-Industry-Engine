import type {
  PublicIntakeApiError,
  PublicIntakeContext,
  PublicIntakeFormValues,
  PublicIntakeRecord,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";

async function parseError(res: Response): Promise<PublicIntakeApiError> {
  let message = `请求失败 (${res.status})`;
  let code: string | undefined;
  try {
    const data = (await res.json()) as { detail?: string | { code?: string; message?: string }; message?: string };
    const detail = data.detail;
    if (typeof detail === "string") {
      const separator = detail.indexOf(":");
      if (separator > 0) {
        code = detail.slice(0, separator).trim();
        message = detail.slice(separator + 1).trim();
      } else {
        message = detail;
      }
    } else if (detail && typeof detail === "object") {
      code = detail.code;
      message = detail.message || message;
    } else if (data.message) {
      message = data.message;
    }
  } catch {
    // keep fallback message
  }
  return { status: res.status, code, message };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) throw await parseError(res);
  return res.json() as Promise<T>;
}

export function fetchPublicIntakeContext(token: string): Promise<PublicIntakeContext> {
  return request<PublicIntakeContext>(`/intakes/public/${encodeURIComponent(token)}`);
}

export async function savePublicIntakeDraft(
  token: string,
  form: PublicIntakeFormValues,
  files: File[],
): Promise<PublicIntakeRecord> {
  const body = buildFormData(form, files);
  return request<PublicIntakeRecord>(`/intakes/public/${encodeURIComponent(token)}/draft`, {
    method: "POST",
    body,
  });
}

export async function submitPublicIntake(
  token: string,
  form: PublicIntakeFormValues,
  files: File[],
): Promise<PublicIntakeRecord> {
  const body = buildFormData(form, files);
  return request<PublicIntakeRecord>(`/intakes/public/${encodeURIComponent(token)}/submissions`, {
    method: "POST",
    body,
  });
}

function buildFormData(form: PublicIntakeFormValues, files: File[]): FormData {
  const body = new FormData();
  body.set("enterprise_name", form.enterpriseName.trim());
  body.set("brand_name", form.brandName.trim());
  body.set("product_or_project_name", form.productOrProjectName.trim());
  body.set("relationship", form.relationship.trim());
  body.set("problem", form.problem.trim());
  body.set("website_url", form.websiteUrl.trim());
  body.set("pasted_text", form.pastedText.trim());
  body.set("supplemental_notes", form.supplementalNotes.trim());
  body.set("consent_data_analysis", String(form.consentDataAnalysis));
  body.set("consent_use_authorization", String(form.consentUseAuthorization));
  body.set("server_staging_consent", String(form.serverStagingConsent));
  files.forEach((file) => body.append("files", file, file.name));
  return body;
}
