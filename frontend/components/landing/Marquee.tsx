"use client";

export default function Marquee() {
  const items = [
    "REQUIREMENT ANALYSIS",
    "MULTI-AGENT ORCHESTRATION",
    "ARCHITECTURE GENERATION",
    "CODE GENERATION",
    "SANDBOXED EXECUTION",
    "AUTONOMOUS DEBUGGING",
    "SELF-HEALING",
  ];

  return (
    <div className="w-full border-y border-border bg-grey-50/70 overflow-hidden py-3 select-none">
      <div className="flex w-max animate-marquee">
        {/* First set */}
        <div className="flex items-center gap-8 px-4 text-xs font-mono tracking-widest text-grey-600">
          {items.map((item, idx) => (
            <span key={idx} className="flex items-center gap-8">
              <span>{item}</span>
              <span className="text-grey-300">//</span>
            </span>
          ))}
        </div>
        {/* Duplicate set for seamless continuous loop */}
        <div className="flex items-center gap-8 px-4 text-xs font-mono tracking-widest text-grey-600">
          {items.map((item, idx) => (
            <span key={`dup-${idx}`} className="flex items-center gap-8">
              <span>{item}</span>
              <span className="text-grey-300">//</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
