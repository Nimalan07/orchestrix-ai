import { api, API_BASE_URL } from "./api";
import {
  Project,
  RequirementAnalysisResponse,
  RequirementSpecification,
  SystemArchitecture,
  Task,
  DAGResponse,
  FileArtifact,
  GenerationManifest,
} from "../types/project";

export const projectService = {
  getAll: async (limit = 50, offset = 0): Promise<Project[]> => {
    const res = await api.get<Project[]>("/api/projects", {
      params: { limit, offset },
    });
    return res.data;
  },

  getById: async (id: string): Promise<Project> => {
    const res = await api.get<Project>(`/api/projects/${id}`);
    return res.data;
  },

  create: async (data: { name: string; description: string }): Promise<Project> => {
    const res = await api.post<Project>("/api/projects", data);
    return res.data;
  },

  update: async (id: string, data: Partial<Project>): Promise<Project> => {
    const res = await api.put<Project>(`/api/projects/${id}`, data);
    return res.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/projects/${id}`);
  },

  analyzeRequirements: async (id: string): Promise<RequirementAnalysisResponse> => {
    const res = await api.post<RequirementAnalysisResponse>(
      `/api/projects/${id}/analyze`
    );
    return res.data;
  },

  getRequirements: async (id: string): Promise<RequirementSpecification | null> => {
    try {
      const res = await api.get(`/api/projects/${id}/requirements`);
      return res.data;
    } catch (err: any) {
      if (err.response?.status === 404) return null;
      throw err;
    }
  },

  generateArchitecture: async (id: string): Promise<{ specification: SystemArchitecture }> => {
    const res = await api.post(`/api/projects/${id}/architect`);
    return res.data;
  },

  getArchitecture: async (id: string): Promise<SystemArchitecture | null> => {
    try {
      const res = await api.get(`/api/projects/${id}/architecture`);
      return res.data.specification || res.data;
    } catch (err: any) {
      if (err.response?.status === 404) return null;
      throw err;
    }
  },

  planTasks: async (id: string): Promise<DAGResponse> => {
    const res = await api.post<DAGResponse>(`/api/projects/${id}/plan`);
    return res.data;
  },

  getTasks: async (id: string): Promise<Task[]> => {
    try {
      const res = await api.get<Task[]>(`/api/projects/${id}/tasks`);
      return res.data;
    } catch (err: any) {
      if (err.response?.status === 404) return [];
      throw err;
    }
  },

  getDAG: async (id: string): Promise<DAGResponse | null> => {
    try {
      const res = await api.get<DAGResponse>(`/api/projects/${id}/tasks/dag`);
      return res.data;
    } catch (err: any) {
      if (err.response?.status === 404) return null;
      throw err;
    }
  },

  generateCode: async (id: string): Promise<GenerationManifest> => {
    const res = await api.post<GenerationManifest>(
      `/api/projects/${id}/generate`
    );
    return res.data;
  },

  getArtifacts: async (id: string): Promise<FileArtifact[]> => {
    try {
      const res = await api.get<FileArtifact[]>(`/api/projects/${id}/artifacts`);
      return res.data;
    } catch (err: any) {
      if (err.response?.status === 404) return [];
      throw err;
    }
  },

  getFiles: async (id: string): Promise<{ relative_path: string; size_bytes: number; sha256: string }[]> => {
    try {
      const res = await api.get(`/api/projects/${id}/files`);
      return res.data;
    } catch (err: any) {
      if (err.response?.status === 404) return [];
      throw err;
    }
  },

  readFile: async (id: string, filePath: string): Promise<string> => {
    const res = await api.get(`/api/projects/${id}/file`, {
      params: { file_path: filePath },
      responseType: "text",
    });
    return res.data;
  },

  getManifest: async (id: string): Promise<GenerationManifest | null> => {
    try {
      const res = await api.get<GenerationManifest>(`/api/projects/${id}/manifest`);
      return res.data;
    } catch (err: any) {
      if (err.response?.status === 404) return null;
      throw err;
    }
  },

  getExportUrl: (id: string): string => {
    return `${API_BASE_URL}/api/projects/${id}/export`;
  },
};
