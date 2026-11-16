"use client";

import { useMemo } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  Node,
  Edge,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { DAGResponse, Task } from "../../types/project";
import { GitBranch, User, CheckCircle2, Clock, AlertCircle } from "lucide-react";

interface DAGViewerProps {
  dag: DAGResponse;
}

export default function DAGViewer({ dag }: DAGViewerProps) {
  const { nodes, edges } = useMemo(() => {
    const computedNodes: Node[] = [];
    const computedEdges: Edge[] = [];

    const tasks = dag.tasks || [];
    const taskKeyMap = new Map<string, Task>();
    tasks.forEach((t) => taskKeyMap.set(t.task_key, t));

    // Group tasks by wave
    const waveGroups: Record<number, Task[]> = {};
    tasks.forEach((t) => {
      const w = t.wave || 1;
      if (!waveGroups[w]) waveGroups[w] = [];
      waveGroups[w].push(t);
    });

    Object.entries(waveGroups).forEach(([waveStr, waveTasks]) => {
      const wave = parseInt(waveStr, 10);
      waveTasks.forEach((task, idx) => {
        const xPos = (wave - 1) * 320 + 40;
        const yPos = idx * 140 + 40;

        computedNodes.push({
          id: task.task_key,
          position: { x: xPos, y: yPos },
          data: {
            label: (
              <div className="p-3 bg-white border border-border rounded-lg shadow-sm hover:border-black transition-all text-left w-64">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-mono bg-grey-100 text-grey-800 px-1.5 py-0.5 rounded font-semibold">
                    {task.task_key}
                  </span>
                  <span className="text-[10px] font-mono text-grey-500 uppercase">
                    Wave {task.wave}
                  </span>
                </div>
                <div className="font-medium text-xs text-black line-clamp-1 mb-2">
                  {task.title}
                </div>
                <div className="flex items-center justify-between text-[10px] text-grey-500 pt-1.5 border-t border-border">
                  <span className="flex items-center gap-1 font-mono">
                    <User className="w-3 h-3 text-grey-400" />
                    {task.assigned_agent.replace("_", " ")}
                  </span>
                  <span
                    className={`uppercase font-mono px-1.5 py-0.2 rounded text-[9px] ${
                      task.status === "completed"
                        ? "bg-emerald-50 text-emerald-700"
                        : "bg-grey-100 text-grey-600"
                    }`}
                  >
                    {task.status}
                  </span>
                </div>
              </div>
            ),
          },
          style: {
            background: "transparent",
            border: "none",
            padding: 0,
          },
        });

        // Add edges for each dependency
        if (task.dependencies && Array.isArray(task.dependencies)) {
          task.dependencies.forEach((depKey) => {
            computedEdges.push({
              id: `e-${depKey}-${task.task_key}`,
              source: depKey,
              target: task.task_key,
              animated: task.status === "in_progress",
              style: { stroke: "#71717A", strokeWidth: 1.5 },
              markerEnd: {
                type: MarkerType.ArrowClosed,
                color: "#71717A",
                width: 14,
                height: 14,
              },
            });
          });
        }
      });
    });

    return { nodes: computedNodes, edges: computedEdges };
  }, [dag]);

  return (
    <div className="space-y-6">
      {/* DAG Stats Bar */}
      <div className="p-4 bg-grey-50 border border-border rounded-lg flex flex-wrap items-center justify-between gap-4 text-xs font-mono">
        <div className="flex items-center gap-6">
          <span className="flex items-center gap-2">
            <GitBranch className="w-4 h-4 text-black" />
            <span className="text-grey-500">Total Tasks:</span>
            <span className="font-bold text-black">{dag.tasks.length}</span>
          </span>
          <span className="flex items-center gap-2">
            <span className="text-grey-500">Execution Waves:</span>
            <span className="font-bold text-black">{dag.total_waves}</span>
          </span>
          <span className="flex items-center gap-2">
            <span className="text-grey-500">Cycles Detected:</span>
            <span
              className={`font-bold ${
                dag.has_cycle ? "text-red-600" : "text-emerald-600"
              }`}
            >
              {dag.has_cycle ? "YES (Cycle Found)" : "0 (Acyclic DAG Verified)"}
            </span>
          </span>
        </div>
        <div className="text-[11px] text-grey-500">
          Kahn's Topological Sort Engine Active
        </div>
      </div>

      {/* React Flow Interactive Graph */}
      <div className="h-[460px] w-full border border-border rounded-xl bg-white overflow-hidden shadow-sm relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView
          minZoom={0.2}
          maxZoom={1.5}
          attributionPosition="bottom-right"
        >
          <Background color="#E4E4E7" gap={20} size={1} />
          <Controls position="top-right" />
          <MiniMap
            nodeColor="#E4E4E7"
            maskColor="rgba(255, 255, 255, 0.8)"
            style={{ height: 100, width: 140 }}
          />
        </ReactFlow>
      </div>

      {/* Wave Breakdown Table */}
      <div className="space-y-3 pt-4">
        <h4 className="text-xs font-mono uppercase tracking-wider text-grey-600">
          Topological Wave Sequencing
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(dag.waves).map(([waveNum, waveTasks]) => (
            <div
              key={waveNum}
              className="p-4 bg-white border border-border rounded-lg text-xs"
            >
              <div className="font-mono text-[11px] font-semibold text-black pb-2 mb-2 border-b border-border flex items-center justify-between">
                <span>WAVE {waveNum}</span>
                <span className="text-grey-500 font-normal">
                  {waveTasks.length} {waveTasks.length === 1 ? "task" : "tasks"}
                </span>
              </div>
              <ul className="space-y-2">
                {waveTasks.map((t) => (
                  <li key={t.task_key} className="flex items-start gap-2">
                    <span className="font-mono text-[10px] text-grey-400 mt-0.5">
                      {t.task_key}
                    </span>
                    <span className="text-grey-800 line-clamp-1 flex-1">
                      {t.title}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
