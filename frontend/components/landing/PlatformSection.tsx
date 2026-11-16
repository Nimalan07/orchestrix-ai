"use client";

import { Code2, GitFork, ShieldAlert, Cpu, Terminal, FileCode } from "lucide-react";

export default function PlatformSection() {
  return (
    <section id="features" className="py-24 bg-white border-b border-border">
      <div className="max-w-7xl mx-auto px-6">
        <div className="max-w-3xl mx-auto text-center mb-20">
          <div className="text-xs font-mono text-grey-500 tracking-widest uppercase mb-3">
            PLATFORM CAPABILITIES
          </div>
          <h2 className="font-serif text-3xl sm:text-4xl md:text-5xl font-normal text-black mb-4">
            Built for enterprise-grade autonomous delivery.
          </h2>
          <p className="text-grey-600 text-base sm:text-lg font-light leading-relaxed">
            Every layer from requirement parsing to sandboxed execution is engineered
            with deterministic guarantees and strict isolation.
          </p>
        </div>

        {/* Feature 01 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-24 pb-20 border-b border-border">
          <div>
            <div className="text-xs font-mono text-grey-500 tracking-wider mb-2">
              01 // INTELLIGENT PLANNING
            </div>
            <h3 className="font-serif text-3xl font-normal text-black mb-4">
              Deterministic DAGs, not hallucinated dependencies.
            </h3>
            <p className="text-grey-600 text-base font-light leading-relaxed mb-6">
              Orchestrix converts high-level requirements into formal specifications,
              database schemas, and typed API contracts. The planner computes topological
              execution waves via Kahn’s algorithm, guaranteeing zero dependency deadlocks.
            </p>
            <ul className="space-y-3 text-sm text-grey-700">
              <li className="flex items-center gap-2.5">
                <span className="w-1.5 h-1.5 rounded-full bg-black" />
                Automatic cycle path tracing and topological parallel wave batching
              </li>
              <li className="flex items-center gap-2.5">
                <span className="w-1.5 h-1.5 rounded-full bg-black" />
                OpenAPI-compatible contracts and SQLAlchemy entity schemas
              </li>
              <li className="flex items-center gap-2.5">
                <span className="w-1.5 h-1.5 rounded-full bg-black" />
                Pydantic v2 structured validation with iterative JSON self-repair
              </li>
            </ul>
          </div>
          <div className="bg-grey-50 border border-border rounded-xl p-6 font-mono text-xs text-grey-800 shadow-sm overflow-x-auto">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-border text-grey-500">
              <span className="flex items-center gap-2">
                <GitFork className="w-4 h-4 text-black" />
                <span>dag_planner.json</span>
              </span>
              <span className="text-[10px] bg-grey-200 px-2 py-0.5 rounded text-black font-semibold">
                6 WAVES COMPUTED
              </span>
            </div>
            <pre className="text-grey-700 leading-relaxed">
{`{
  "total_waves": 6,
  "has_cycle": false,
  "waves": {
    "1": ["TASK-001: Init DB Models (DB Engineer)"],
    "2": ["TASK-002: Student CRUD (Backend Dev)"],
    "3": ["TASK-003: Attendance Logic (Backend Dev)"],
    "4": ["TASK-004: Frontend Types (Frontend Dev)"],
    "5": ["TASK-005: Student Page (Frontend Dev)"],
    "6": ["TASK-006: Integration Test Suite (Tester)"]
  }
}`}
            </pre>
          </div>
        </div>

        {/* Feature 02 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-24 pb-20 border-b border-border">
          <div className="order-2 lg:order-1 bg-grey-900 text-grey-100 rounded-xl p-6 font-mono text-xs shadow-sm overflow-x-auto">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-grey-800 text-grey-400">
              <span className="flex items-center gap-2">
                <FileCode className="w-4 h-4 text-emerald-400" />
                <span>workspace_artifacts.log</span>
              </span>
              <span className="text-[10px] bg-grey-800 px-2 py-0.5 rounded text-emerald-300">
                SHA-256 VERIFIED
              </span>
            </div>
            <pre className="text-grey-300 leading-relaxed">
{`[INFO] Writing: backend/app/models/student.py (1.2 KB)
[SHA256] 9f82d... -> Persisted to PostgreSQL
[INFO] Writing: backend/app/api/students.py (2.4 KB)
[SHA256] 4a11b... -> Persisted to PostgreSQL
[INFO] Scaffolding: backend/Dockerfile (Python 3.13-slim)
[INFO] Scaffolding: docker-compose.yml (Multi-tier stack)
[SUCCESS] 23 project artifacts synthesized safely.`}
            </pre>
          </div>
          <div className="order-1 lg:order-2">
            <div className="text-xs font-mono text-grey-500 tracking-wider mb-2">
              02 // CODE GENERATION ENGINE
            </div>
            <h3 className="font-serif text-3xl font-normal text-black mb-4">
              Sandboxed workspaces with cryptographic verification.
            </h3>
            <p className="text-grey-600 text-base font-light leading-relaxed mb-6">
              Developer agents produce complete, modular source trees directly in isolated
              project directories. Every written file is checked for path traversal exploits
              and tracked in PostgreSQL with SHA-256 integrity checksums.
            </p>
            <ul className="space-y-3 text-sm text-grey-700">
              <li className="flex items-center gap-2.5">
                <span className="w-1.5 h-1.5 rounded-full bg-black" />
                Path traversal containment prevents arbitrary host filesystem writes
              </li>
              <li className="flex items-center gap-2.5">
                <span className="w-1.5 h-1.5 rounded-full bg-black" />
                Automated scaffolding: requirements, Dockerfiles, and compose configurations
              </li>
              <li className="flex items-center gap-2.5">
                <span className="w-1.5 h-1.5 rounded-full bg-black" />
                Clean ZIP archive export for instant developer onboarding
              </li>
            </ul>
          </div>
        </div>

        {/* Feature 03 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div>
            <div className="text-xs font-mono text-grey-500 tracking-wider mb-2">
              03 // AUTONOMOUS SELF-HEALING
            </div>
            <h3 className="font-serif text-3xl font-normal text-black mb-4">
              Generate $\rightarrow$ Test $\rightarrow$ Diagnose $\rightarrow$ Repair.
            </h3>
            <p className="text-grey-600 text-base font-light leading-relaxed mb-6">
              When tests fail inside the isolated sandbox, the Debugger Agent reads the full
              stack trace, diagnoses the precise root cause, and generates targeted code
              replacements. The engine re-tests automatically in bounded repair loops.
            </p>
            <ul className="space-y-3 text-sm text-grey-700">
              <li className="flex items-center gap-2.5">
                <span className="w-1.5 h-1.5 rounded-full bg-black" />
                Dual execution engine: Docker containers or local process isolation
              </li>
              <li className="flex items-center gap-2.5">
                <span className="w-1.5 h-1.5 rounded-full bg-black" />
                Bounded to 3 self-healing iterations to prevent unbounded LLM loops
              </li>
              <li className="flex items-center gap-2.5">
                <span className="w-1.5 h-1.5 rounded-full bg-black" />
                Comprehensive diagnostic reports with full pass/fail history
              </li>
            </ul>
          </div>
          <div className="bg-grey-50 border border-border rounded-xl p-6 font-mono text-xs text-grey-800 shadow-sm overflow-x-auto">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-border text-grey-500">
              <span className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-black" />
                <span>self_healing_execution.log</span>
              </span>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-semibold">
                HEALED // 1 ITERATION
              </span>
            </div>
            <pre className="text-grey-700 leading-relaxed">
{`[RUN-01] pytest backend/tests/test_api.py
FAILED: test_students_endpoint (Status 404 != 200)

[DEBUGGER] Root Cause: Missing router registration in main.py
[DEBUGGER] Applying patch to backend/app/main.py...
[DEBUGGER] Recalculated SHA256: e87c2...

[RETEST] pytest backend/tests/test_api.py
================ 2 passed in 1.08s ================
[STATUS] Project marked HEALED & VERIFIED.`}
            </pre>
          </div>
        </div>
      </div>
    </section>
  );
}
