export type PublicIntakePageState =
  | "loading"
  | "empty"
  | "draft"
  | "submitting"
  | "processing"
  | "submitted"
  | "blocked"
  | "error"
  | "no-permission"
  | "expired";

export interface PublicIntakeContext {
  token_status: "valid";
  realm: {
    realm_code: string;
    realm_type: string;
    display_name: string;
  };
  allowed_file_types: string[];
  max_files: number;
  max_file_bytes: number;
  analysis: {
    external_ai_ready: boolean;
    mode: string;
    notice: string;
  };
  latest_draft: PublicIntakeRecord | null;
  latest_submission: PublicIntakeRecord | null;
  audit: {
    scope: string;
    token_kind: string;
  };
}

export interface PublicIntakeRecord {
  id: string;
  intake_code: string;
  status: string;
  relationship: string | null;
  pasted_text: string | null;
  supplemental_notes: string | null;
  file_manifest: PublicIntakeFile[];
  source_truth_status: string;
  confirmed_at: string | null;
  created_at: string | null;
  updated_at: string | null;
  form: PublicIntakeFormState;
  processing_status: string | null;
  latest_analysis?: PublicIntakeAnalysis | null;
  analyses?: PublicIntakeAnalysis[];
}

export interface PublicIntakeFile {
  file_id: string;
  file_name: string;
  ext: string;
  content_type: string;
  size: number;
  parse_status: string;
  parse_error: string | null;
  snippet?: string;
}

export interface PublicIntakeFormState {
  enterprise_name: string;
  brand_name: string;
  product_or_project_name: string;
  relationship: string;
  problem: string;
  website_url: string;
  pasted_text: string;
  supplemental_notes: string;
  consent_data_analysis: boolean;
  consent_use_authorization: boolean;
  server_staging_consent: boolean;
  consent_at: string | null;
  policy_version: string | null;
}

export interface PublicIntakeAnalysis {
  id: string;
  version: number;
  status: string;
  fields: PublicIntakeField[];
  summary: string | null;
  suggested_next_steps: string[];
  analysis_mode: string;
  model_name: string | null;
  confirmed_at: string | null;
  created_at: string | null;
}

export interface PublicIntakeField {
  key: string;
  label: string;
  value: string;
  status: "observed" | "inferred" | "unknown";
  confidence: number;
  source_file: string | null;
  notes: string;
}

export interface PublicIntakeFormValues {
  enterpriseName: string;
  brandName: string;
  productOrProjectName: string;
  relationship: string;
  problem: string;
  websiteUrl: string;
  pastedText: string;
  supplementalNotes: string;
  consentDataAnalysis: boolean;
  consentUseAuthorization: boolean;
  serverStagingConsent: boolean;
}

export interface PublicIntakeApiError {
  status: number;
  code?: string;
  message: string;
}
