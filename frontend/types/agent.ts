export interface AgentInfo {
  name: string;
  role: string;
  description: string;
  model: string;
  capabilities: string[];
  status?: "idle" | "working" | "completed" | "error";
}
