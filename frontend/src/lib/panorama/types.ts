export type ApplicationSurface = "panorama" | "owner" | "public" | "operations" | "governance" | "midplatform" | "backend";

export type PageTemplate = "workbench" | "list" | "detail" | "config" | "management" | "canvas";

export interface PanoramaPage {
  page_id: string;
  title: string;
  application_surface: ApplicationSurface;
  route: string;
  template: PageTemplate;
  feature_flag: string;
  data_mode: string;
  design_status: string;
  implementation_status: string;
  fixture_ids: string[];
  required_capabilities: string[];
  next_realization_task: string;
}

export interface PanoramaFixture {
  fixture_id: string;
  application_surface: string;
  page_id: string;
  realm_id: string;
  project_id: string;
  user_role: string;
  truth_scope: string;
  scenario: string;
  data_mode: string;
  generated_at: string;
  source_label: string;
  simulation_marker: boolean;
  no_real_write: boolean;
}

export interface CapabilityEntry {
  capability_id: string;
  name: string;
  duty: string;
  serves: string[];
  inputs: string[];
  outputs: string[];
  status: string;
  next_realization_task: string;
}

export interface BaseEntry {
  base_id: string;
  name: string;
  duty: string;
  serves: string[];
  inputs: string[];
  outputs: string[];
  status: string;
  next_realization_task: string;
}

export interface PanoramaRegistry {
  version: string;
  generated_at: string;
  application_surfaces: string[];
  pages: PanoramaPage[];
}

export interface PanoramaFixtureRegistry {
  version: string;
  fixtures: PanoramaFixture[];
}

export interface PanoramaCapabilityMap {
  version: string;
  midplatforms: CapabilityEntry[];
  bases: BaseEntry[];
  page_to_capability: Record<string, string[]>;
}
