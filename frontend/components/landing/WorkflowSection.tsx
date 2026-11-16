"use client";

import { ArrowRight, Sparkles, Check, RefreshCw } from "lucide-react";

export default function WorkflowSection() {
  const steps = [
    {
      num: "01",
      title: "Requirements Analysis",
      desc: "Converts natural language input into validated functional specifications and user roles.",
    },
    {
      num: "02",
      title: "System Architecture",
      desc: "Synthesizes data entities, relationship schemas, and strictly typed REST API contracts.",
    },
    {
      num: "03",
      title: "DAG Task Decomposition",
      desc: "Deterministically computes topological execution waves using Kahn's graph algorithm.",
    },
    {
      num: "04",
      title: "Multi-Agent Code Generation",
      desc: "Specialized agents produce fullstack code safely written to isolated workspaces.",
    },
    {
      num: "05",
      title: "Sandboxed Testing",
      desc: "Executes automated Pytest suites within CPU/memory constrained containers or local process sandboxes.",
    },
    {
      num: "06",
      title: "Autonomous Self-Healing",
      desc: "Diagnoses stack traces, generates targeted unified patches, and re-tests until 100% verified.",
    },
  ];

  return (
    <section id="workflow" className="py-24 bg-grey-50/50 border-b border-border">
      <div className="max-w-7xl mx-auto px-6">
        <div className="max-w-3xl mx-auto text-center mb-16">
          <div className="text-xs font-mono text-grey-500 tracking-widest uppercase mb-3">
            AUTONOMOUS VERIFICATION LOOP
          </div>
          <h2 className="font-serif text-3xl sm:text-4xl md:text-5xl font-normal text-black mb-4">
            From a single prompt to an engineered application.
          </h2>
          <p className="text-grey-600 text-base sm:text-lg font-light leading-relaxed">
            Unlike simple chatbots, Orchestrix executes an active verification loop with code
            execution, test verification, and automated root-cause healing.
          </p>
        </div>

        {/* Steps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {steps.map((step, idx) => (
            <div
              key={idx}
              className="p-6 bg-white border border-border rounded-lg relative overflow-hidden"
            >
              <div className="text-2xl font-serif text-grey-300 font-normal mb-3">
                {step.num}
              </div>
              <h3 className="text-lg font-medium text-black mb-2 tracking-tight">
                {step.title}
              </h3>
              <p className="text-sm text-grey-600 font-light leading-relaxed">
                {step.desc}
              </p>
            </div>
          ))}
        </div>

        {/* Closed-loop feedback banner */}
        <div className="p-6 bg-black text-white rounded-lg flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/10 rounded-full">
              <RefreshCw className="w-6 h-6 text-white animate-spin-slow" />
            </div>
            <div>
              <div className="text-sm font-medium tracking-wide">
                Closed-Loop Self-Healing Engine
              </div>
              <div className="text-xs text-grey-400 font-light">
                Bounded to 3 repair iterations. Automatically re-runs test suites upon patch application.
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono bg-white/10 px-4 py-2 rounded border border-white/10">
            <Check className="w-4 h-4 text-emerald-400" />
            <span>ZERO UNTESTED ARTIFACTS</span>
          </div>
        </div>
      </div>
    </section>
  );
}
