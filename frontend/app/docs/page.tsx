"use client";

import Link from "next/link";
import Sidebar from "../../components/dashboard/Sidebar";
import { ArrowLeft, BookOpen, Terminal, Layers, ShieldCheck, GitBranch } from "lucide-react";

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-white flex">
      <Sidebar />

      <main className="flex-1 overflow-y-auto">
        <header className="h-16 border-b border-border px-8 flex items-center justify-between sticky top-0 bg-white/90 backdrop-blur-md z-10">
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="p-1.5 text-grey-500 hover:text-black rounded hover:bg-grey-100 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <h1 className="text-sm font-medium text-black">Platform Documentation</h1>
          </div>
        </header>

        <div className="p-8 max-w-4xl mx-auto space-y-12">
          {/* Header */}
          <div>
            <div className="text-xs font-mono text-grey-500 tracking-wider uppercase mb-2">
              ARCHITECTURE & API GUIDE
            </div>
            <h1 className="font-serif text-4xl font-normal text-black mb-4">
              Orchestrix Engineering Documentation
            </h1>
            <p className="text-base text-grey-600 font-light leading-relaxed">
              Orchestrix is an autonomous AI software engineering platform that designs,
              plans, writes, tests, and self-heals fullstack web applications.
            </p>
          </div>

          {/* Section 1: System Overview */}
          <section className="space-y-4">
            <h2 className="font-serif text-2xl font-normal text-black flex items-center gap-2">
              <Layers className="w-5 h-5 text-black" />
              <span>Core Architectural Pipeline</span>
            </h2>
            <p className="text-sm text-grey-700 font-light leading-relaxed">
              Unlike conversational chatbots, Orchestrix uses deterministic graph algorithms
              and isolated sandboxes alongside specialized LLMs:
            </p>
            <div className="p-4 bg-grey-50 border border-border rounded-lg font-mono text-xs text-grey-800 space-y-1">
              <div>1. Requirement Analyzer $\rightarrow$ Synthesizes Pydantic specifications.</div>
              <div>2. Architect Agent $\rightarrow$ Designs entities, database schemas, and REST contracts.</div>
              <div>3. Planner Agent $\rightarrow$ Solves dependency ordering via Kahn's algorithm.</div>
              <div>4. Developer Agents $\rightarrow$ Produce modular backend & frontend source trees.</div>
              <div>5. Docker / Process Sandbox $\rightarrow$ Executes test suites with resource limits.</div>
              <div>6. Debugger Agent $\rightarrow$ Diagnoses root causes and self-heals code.</div>
            </div>
          </section>

          {/* Section 2: REST APIs */}
          <section className="space-y-4">
            <h2 className="font-serif text-2xl font-normal text-black flex items-center gap-2">
              <Terminal className="w-5 h-5 text-black" />
              <span>Key REST API Endpoints</span>
            </h2>
            <div className="space-y-3 font-mono text-xs">
              <div className="p-3 bg-white border border-border rounded-lg flex items-center justify-between">
                <div>
                  <span className="font-bold bg-black text-white px-1.5 py-0.5 rounded mr-2">POST</span>
                  <span className="text-black">/api/projects</span>
                </div>
                <span className="text-grey-500 font-sans text-xs">Create new project</span>
              </div>
              <div className="p-3 bg-white border border-border rounded-lg flex items-center justify-between">
                <div>
                  <span className="font-bold bg-black text-white px-1.5 py-0.5 rounded mr-2">POST</span>
                  <span className="text-black">/api/projects/&#123;id&#125;/analyze</span>
                </div>
                <span className="text-grey-500 font-sans text-xs">Trigger Requirement Analyzer</span>
              </div>
              <div className="p-3 bg-white border border-border rounded-lg flex items-center justify-between">
                <div>
                  <span className="font-bold bg-black text-white px-1.5 py-0.5 rounded mr-2">POST</span>
                  <span className="text-black">/api/projects/&#123;id&#125;/architect</span>
                </div>
                <span className="text-grey-500 font-sans text-xs">Generate system architecture</span>
              </div>
              <div className="p-3 bg-white border border-border rounded-lg flex items-center justify-between">
                <div>
                  <span className="font-bold bg-black text-white px-1.5 py-0.5 rounded mr-2">POST</span>
                  <span className="text-black">/api/projects/&#123;id&#125;/plan</span>
                </div>
                <span className="text-grey-500 font-sans text-xs">Compute DAG execution waves</span>
              </div>
              <div className="p-3 bg-white border border-border rounded-lg flex items-center justify-between">
                <div>
                  <span className="font-bold bg-black text-white px-1.5 py-0.5 rounded mr-2">POST</span>
                  <span className="text-black">/api/projects/&#123;id&#125;/generate</span>
                </div>
                <span className="text-grey-500 font-sans text-xs">Run multi-agent code generation</span>
              </div>
              <div className="p-3 bg-white border border-border rounded-lg flex items-center justify-between">
                <div>
                  <span className="font-bold bg-black text-white px-1.5 py-0.5 rounded mr-2">POST</span>
                  <span className="text-black">/api/projects/&#123;id&#125;/execute</span>
                </div>
                <span className="text-grey-500 font-sans text-xs">Run sandboxed tests & self-healing</span>
              </div>
              <div className="p-3 bg-white border border-border rounded-lg flex items-center justify-between">
                <div>
                  <span className="font-bold bg-black text-white px-1.5 py-0.5 rounded mr-2">GET</span>
                  <span className="text-black">/api/projects/&#123;id&#125;/export</span>
                </div>
                <span className="text-grey-500 font-sans text-xs">Export workspace as ZIP archive</span>
              </div>
            </div>
          </section>

          {/* Section 3: Verification */}
          <section className="space-y-4">
            <h2 className="font-serif text-2xl font-normal text-black flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-black" />
              <span>Sandbox Isolation Boundaries</span>
            </h2>
            <p className="text-sm text-grey-700 font-light leading-relaxed">
              Orchestrix implements a dual-mode sandbox runner. In environments with an active
              Docker daemon, test suites run in isolated Python containers limited to 1 CPU core
              and 512MB RAM. In development or local environments without a Docker daemon,
              the engine falls back to isolated local process execution with scrubbed environment
              variables, path traversal protection, and strict execution timeouts.
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}
