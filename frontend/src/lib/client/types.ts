export interface ClientProject {
  id: string;
  project_code: string;
  name: string;
  status: string;
  lifecycle_state: string;
  truth_status: string;
  created_at: string | null;
  assets: Array<{ title: string; asset_type: string; truth_status: string }>;
  outcomes: Array<{ claim_text: string; outcome_type: string; truth_status: string }>;
}

export interface ClientProjectContext {
  token_status: string;
  realm: {
    realm_code: string;
    realm_type: string;
    display_name: string;
  };
  authorization: {
    use_scope: string;
    source_name: string | null;
    grantee_type: string | null;
    valid_until: string | null;
    status: string;
    authorization_code_masked: string;
  };
  projects: ClientProject[];
}
