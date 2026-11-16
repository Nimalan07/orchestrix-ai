"use client";

import Link from "next/link";
import { FolderGit2, ArrowRight, Clock, ShieldCheck, CheckCircle2 } from "lucide-react";
import { Project } from "../../types/project";

export default function ProjectCard({ project }: { project: Project }) {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return (
          <span className="text-[10px] font-mono bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            COMPLETED
          </span>
        );
      case "generating":
        return (
          <span className="text-[10px] font-mono bg-amber-50 text-amber-700 border border-amber-200 px-2 py-0.5 rounded-full animate-pulse">
            GENERATING
          </span>
        );
      case "planned":
        return (
          <span className="text-[10px] font-mono bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded-full">
            PLANNED
          </span>
        );
      default:
        return (
          <span className="text-[10px] font-mono bg-grey-100 text-grey-700 border border-border px-2 py-0.5 rounded-full uppercase">
            {status}
          </span>
        );
    }
  };

  const formattedDate = new Date(project.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <Link
      href={`/projects/${project.id}`}
      className="group block p-6 bg-white border border-border rounded-lg hover:border-black/50 hover:shadow-[0_4px_20px_rgba(0,0,0,0.03)] transition-all"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-grey-50 rounded border border-border text-black group-hover:bg-black group-hover:text-white transition-colors">
            <FolderGit2 className="w-4 h-4" />
          </div>
          <h3 className="font-medium text-black text-base group-hover:underline decoration-1 underline-offset-4">
            {project.name}
          </h3>
        </div>
        {getStatusBadge(project.status)}
      </div>

      <p className="text-sm text-grey-600 font-light line-clamp-2 mb-4 leading-relaxed">
        {project.description || "No description provided."}
      </p>

      <div className="pt-3 border-t border-border flex items-center justify-between text-xs text-grey-500 font-mono">
        <span className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5" />
          {formattedDate}
        </span>
        <span className="flex items-center gap-1 text-black font-sans font-medium text-xs group-hover:translate-x-0.5 transition-transform">
          Open Workspace
          <ArrowRight className="w-3.5 h-3.5" />
        </span>
      </div>
    </Link>
  );
}
