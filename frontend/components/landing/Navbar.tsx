"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowRight, Menu, X } from "lucide-react";

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full bg-white/90 backdrop-blur-md border-b border-border transition-all">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <span className="text-xl font-bold tracking-tight text-black flex items-center gap-1.5">
            <span className="text-sm font-mono border border-black px-1.5 py-0.5 rounded">◈</span>
            ORCHESTRIX
          </span>
        </Link>

        {/* Center Navigation Links */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-grey-600">
          <Link href="#features" className="hover:text-black transition-colors">
            Features
          </Link>
          <Link href="#agents" className="hover:text-black transition-colors">
            Agents
          </Link>
          <Link href="#workflow" className="hover:text-black transition-colors">
            Workflow
          </Link>
          <Link href="#technology" className="hover:text-black transition-colors">
            Technology
          </Link>
          <Link
            href="https://github.com/Nimalan07/orchestrix-ai"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-black transition-colors"
          >
            GitHub
          </Link>
        </nav>

        {/* Right CTA Button */}
        <div className="hidden md:flex items-center gap-3">
          <Link
            href="/dashboard"
            className="text-sm font-medium px-4 py-2 text-grey-600 hover:text-black transition-colors"
          >
            Dashboard
          </Link>
          <Link
            href="/projects/new"
            className="inline-flex items-center gap-2 bg-black text-white hover:bg-grey-800 text-sm font-medium px-4 py-2 rounded-md transition-all shadow-sm"
          >
            <span>Get Started</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Mobile menu button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 text-grey-700 hover:text-black focus:outline-none"
          aria-label="Toggle Menu"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-border bg-white px-6 py-4 space-y-3">
          <Link
            href="#features"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-sm font-medium text-grey-700 hover:text-black py-1"
          >
            Features
          </Link>
          <Link
            href="#agents"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-sm font-medium text-grey-700 hover:text-black py-1"
          >
            Agents
          </Link>
          <Link
            href="#workflow"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-sm font-medium text-grey-700 hover:text-black py-1"
          >
            Workflow
          </Link>
          <Link
            href="#technology"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-sm font-medium text-grey-700 hover:text-black py-1"
          >
            Technology
          </Link>
          <div className="pt-2 flex flex-col gap-2">
            <Link
              href="/dashboard"
              onClick={() => setMobileMenuOpen(false)}
              className="text-center text-sm font-medium px-4 py-2 border border-border rounded-md hover:bg-grey-50"
            >
              Dashboard
            </Link>
            <Link
              href="/projects/new"
              onClick={() => setMobileMenuOpen(false)}
              className="text-center text-sm font-medium px-4 py-2 bg-black text-white rounded-md hover:bg-grey-800"
            >
              Get Started
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
