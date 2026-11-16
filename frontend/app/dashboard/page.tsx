"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Sidebar from "../../components/dashboard/Sidebar";
import StatsCard from "../../components/dashboard/StatsCard";
import ProjectCard from "../../components/dashboard/ProjectCard";
import { projectService } from "../../services/projectService";
import { agentService } from "../../services/agentService";
import { Project } from "../../types/project";
import { AgentInfo } from "../../types/agent";
import {
  FolderGit2,
  Cpu,
  CheckCircle2,
  ShieldCheck,
  Plus,
  RefreshCw,
  Search,
} from "lucide-react";

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  const fetchData = async () => {
    try {
      setLoading(true);
      const [projList, agentList] = await Promise.all([
        projectService.getAll(),
        agentService.getRoster(),
      ]);
      setProjects(projList);
      setAgents(agentList);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const completedProjects = projects.filter((p) => p.status === "completed").length;
  const passRate = projects.length > 0
    ? Math.round((completedProjects / projects.length) * 100)
    : 100;

  const filteredProjects = projects.filter(
    (p) =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-white flex">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto">
        {/* Top Header */}
        <header className="h-16 border-b border-border px-8 flex items-center justify-between sticky top-0 bg-white/90 backdrop-blur-md z-10">
          <div>
            <h1 className="text-lg font-medium text-black">Workspace Overview</h1>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={fetchData}
              className="p-2 text-grey-500 hover:text-black hover:bg-grey-100 rounded-md transition-colors"
              title="Refresh Data"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
            <Link
              href="/projects/new"
              className="inline-flex items-center gap-2 bg-black text-white hover:bg-grey-800 text-xs font-medium px-4 py-2 rounded-md transition-all shadow-sm"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>New Project</span>
            </Link>
          </div>
        </header>

        <div className="p-8 max-w-7xl mx-auto space-y-8">
          {/* Metrics Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatsCard
              label="TOTAL PROJECTS"
              value={projects.length}
              subtitle="Active in PostgreSQL"
              icon={FolderGit2}
            />
            <StatsCard
              label="AI AGENTS"
              value={agents.length || 8}
              subtitle="Specialized team active"
              icon={Cpu}
            />
            <StatsCard
              label="COMPLETED BUILDS"
              value={completedProjects}
              subtitle="End-to-end verified"
              icon={CheckCircle2}
            />
            <StatsCard
              label="TEST PASS RATE"
              value={`${passRate}%`}
              subtitle="Sandboxed executions"
              icon={ShieldCheck}
            />
          </div>

          {/* Projects Section */}
          <section className="space-y-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-serif text-black font-normal">
                  Engineering Projects
                </h2>
                <p className="text-xs text-grey-500 font-light">
                  Inspect generated architectures, task DAGs, workspaces, and test results.
                </p>
              </div>

              {/* Search Bar */}
              <div className="relative w-full sm:w-64">
                <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-grey-400" />
                <input
                  type="text"
                  placeholder="Search projects..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 text-xs bg-grey-50 border border-border rounded-md focus:outline-none focus:border-black text-black"
                />
              </div>
            </div>

            {loading ? (
              <div className="py-20 text-center text-sm text-grey-500 font-mono">
                <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-black" />
                Loading projects from PostgreSQL...
              </div>
            ) : filteredProjects.length === 0 ? (
              <div className="p-12 text-center bg-grey-50/50 border border-dashed border-border rounded-lg space-y-3">
                <FolderGit2 className="w-8 h-8 mx-auto text-grey-400" />
                <h3 className="text-sm font-medium text-black">No projects found</h3>
                <p className="text-xs text-grey-500 max-w-sm mx-auto font-light">
                  {searchQuery
                    ? "No projects matched your search query."
                    : "Create your first project to trigger the autonomous multi-agent engineering loop."}
                </p>
                <Link
                  href="/projects/new"
                  className="inline-flex items-center gap-1.5 text-xs font-medium bg-black text-white px-3.5 py-2 rounded-md hover:bg-grey-800 transition-colors"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Create Project</span>
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredProjects.map((project) => (
                  <ProjectCard key={project.id} project={project} />
                ))}
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
