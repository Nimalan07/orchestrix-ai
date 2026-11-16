"use client";

import Link from "next/link";
import { ArrowRight, Terminal, Sparkles, CheckCircle2 } from "lucide-react";

export default function Hero() {
  return (
    <section className="relative pt-24 pb-20 md:pt-32 md:pb-28 overflow-hidden bg-white">
      {/* Background Subtle Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#f0f0f0_1px,transparent_1px),linear-gradient(to_bottom,#f0f0f0_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none opacity-40" />

      <div className="relative max-w-5xl mx-auto px-6 text-center">
        {/* Eyebrow */}
        <div className="inline-flex items-center gap-2 px-3 py-1 mb-8 rounded-full border border-border bg-grey-50 text-[11px] font-mono tracking-widest uppercase text-grey-700">
          <span className="w-1.5 h-1.5 rounded-full bg-black animate-pulse" />
          AUTONOMOUS SOFTWARE ENGINEERING PLATFORM
        </div>

        {/* Primary Serif Headline */}
        <h1 className="font-serif text-4xl sm:text-6xl md:text-7xl font-normal tracking-tight text-black leading-[1.12] mb-6 max-w-4xl mx-auto">
          From Idea to Production-Ready Software. <span className="italic">Autonomously.</span>
        </h1>

        {/* Supporting Subtitle */}
        <p className="text-base sm:text-lg md:text-xl text-grey-600 max-w-2xl mx-auto font-light leading-relaxed mb-10">
          Orchestrix is an AI-powered multi-agent software engineering platform that
          transforms natural-language requirements into functional, tested and
          reviewable applications.
        </p>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-14">
          <Link
            href="/projects/new"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 bg-black text-white hover:bg-grey-800 text-sm font-medium px-7 py-3.5 rounded-md transition-all shadow-sm group"
          >
            <span>Start Building</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          </Link>
          <Link
            href="#features"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-grey-100 hover:bg-grey-200 text-grey-800 text-sm font-medium px-7 py-3.5 rounded-md transition-all border border-border"
          >
            <span>Explore Features</span>
          </Link>
        </div>

        {/* Technical Sub-Tagline */}
        <div className="pt-8 border-t border-border/80 flex flex-wrap items-center justify-center gap-y-2 gap-x-6 text-[11px] font-mono tracking-wider uppercase text-grey-500">
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-black" />
            MULTI-AGENT AI
          </span>
          <span className="text-grey-300">•</span>
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-black" />
            AUTONOMOUS CODE GENERATION
          </span>
          <span className="text-grey-300">•</span>
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-black" />
            SANDBOXED EXECUTION
          </span>
          <span className="text-grey-300">•</span>
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-black" />
            SELF-HEALING
          </span>
        </div>
      </div>
    </section>
  );
}
