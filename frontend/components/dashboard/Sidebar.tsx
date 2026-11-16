"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FolderGit2,
  PlusCircle,
  Cpu,
  BookOpen,
  ArrowUpRight,
  ShieldCheck,
} from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();

  const links = [
    {
      name: "Overview",
      href: "/dashboard",
      icon: LayoutDashboard,
      active: pathname === "/dashboard",
    },
    {
      name: "New Project",
      href: "/projects/new",
      icon: PlusCircle,
      active: pathname === "/projects/new",
    },
    {
      name: "Documentation",
      href: "/docs",
      icon: BookOpen,
      active: pathname === "/docs",
    },
  ];

  return (
    <aside className="w-64 border-r border-border bg-white flex flex-col justify-between h-screen sticky top-0 shrink-0">
      <div>
        {/* Brand Header */}
        <div className="h-16 border-b border-border px-6 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <span className="text-sm font-mono border border-black px-1.5 py-0.5 rounded">◈</span>
            <span className="font-bold tracking-tight text-sm text-black">
              ORCHESTRIX
            </span>
          </Link>
          <span className="flex items-center gap-1.5 text-[10px] font-mono bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Connected
          </span>
        </div>

        {/* Navigation Items */}
        <div className="p-4 space-y-1">
          <div className="text-[11px] font-mono uppercase text-grey-400 px-3 py-2 tracking-wider">
            Workspace
          </div>
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <Link
                key={link.name}
                href={link.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  link.active
                    ? "bg-black text-white"
                    : "text-grey-600 hover:text-black hover:bg-grey-50"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{link.name}</span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* System Status Footer */}
      <div className="p-4 border-t border-border bg-grey-50/50">
        <div className="p-3 bg-white border border-border rounded-md space-y-2 text-xs">
          <div className="flex items-center justify-between text-grey-600">
            <span className="flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-black" />
              <span>LLM Engine</span>
            </span>
            <span className="font-mono text-[10px] bg-grey-100 px-1.5 py-0.5 rounded text-black font-medium">
              Ollama // Qwen
            </span>
          </div>
          <div className="flex items-center justify-between text-grey-600">
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-black" />
              <span>Sandbox</span>
            </span>
            <span className="font-mono text-[10px] bg-grey-100 px-1.5 py-0.5 rounded text-black font-medium">
              Dual-Mode
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
