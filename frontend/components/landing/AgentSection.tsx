"use client";

import {
  FileSearch,
  Layers,
  GitBranch,
  Database,
  Server,
  Layout,
  CheckCircle,
  Wrench,
} from "lucide-react";

export default function AgentSection() {
  const agents = [
    {
      role: "Requirement Analyzer",
      description: "Converts natural-language requirements into structured JSON specifications.",
      icon: FileSearch,
      output: "requirements.json",
      stage: "Stage 01",
    },
    {
      role: "Architect Agent",
      description: "Designs system architecture, data entities, and typed API contracts.",
      icon: Layers,
      output: "architecture.json",
      stage: "Stage 02",
    },
    {
      role: "Planner Agent",
      description: "Creates dependency-aware engineering tasks using deterministic DAG Kahn algorithm.",
      icon: GitBranch,
      output: "dag_waves.json",
      stage: "Stage 03",
    },
    {
      role: "Database Engineer",
      description: "Generates SQLAlchemy 2.x models, schemas, and Alembic database migrations.",
      icon: Database,
      output: "models / migrations",
      stage: "Stage 04",
    },
    {
      role: "Backend Developer",
      description: "Generates FastAPI routers, CRUD services, and secure JWT authentication.",
      icon: Server,
      output: "api / services",
      stage: "Stage 05",
    },
    {
      role: "Frontend Developer",
      description: "Builds responsive pages, interactive forms, and reusable UI components.",
      icon: Layout,
      output: "pages / components",
      stage: "Stage 06",
    },
    {
      role: "Testing Agent",
      description: "Executes Pytest test suites inside isolated sandboxes and parses failure diagnostics.",
      icon: CheckCircle,
      output: "test_report.json",
      stage: "Stage 07",
    },
    {
      role: "Debugger Agent",
      description: "Diagnoses stack traces, locates root causes, and generates targeted code repairs.",
      icon: Wrench,
      output: "self_healing_patch",
      stage: "Stage 08",
    },
  ];

  return (
    <section id="agents" className="py-24 bg-white border-b border-border">
      <div className="max-w-7xl mx-auto px-6">
        <div className="max-w-3xl mx-auto text-center mb-16">
          <div className="text-xs font-mono text-grey-500 tracking-widest uppercase mb-3">
            08 SPECIALIZED ROLES
          </div>
          <h2 className="font-serif text-3xl sm:text-4xl md:text-5xl font-normal text-black mb-4">
            A specialized team of AI engineers. One unified system.
          </h2>
          <p className="text-grey-600 text-base sm:text-lg font-light leading-relaxed">
            Every agent has a defined responsibility, operates with structured Pydantic
            contracts, and contributes to the complete software lifecycle.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {agents.map((agent, i) => {
            const Icon = agent.icon;
            return (
              <div
                key={i}
                className="group relative p-6 bg-white border border-border rounded-lg hover:border-black/40 hover:shadow-[0_4px_20px_rgba(0,0,0,0.04)] transition-all duration-200"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2.5 bg-grey-50 rounded border border-border text-black group-hover:bg-black group-hover:text-white transition-colors">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[11px] font-mono text-grey-400 uppercase tracking-wider">
                    {agent.stage}
                  </span>
                </div>
                <h3 className="text-lg font-medium text-black mb-2 tracking-tight">
                  {agent.role}
                </h3>
                <p className="text-sm text-grey-600 font-light leading-relaxed mb-4">
                  {agent.description}
                </p>
                <div className="pt-3 border-t border-border flex items-center justify-between text-xs font-mono text-grey-500">
                  <span>Artifact</span>
                  <span className="text-black bg-grey-100 px-2 py-0.5 rounded text-[11px]">
                    {agent.output}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
