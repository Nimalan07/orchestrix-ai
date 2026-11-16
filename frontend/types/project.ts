export interface Project {
  id: string;
  name: string;
  description: string;
  status: "created" | "analyzed" | "architected" | "planned" | "generating" | "completed" | "failed";
  created_at: string;
  updated_at: string;
}

export interface FunctionalRequirement {
  id: string;
  title: string;
  description: string;
  priority: string;
}

export interface NonFunctionalRequirement {
  category: string;
  requirement: string;
  metric?: string;
}

export interface FeatureModule {
  name: string;
  description: string;
  components: string[];
}

export interface UserRole {
  role_name: string;
  description?: string;
  permissions: string[];
}

export interface TechnicalConstraint {
  category?: string;
  constraint?: string;
  rationale?: string;
}

export interface AcceptanceCriterion {
  id?: string;
  scenario?: string;
  given?: string;
  when?: string;
  then?: string;
  criterion?: string;
  verification_method?: string;
}

export interface RequirementSpecification {
  project_name?: string;
  overview?: string;
  project_overview?: string;
  target_audience?: string;
  functional_requirements: FunctionalRequirement[];
  non_functional_requirements: NonFunctionalRequirement[];
  user_roles: UserRole[];
  core_features?: FeatureModule[];
  feature_modules?: FeatureModule[];
  technical_constraints: (string | TechnicalConstraint)[];
  acceptance_criteria: (string | AcceptanceCriterion)[];
  clarifying_questions: string[];
}

export interface RequirementAnalysisResponse {
  project_id: string;
  specification: RequirementSpecification;
  analyzed_at: string;
}

export interface TechStack {
  backend: string;
  frontend: string;
  database: string;
  orm: string;
  authentication: string;
}

export interface APIContract {
  endpoint: string;
  method: string;
  summary: string;
  request_schema?: Record<string, any>;
  response_schema?: Record<string, any>;
}

export interface EntityField {
  name: string;
  type: string;
  primary_key?: boolean;
  nullable?: boolean;
  unique?: boolean;
  description?: string;
}

export interface DataEntity {
  name: string;
  table_name?: string;
  description?: string;
  fields: EntityField[];
  relationships?: string[];
}

export interface SystemArchitecture {
  project_name: string;
  architecture_pattern: string;
  tech_stack: TechStack;
  components?: { name: string; type: string; responsibilities: string[] }[];
  entities?: DataEntity[];
  data_entities?: DataEntity[];
  api_contracts: APIContract[];
  architectural_decisions?: { decision: string; rationale: string }[];
  decisions?: any[];
}

export interface Task {
  id: string;
  project_id: string;
  task_key: string;
  title: string;
  description: string;
  assigned_agent: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  wave: number;
  dependencies: string[];
}

export interface DAGResponse {
  tasks: Task[];
  waves: Record<string, Task[]>;
  total_waves: number;
  has_cycle: boolean;
  cycle_path: string[];
}

export interface FileArtifact {
  id: string;
  project_id: string;
  task_id?: string;
  file_path: string;
  file_hash: string;
  version: number;
  generated_by_agent: string;
  created_at: string;
}

export interface GenerationManifest {
  project_id: string;
  project_name: string;
  workspace_directory: string;
  total_files: number;
  files: { relative_path: string; size_bytes: number; sha256: string }[];
  generated_at: string;
}
