"use client";

import Link from "next/link";
import { ArrowRight, Github } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-white">
      {/* Call to action banner */}
      <div className="border-b border-border py-20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="font-serif text-3xl sm:text-5xl font-normal text-black mb-4">
            Your next application starts with an idea.
          </h2>
          <p className="text-grey-600 text-base sm:text-lg font-light leading-relaxed mb-8 max-w-xl mx-auto">
            Let specialized AI agents take your software development workflow from
            requirements to tested applications.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/projects/new"
              className="inline-flex items-center justify-center gap-2 bg-black text-white hover:bg-grey-800 text-sm font-medium px-7 py-3.5 rounded-md transition-all shadow-sm"
            >
              <span>Start Building</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="https://github.com/Nimalan07/orchestrix-ai"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 bg-white text-grey-800 hover:bg-grey-50 text-sm font-medium px-7 py-3.5 rounded-md transition-all border border-border"
            >
              <Github className="w-4 h-4" />
              <span>Explore GitHub</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Bottom Sub-Footer */}
      <div className="max-w-7xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-grey-500 font-mono">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>SYSTEM ONLINE // ORCHESTRIX 0.1.0</span>
        </div>
        <div>
          © {new Date().getFullYear()} Orchestrix Autonomous AI Software Engineering Platform.
        </div>
      </div>
    </footer>
  );
}
