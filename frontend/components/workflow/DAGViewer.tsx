"use client";

import { useMemo, useEffect } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  Node,
  Edge,
  MarkerType,
  useNodesState,
  useEdgesState,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { DAGResponse, Task } from "../../types/project";
import { GitBranch, User, Move } from "lucide-react";

interface DAGViewerProps {
  dag: DAGResponse;
}

export default function DAGViewer({ dag }: DAGViewerProps) {
  const { initialNodes, initialEdges, waveGroups, totalWaves } = useMemo(() => {
    const computedNodes: Node[] = [];
    const computedEdges: Edge[] = [];

    const tasks = dag?.tasks || [];
    const taskKeyMap = new Map<string, Task>();
    tasks.forEach((t) => taskKeyMap.set(t.task_key, t));

    // Group tasks by wave / tier
    const groups: Record<number, Task[]> = {};
    tasks.forEach((t) => {
      const w = t.tier !== undefined ? t.tier + 1 : (t.wave || 1);
      if (!groups[w]) groups[w] = [];
      groups[w].push(t);
    });

    Object.entries(groups).forEach(([waveStr, waveTasks]) => {
      const wave = parseInt(waveStr, 10);
      waveTasks.forEach((task, idx) => {
        const xPos = (wave - 1) * 330 + 40;
        const yPos = idx * 150 + 50;
        const displayWave = task.tier !== undefined ? task.tier + 1 : (task.wave || wave);

        computedNodes.push({
          id: task.task_key,
          position: { x: xPos, y: yPos },
          data: {
            label: (
              <div className="p-3.5 bg-white border border-border rounded-lg shadow-sm hover:border-black hover:shadow-md transition-all text-left w-64 cursor-grab active:cursor-grabbing select-none">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-mono bg-grey-100 text-grey-800 px-1.5 py-0.5 rounded font-semibold">
                    {task.task_key}
                  </span>
                  <span className="text-[10px] font-mono text-grey-500 uppercase flex items-center gap-1">
                    <Move className="w-2.5 h-2.5 text-grey-400" />
                    Wave {displayWave}
                  </span>
                </div>
                <div className="font-medium text-xs text-black line-clamp-1 mb-2">
                  {task.title}
                </div>
                <div className="flex items-center justify-between text-[10px] text-grey-500 pt-1.5 border-t border-border">
                  <span className="flex items-center gap-1 font-mono truncate max-w-[130px]">
                    <User className="w-3 h-3 text-grey-400 shrink-0" />
                    {task.assigned_agent ? task.assigned_agent.replace(/_/g, " ") : "Agent"}
                  </span>
                  <span
                    className={`uppercase font-mono px-1.5 py-0.2 rounded text-[9px] shrink-0 ${
                      task.status === "completed"
                        ? "bg-emerald-50 text-emerald-700 font-semibold"
                        : "bg-grey-100 text-grey-600"
                    }`}
                  >
                    {task.status || "pending"}
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
              type: "smoothstep",
              animated: true,
              style: { stroke: "#18181B", strokeWidth: 1.75 },
              markerEnd: {
                type: MarkerType.ArrowClosed,
                color: "#18181B",
                width: 14,
                height: 14,
              },
            });
          });
        }
      });
    });

    const computedTotalWaves =
      dag?.total_tiers ||
      dag?.total_waves ||
      Object.keys(groups).length;

    return {
      initialNodes: computedNodes,
      initialEdges: computedEdges,
      waveGroups: groups,
      totalWaves: computedTotalWaves,
    };
  }, [dag]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  return (
    <div className="space-y-6">
      {/* DAG Stats Bar */}
      <div className="p-4 bg-grey-50 border border-border rounded-lg flex flex-wrap items-center justify-between gap-4 text-xs font-mono">
        <div className="flex items-center gap-6">
          <span className="flex items-center gap-2">
            <GitBranch className="w-4 h-4 text-black" />
            <span className="text-grey-500">Total Tasks:</span>
            <span className="font-bold text-black">
              {dag?.total_tasks ?? dag?.tasks?.length ?? 0}
            </span>
          </span>
          <span className="flex items-center gap-2">
            <span className="text-grey-500">Execution Waves:</span>
            <span className="font-bold text-black">{totalWaves}</span>
          </span>
          <span className="flex items-center gap-2">
            <span className="text-grey-500">Cycles Detected:</span>
            <span
              className={`font-bold ${
                dag?.has_cycle ? "text-red-600" : "text-emerald-600"
              }`}
            >
              {dag?.has_cycle ? "YES (Cycle Found)" : "0 (Acyclic DAG Verified)"}
            </span>
          </span>
        </div>
        <div className="text-[11px] text-grey-500 flex items-center gap-1.5">
          <Move className="w-3.5 h-3.5 text-grey-400" />
          <span>Interactive Canvas • Nodes Draggable • Flowing Dependency Lines</span>
        </div>
      </div>

      {/* React Flow Interactive Graph */}
      <div className="h-[480px] w-full border border-border rounded-xl bg-white overflow-hidden shadow-sm relative group">
        <div className="absolute top-3 left-4 z-10 flex items-center gap-1.5 text-[11px] font-mono text-grey-500 bg-white/95 backdrop-blur-xs px-2.5 py-1 rounded border border-border shadow-xs pointer-events-none">
          <Move className="w-3 h-3 text-grey-400" />
          <span>Drag any node to reposition • Lines dynamically follow</span>
        </div>

        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodesDraggable={true}
          nodesConnectable={false}
          elementsSelectable={true}
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
          {Object.entries(waveGroups).map(([waveNum, waveTasks]) => (
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
