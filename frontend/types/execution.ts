export interface ExecutionRun {
  id: string;
  project_id: string;
  run_type: "test" | "heal" | "build";
  sandbox_mode: "docker" | "local_process";
  status: "pending" | "running" | "passed" | "failed" | "healed" | "error";
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  iterations: number;
  duration_seconds: number;
  stdout?: string;
  stderr?: string;
  diagnostic_report?: Record<string, any>;
  created_at: string;
  completed_at?: string;
}
