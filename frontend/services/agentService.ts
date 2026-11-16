import { api } from "./api";
import { AgentInfo } from "../types/agent";

export const agentService = {
  getRoster: async (): Promise<AgentInfo[]> => {
    try {
      const res = await api.get<{ agents: AgentInfo[] }>("/api/agents/roster");
      return res.data.agents || (res.data as any);
    } catch (err) {
      // Fallback default roster
      return [
        {
          name: "Requirement Analyzer",
          role: "Requirements Engineering",
          description: "Converts natural-language requirements into structured JSON specifications.",
          model: "qwen2.5-coder:7b",
          capabilities: ["NLP Extraction", "Schema Validation", "JSON Self-Repair"],
          status: "completed",
        },
        {
          name: "Architect Agent",
          role: "System Architecture",
          description: "Designs component architecture, data entities, and API contracts.",
          model: "qwen2.5-coder:7b",
          capabilities: ["API Contract Design", "Data Modeling", "Tech Stack Selection"],
          status: "completed",
        },
        {
          name: "Planner Agent",
          role: "Task Decomposition & DAG",
          description: "Breaks architecture into dependency-aware ordered tasks using Kahn's algorithm.",
          model: "qwen2.5-coder:7b",
          capabilities: ["DAG Generation", "Topological Wave Sorting", "Cycle Detection"],
          status: "completed",
        },
        {
          name: "Database Engineer",
          role: "Data Persistence",
          description: "Generates SQLAlchemy models, schemas, and Alembic database migrations.",
          model: "qwen2.5-coder:7b",
          capabilities: ["SQLAlchemy 2.x", "PostgreSQL", "Alembic Migrations"],
          status: "completed",
        },
        {
          name: "Backend Developer",
          role: "API & Business Logic",
          description: "Generates FastAPI endpoints, services, authentication, and CRUD operations.",
          model: "qwen2.5-coder:7b",
          capabilities: ["FastAPI", "Pydantic v2", "JWT Auth", "REST APIs"],
          status: "completed",
        },
        {
          name: "Frontend Developer",
          role: "UI & Component Design",
          description: "Builds responsive pages, forms, and client components using Next.js and Tailwind.",
          model: "qwen2.5-coder:7b",
          capabilities: ["Next.js 14", "React", "TypeScript", "Tailwind CSS"],
          status: "completed",
        },
        {
          name: "Testing Agent",
          role: "Quality Assurance",
          description: "Synthesizes Pytest test suites and verifies applications in isolated sandboxes.",
          model: "qwen2.5-coder:7b",
          capabilities: ["Pytest Automation", "Sandbox Execution", "Failure Log Parsing"],
          status: "completed",
        },
        {
          name: "Debugger Agent",
          role: "Autonomous Self-Healing",
          description: "Diagnoses stack traces, locates root causes, and generates verified code repairs.",
          model: "qwen2.5-coder:7b",
          capabilities: ["Root Cause Diagnosis", "Targeted Unified Diff Patches", "Self-Healing Loop"],
          status: "completed",
        },
      ];
    }
  },
};
