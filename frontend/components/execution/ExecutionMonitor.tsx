"use client";

import { useState, useEffect } from "react";
import { executionService } from "../../services/executionService";
import { ExecutionRun } from "../../types/execution";
import {
  Play,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Terminal,
  ShieldCheck,
  Cpu,
  Clock,
  Layers,
} from "lucide-react";

interface ExecutionMonitorProps {
  projectId: string;
}

export default function ExecutionMonitor({ projectId }: ExecutionMonitorProps) {
  const [runs, setRuns] = useState<ExecutionRun[]>([]);
  const [selectedRun, setSelectedRun] = useState<ExecutionRun | null>(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRuns = async () => {
    try {
      setLoading(true);
      const data = await executionService.getRuns(projectId);
      setRuns(data);
      if (data.length > 0 && !selectedRun) {
        setSelectedRun(data[0]);
      }
    } catch (err: any) {
      console.error("Failed to fetch execution runs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRuns();
  }, [projectId]);

  const handleTriggerExecution = async () => {
    try {
      setExecuting(true);
      setError(null);
      const newRun = await executionService.executeProject(projectId, {
        max_iterations: 3,
        sandbox_mode: "auto",
      });
      setRuns((prev) => [newRun, ...prev]);
      setSelectedRun(newRun);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to execute sandboxed tests."
      );
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Action Bar */}
      <div className="p-4 bg-white border border-border rounded-lg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-medium text-black">
            Sandboxed Verification & Self-Healing
          </h3>
          <p className="text-xs text-grey-500 font-light">
            Runs automated Pytest suites in isolated environments and diagnoses failures.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchRuns}
            className="p-2 text-grey-500 hover:text-black rounded hover:bg-grey-100 transition-colors"
            title="Refresh History"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>

          <button
            onClick={handleTriggerExecution}
            disabled={executing}
            className="inline-flex items-center gap-2 bg-black text-white hover:bg-grey-800 disabled:bg-grey-400 text-xs font-medium px-4 py-2 rounded-md transition-all shadow-sm"
          >
            {executing ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Running Sandbox & Self-Healing...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Run Sandbox Tests</span>
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 text-xs rounded-md">
          {error}
        </div>
      )}

      {loading && runs.length === 0 ? (
        <div className="py-16 text-center text-xs font-mono text-grey-500">
          <RefreshCw className="w-4 h-4 animate-spin mx-auto mb-2 text-black" />
          Loading execution records...
        </div>
      ) : runs.length === 0 ? (
        <div className="p-12 text-center bg-grey-50 border border-dashed border-border rounded-lg space-y-3">
          <Terminal className="w-8 h-8 mx-auto text-grey-400" />
          <h4 className="text-sm font-medium text-black">No executions recorded yet</h4>
          <p className="text-xs text-grey-500 max-w-sm mx-auto font-light">
            Launch your first sandboxed test run to verify the generated backend and test the
            autonomous self-healing loop.
          </p>
          <button
            onClick={handleTriggerExecution}
            disabled={executing}
            className="inline-flex items-center gap-1.5 text-xs font-medium bg-black text-white px-3.5 py-2 rounded-md hover:bg-grey-800 transition-colors"
          >
            <Play className="w-3 h-3 fill-current" />
            <span>Start Test Run</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Execution History List */}
          <div className="lg:col-span-1 space-y-2">
            <div className="text-xs font-mono uppercase text-grey-500 tracking-wider mb-2">
              Run History ({runs.length})
            </div>
            <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
              {runs.map((run) => (
                <button
                  key={run.id}
                  onClick={() => setSelectedRun(run)}
                  className={`w-full text-left p-3.5 rounded-lg border text-xs transition-all ${
                    selectedRun?.id === run.id
                      ? "bg-black text-white border-black shadow-sm"
                      : "bg-white text-grey-800 border-border hover:border-grey-400"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-mono text-[10px] uppercase font-semibold">
                      {run.sandbox_mode}
                    </span>
                    <span
                      className={`text-[9px] font-mono uppercase px-1.5 py-0.5 rounded ${
                        run.status === "passed" || run.status === "healed"
                          ? selectedRun?.id === run.id
                            ? "bg-emerald-500 text-white"
                            : "bg-emerald-50 text-emerald-700"
                          : selectedRun?.id === run.id
                          ? "bg-red-500 text-white"
                          : "bg-red-50 text-red-700"
                      }`}
                    >
                      {run.status}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] opacity-80 mb-1">
                    <span>
                      {run.passed_tests}/{run.total_tests} Tests Passed
                    </span>
                    <span>{run.duration_seconds.toFixed(2)}s</span>
                  </div>
                  <div className="text-[10px] opacity-60 font-mono">
                    {new Date(run.created_at).toLocaleTimeString()} •{" "}
                    {run.iterations} healing {run.iterations === 1 ? "loop" : "loops"}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Selected Run Details */}
          {selectedRun && (
            <div className="lg:col-span-2 space-y-4">
              {/* Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                <div className="p-3 bg-white border border-border rounded-lg">
                  <div className="text-grey-500 text-[10px] mb-1">STATUS</div>
                  <div className="font-bold text-black uppercase">
                    {selectedRun.status}
                  </div>
                </div>
                <div className="p-3 bg-white border border-border rounded-lg">
                  <div className="text-grey-500 text-[10px] mb-1">TESTS PASSED</div>
                  <div className="font-bold text-emerald-600">
                    {selectedRun.passed_tests} / {selectedRun.total_tests}
                  </div>
                </div>
                <div className="p-3 bg-white border border-border rounded-lg">
                  <div className="text-grey-500 text-[10px] mb-1">HEALING LOOPS</div>
                  <div className="font-bold text-black">
                    {selectedRun.iterations} (max 3)
                  </div>
                </div>
                <div className="p-3 bg-white border border-border rounded-lg">
                  <div className="text-grey-500 text-[10px] mb-1">DURATION</div>
                  <div className="font-bold text-black">
                    {selectedRun.duration_seconds.toFixed(2)}s
                  </div>
                </div>
              </div>

              {/* Diagnostic / Self-Healing Report */}
              {selectedRun.diagnostic_report && (
                <div className="p-4 bg-grey-50 border border-border rounded-lg text-xs space-y-2">
                  <div className="font-mono text-[11px] uppercase text-grey-500 font-semibold flex items-center justify-between">
                    <span>Diagnostic & Self-Healing Analysis</span>
                    <span className="text-black">
                      Mode: {selectedRun.sandbox_mode}
                    </span>
                  </div>
                  <div className="text-grey-700 leading-relaxed font-light">
                    {selectedRun.status === "passed" && selectedRun.iterations === 0 && (
                      <span className="text-emerald-700">
                        Initial automated test suite passed cleanly with 100% assertions satisfied on the baseline run.
                      </span>
                    )}
                    {selectedRun.status === "healed" && (
                      <span className="text-emerald-700 font-medium">
                        Autonomous debugger successfully diagnosed failure and applied verified code repairs in {selectedRun.iterations} iteration(s).
                      </span>
                    )}
                    {selectedRun.status === "failed" && (
                      <span className="text-red-700">
                        Execution encountered failures that exceeded the bounded 3-iteration self-healing threshold. Human review advised.
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Terminal Logs */}
              <div className="bg-grey-900 text-grey-100 rounded-xl p-4 font-mono text-xs overflow-hidden shadow-sm">
                <div className="flex items-center justify-between pb-3 mb-3 border-b border-grey-800 text-grey-400">
                  <span className="flex items-center gap-2">
                    <Terminal className="w-3.5 h-3.5 text-emerald-400" />
                    <span>stdout / execution.log</span>
                  </span>
                  <span className="text-[10px] text-grey-500">
                    ID: {selectedRun.id.slice(0, 8)}...
                  </span>
                </div>
                <pre className="text-grey-300 leading-relaxed whitespace-pre-wrap max-h-80 overflow-y-auto">
                  {selectedRun.stdout || "No standard output recorded."}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
