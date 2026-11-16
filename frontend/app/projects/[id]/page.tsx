"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import Sidebar from "../../../components/dashboard/Sidebar";
import DAGViewer from "../../../components/workflow/DAGViewer";
import FileExplorer from "../../../components/files/FileExplorer";
import ExecutionMonitor from "../../../components/execution/ExecutionMonitor";
import { projectService } from "../../../services/projectService";
import {
  Project,
  RequirementSpecification,
  SystemArchitecture,
  DAGResponse,
} from "../../../types/project";
import {
  ArrowLeft,
  Sparkles,
  Download,
  CheckCircle2,
  AlertCircle,
  FileSearch,
  Layers,
  GitBranch,
  Code2,
  Play,
  RefreshCw,
  Database,
  Server,
  FileCode,
  ShieldCheck,
  ChevronRight,
} from "lucide-react";

export default function ProjectWorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [requirements, setRequirements] = useState<RequirementSpecification | null>(null);
  const [architecture, setArchitecture] = useState<SystemArchitecture | null>(null);
  const [dag, setDAG] = useState<DAGResponse | null>(null);
  const [activeTab, setActiveTab] = useState<
    "overview" | "requirements" | "architecture" | "tasks" | "files" | "executions"
  >("overview");

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchProjectData = async () => {
    try {
      setLoading(true);
      setError(null);
      const proj = await projectService.getById(projectId);
      setProject(proj);

      const [reqs, arch, taskDag] = await Promise.all([
        projectService.getRequirements(projectId),
        projectService.getArchitecture(projectId),
        projectService.getDAG(projectId),
      ]);

      setRequirements(reqs);
      setArchitecture(arch);
      setDAG(taskDag);
    } catch (err: any) {
      console.error("Failed to load project details:", err);
      setError(err.response?.data?.detail || err.message || "Failed to load project.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (projectId) {
      fetchProjectData();
    }
  }, [projectId]);

  // Stage Trigger Handlers
  const handleAnalyze = async () => {
    try {
      setActionLoading(true);
      setStatusMsg("Requirement Analyzer Agent is synthesizing specifications...");
      await projectService.analyzeRequirements(projectId);
      await fetchProjectData();
      setActiveTab("requirements");
      setStatusMsg(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Requirement analysis failed.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleArchitect = async () => {
    try {
      setActionLoading(true);
      setStatusMsg("Architect Agent is designing system entities and API contracts...");
      await projectService.generateArchitecture(projectId);
      await fetchProjectData();
      setActiveTab("architecture");
      setStatusMsg(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Architecture generation failed.");
    } finally {
      setActionLoading(false);
    }
  };

  const handlePlan = async () => {
    try {
      setActionLoading(true);
      setStatusMsg("Planner Agent is computing topological DAG waves via Kahn's algorithm...");
      await projectService.planTasks(projectId);
      await fetchProjectData();
      setActiveTab("tasks");
      setStatusMsg(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Task planning failed.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleGenerateCode = async () => {
    try {
      setActionLoading(true);
      setStatusMsg("Developer agents are generating source files & runtime scaffolding...");
      await projectService.generateCode(projectId);
      await fetchProjectData();
      setActiveTab("files");
      setStatusMsg(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Code generation failed.");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading && !project) {
    return (
      <div className="min-h-screen bg-white flex">
        <Sidebar />
        <main className="flex-1 flex items-center justify-center font-mono text-xs text-grey-500">
          <RefreshCw className="w-5 h-5 animate-spin mr-2 text-black" />
          Loading project workspace...
        </main>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-white flex">
        <Sidebar />
        <main className="flex-1 p-12 text-center text-sm text-grey-600">
          Project not found.{" "}
          <Link href="/dashboard" className="text-black underline">
            Return to Dashboard
          </Link>
        </main>
      </div>
    );
  }

  // Pipeline stages calculation
  const stages = [
    { name: "Requirements", ready: !!requirements, action: handleAnalyze },
    { name: "Architecture", ready: !!architecture, action: handleArchitect },
    { name: "Task DAG", ready: !!dag, action: handlePlan },
    { name: "Code Generation", ready: project.status === "completed", action: handleGenerateCode },
  ];

  return (
    <div className="min-h-screen bg-white flex">
      <Sidebar />

      <main className="flex-1 overflow-y-auto">
        {/* Top Header */}
        <header className="h-16 border-b border-border px-8 flex items-center justify-between sticky top-0 bg-white/90 backdrop-blur-md z-10">
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="p-1.5 text-grey-500 hover:text-black rounded hover:bg-grey-100 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div>
              <h1 className="text-sm font-semibold text-black tracking-tight flex items-center gap-2">
                <span>{project.name}</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full border border-border bg-grey-50 uppercase text-grey-600">
                  {project.status}
                </span>
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchProjectData}
              className="p-2 text-grey-500 hover:text-black rounded hover:bg-grey-100 transition-colors"
              title="Refresh Workspace"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>

            <a
              href={projectService.getExportUrl(project.id)}
              download
              className="inline-flex items-center gap-1.5 bg-white border border-border text-grey-800 hover:bg-grey-50 text-xs font-medium px-3.5 py-1.5 rounded-md transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export ZIP</span>
            </a>
          </div>
        </header>

        {/* Status / Loading Notification Bar */}
        {actionLoading && statusMsg && (
          <div className="bg-black text-white px-8 py-2.5 text-xs font-mono flex items-center gap-2 animate-pulse">
            <RefreshCw className="w-3.5 h-3.5 animate-spin text-white" />
            <span>{statusMsg}</span>
          </div>
        )}

        {error && (
          <div className="mx-8 mt-6 p-4 bg-red-50 border border-red-200 text-red-700 text-xs rounded-md">
            {error}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="border-b border-border px-8 bg-grey-50/50">
          <nav className="flex space-x-8 text-xs font-medium">
            {[
              { id: "overview", label: "Overview" },
              { id: "requirements", label: "Requirements" },
              { id: "architecture", label: "Architecture" },
              { id: "tasks", label: "Task DAG" },
              { id: "files", label: "Workspace Files" },
              { id: "executions", label: "Executions & QA" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-3.5 border-b-2 font-mono uppercase tracking-wider transition-colors ${
                  activeTab === tab.id
                    ? "border-black text-black font-bold"
                    : "border-transparent text-grey-500 hover:text-black"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content Body */}
        <div className="p-8 max-w-7xl mx-auto">
          {/* TAB 1: OVERVIEW */}
          {activeTab === "overview" && (
            <div className="space-y-8">
              {/* Project Card */}
              <div className="p-6 bg-white border border-border rounded-lg shadow-sm space-y-4">
                <div className="text-xs font-mono text-grey-400 uppercase tracking-widest">
                  PROJECT SPECIFICATION
                </div>
                <h2 className="font-serif text-2xl font-normal text-black">
                  {project.name}
                </h2>
                <p className="text-sm text-grey-700 font-light leading-relaxed">
                  {project.description}
                </p>
                <div className="pt-4 border-t border-border flex flex-wrap gap-6 text-xs font-mono text-grey-500">
                  <div>
                    <span className="text-grey-400">ID: </span>
                    <span className="text-black">{project.id}</span>
                  </div>
                  <div>
                    <span className="text-grey-400">Created: </span>
                    <span className="text-black">
                      {new Date(project.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-grey-400">Status: </span>
                    <span className="text-black uppercase font-semibold">
                      {project.status}
                    </span>
                  </div>
                </div>
              </div>

              {/* Engineering Pipeline Stages */}
              <div className="space-y-4">
                <h3 className="text-xs font-mono uppercase text-grey-500 tracking-wider">
                  Engineering Pipeline Lifecycle
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {stages.map((stage, idx) => (
                    <div
                      key={stage.name}
                      className="p-5 bg-white border border-border rounded-lg space-y-3"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-mono text-grey-400">
                          STAGE 0{idx + 1}
                        </span>
                        {stage.ready ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        ) : (
                          <span className="w-2 h-2 rounded-full bg-grey-300" />
                        )}
                      </div>
                      <div className="font-medium text-sm text-black">
                        {stage.name}
                      </div>
                      <button
                        onClick={stage.action}
                        disabled={actionLoading}
                        className={`w-full py-1.5 px-3 rounded text-xs font-mono transition-colors ${
                          stage.ready
                            ? "bg-grey-100 hover:bg-grey-200 text-grey-700"
                            : "bg-black hover:bg-grey-800 text-white"
                        }`}
                      >
                        {stage.ready ? "Re-Run Stage" : "Execute Stage"}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: REQUIREMENTS */}
          {activeTab === "requirements" && (
            <div className="space-y-6">
              {!requirements ? (
                <div className="p-12 text-center bg-grey-50 border border-dashed border-border rounded-lg space-y-3">
                  <FileSearch className="w-8 h-8 mx-auto text-grey-400" />
                  <h4 className="text-sm font-medium text-black">Requirements not analyzed yet</h4>
                  <p className="text-xs text-grey-500 max-w-sm mx-auto font-light">
                    Run the Requirement Analyzer Agent to parse the user prompt into formal specifications.
                  </p>
                  <button
                    onClick={handleAnalyze}
                    disabled={actionLoading}
                    className="inline-flex items-center gap-1.5 text-xs font-medium bg-black text-white px-4 py-2 rounded-md hover:bg-grey-800 transition-colors"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Run Requirement Analyzer</span>
                  </button>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Overview */}
                  <div className="p-6 bg-white border border-border rounded-lg space-y-2">
                    <h3 className="text-xs font-mono uppercase tracking-wider text-grey-500">
                      Project Overview
                    </h3>
                    <p className="text-sm text-grey-800 font-light leading-relaxed">
                      {requirements.project_overview}
                    </p>
                  </div>

                  {/* Functional Requirements */}
                  <div className="p-6 bg-white border border-border rounded-lg space-y-4">
                    <h3 className="text-xs font-mono uppercase tracking-wider text-grey-500">
                      Functional Requirements ({requirements.functional_requirements.length})
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {requirements.functional_requirements.map((fr) => (
                        <div key={fr.id} className="p-4 bg-grey-50 rounded-lg border border-border text-xs space-y-1">
                          <div className="flex items-center justify-between font-mono font-semibold text-black">
                            <span>{fr.id}</span>
                            <span className="text-[10px] uppercase bg-grey-200 px-1.5 py-0.5 rounded">
                              {fr.priority}
                            </span>
                          </div>
                          <div className="font-medium text-black">{fr.title}</div>
                          <div className="text-grey-600 font-light leading-relaxed">{fr.description}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Non-Functional & Acceptance Criteria */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="p-6 bg-white border border-border rounded-lg space-y-3">
                      <h3 className="text-xs font-mono uppercase tracking-wider text-grey-500">
                        Technical Constraints & Roles
                      </h3>
                      <ul className="space-y-2 text-xs text-grey-700">
                        {requirements.technical_constraints?.map((tc, i) => (
                          <li key={i} className="flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-black shrink-0" />
                            <span>{tc}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="p-6 bg-white border border-border rounded-lg space-y-3">
                      <h3 className="text-xs font-mono uppercase tracking-wider text-grey-500">
                        Acceptance Criteria
                      </h3>
                      <ul className="space-y-2 text-xs text-grey-700">
                        {requirements.acceptance_criteria?.map((ac, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <CheckCircle2 className="w-3.5 h-3.5 text-black shrink-0 mt-0.5" />
                            <span>{ac.criterion}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: ARCHITECTURE */}
          {activeTab === "architecture" && (
            <div className="space-y-6">
              {!architecture ? (
                <div className="p-12 text-center bg-grey-50 border border-dashed border-border rounded-lg space-y-3">
                  <Layers className="w-8 h-8 mx-auto text-grey-400" />
                  <h4 className="text-sm font-medium text-black">Architecture not designed yet</h4>
                  <p className="text-xs text-grey-500 max-w-sm mx-auto font-light">
                    Run the Architect Agent to design components, data entities, and typed REST API contracts.
                  </p>
                  <button
                    onClick={handleArchitect}
                    disabled={actionLoading}
                    className="inline-flex items-center gap-1.5 text-xs font-medium bg-black text-white px-4 py-2 rounded-md hover:bg-grey-800 transition-colors"
                  >
                    <Layers className="w-3.5 h-3.5" />
                    <span>Generate Architecture</span>
                  </button>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Tech Stack Banner */}
                  <div className="p-6 bg-white border border-border rounded-lg space-y-3">
                    <h3 className="text-xs font-mono uppercase tracking-wider text-grey-500">
                      Approved Technology Stack
                    </h3>
                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs font-mono">
                      <div className="p-3 bg-grey-50 rounded border border-border">
                        <div className="text-grey-400 text-[10px]">BACKEND</div>
                        <div className="font-semibold text-black">{architecture.tech_stack.backend}</div>
                      </div>
                      <div className="p-3 bg-grey-50 rounded border border-border">
                        <div className="text-grey-400 text-[10px]">FRONTEND</div>
                        <div className="font-semibold text-black">{architecture.tech_stack.frontend}</div>
                      </div>
                      <div className="p-3 bg-grey-50 rounded border border-border">
                        <div className="text-grey-400 text-[10px]">DATABASE</div>
                        <div className="font-semibold text-black">{architecture.tech_stack.database}</div>
                      </div>
                      <div className="p-3 bg-grey-50 rounded border border-border">
                        <div className="text-grey-400 text-[10px]">ORM</div>
                        <div className="font-semibold text-black">{architecture.tech_stack.orm}</div>
                      </div>
                      <div className="p-3 bg-grey-50 rounded border border-border">
                        <div className="text-grey-400 text-[10px]">AUTH</div>
                        <div className="font-semibold text-black">{architecture.tech_stack.authentication}</div>
                      </div>
                    </div>
                  </div>

                  {/* Entities & API Contracts */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Entities */}
                    <div className="p-6 bg-white border border-border rounded-lg space-y-4">
                      <h3 className="text-xs font-mono uppercase tracking-wider text-grey-500">
                        Data Entities & Schemas
                      </h3>
                      <div className="space-y-3">
                        {architecture.entities?.map((ent) => (
                          <div key={ent.name} className="p-3.5 bg-grey-50 rounded border border-border text-xs">
                            <div className="font-mono font-bold text-black mb-2 flex items-center gap-2">
                              <Database className="w-3.5 h-3.5" />
                              <span>{ent.name}</span>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-grey-600">
                              {ent.fields?.map((f) => (
                                <div key={f.name} className="truncate">
                                  <span className="text-black">{f.name}:</span> {f.type}
                                  {f.primary_key && " (PK)"}
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* API Contracts */}
                    <div className="p-6 bg-white border border-border rounded-lg space-y-4">
                      <h3 className="text-xs font-mono uppercase tracking-wider text-grey-500">
                        REST API Contracts
                      </h3>
                      <div className="space-y-2">
                        {architecture.api_contracts?.map((c, i) => (
                          <div key={i} className="p-3 bg-grey-50 rounded border border-border text-xs font-mono flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-black text-white">
                                {c.method}
                              </span>
                              <span className="text-grey-800">{c.endpoint}</span>
                            </div>
                            <span className="text-grey-500 text-[11px] font-sans truncate max-w-[180px]">
                              {c.summary}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: TASK DAG */}
          {activeTab === "tasks" && (
            <div className="space-y-6">
              {!dag ? (
                <div className="p-12 text-center bg-grey-50 border border-dashed border-border rounded-lg space-y-3">
                  <GitBranch className="w-8 h-8 mx-auto text-grey-400" />
                  <h4 className="text-sm font-medium text-black">Task DAG not generated yet</h4>
                  <p className="text-xs text-grey-500 max-w-sm mx-auto font-light">
                    Run the Planner Agent to decompose architecture into dependency-aware parallel execution waves.
                  </p>
                  <button
                    onClick={handlePlan}
                    disabled={actionLoading}
                    className="inline-flex items-center gap-1.5 text-xs font-medium bg-black text-white px-4 py-2 rounded-md hover:bg-grey-800 transition-colors"
                  >
                    <GitBranch className="w-3.5 h-3.5" />
                    <span>Plan Tasks & Generate DAG</span>
                  </button>
                </div>
              ) : (
                <DAGViewer dag={dag} />
              )}
            </div>
          )}

          {/* TAB 5: FILES */}
          {activeTab === "files" && <FileExplorer projectId={project.id} />}

          {/* TAB 6: EXECUTIONS & QA */}
          {activeTab === "executions" && <ExecutionMonitor projectId={project.id} />}
        </div>
      </main>
    </div>
  );
}
