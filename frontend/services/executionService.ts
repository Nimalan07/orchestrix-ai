import { api } from "./api";
import { ExecutionRun } from "../types/execution";

export const executionService = {
  executeProject: async (
    projectId: string,
    options: { max_iterations?: number; sandbox_mode?: string } = {}
  ): Promise<ExecutionRun> => {
    const res = await api.post<ExecutionRun>(
      `/api/projects/${projectId}/execute`,
      {
        max_iterations: options.max_iterations ?? 3,
        sandbox_mode: options.sandbox_mode ?? "auto",
      }
    );
    return res.data;
  },

  getRuns: async (projectId: string): Promise<ExecutionRun[]> => {
    try {
      const res = await api.get<ExecutionRun[]>(
        `/api/projects/${projectId}/runs`
      );
      return res.data;
    } catch (err: any) {
      if (err.response?.status === 404) return [];
      throw err;
    }
  },

  getRunById: async (
    projectId: string,
    runId: string
  ): Promise<ExecutionRun> => {
    const res = await api.get<ExecutionRun>(
      `/api/projects/${projectId}/runs/${runId}`
    );
    return res.data;
  },
};
