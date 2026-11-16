"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Sidebar from "../../../components/dashboard/Sidebar";
import { projectService } from "../../../services/projectService";
import { ArrowLeft, Sparkles, ArrowRight, Loader2, Lightbulb } from "lucide-react";

export default function NewProjectPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const samplePrompts = [
    {
      name: "Student Management Platform",
      prompt:
        "Build a student management platform with authentication, attendance tracking, student profiles and an admin dashboard.",
    },
    {
      name: "E-Commerce Micro-Market",
      prompt:
        "Build a modern e-commerce platform with product catalogs, shopping cart, checkout flow and customer order history.",
    },
    {
      name: "Sprint Task Tracker",
      prompt:
        "Build a developer issue tracking tool with sprint planning, Kanban boards, priority filters and activity audit logs.",
    },
  ];

  const handleSelectSample = (sample: { name: string; prompt: string }) => {
    setName(sample.name);
    setDescription(sample.prompt);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !description.trim()) {
      setError("Please provide both a project name and a requirement description.");
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      const project = await projectService.create({
        name: name.trim(),
        description: description.trim(),
      });
      router.push(`/projects/${project.id}`);
    } catch (err: any) {
      console.error("Failed to create project:", err);
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to initialize project. Please verify the backend is running."
      );
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex">
      <Sidebar />

      <main className="flex-1 overflow-y-auto">
        <header className="h-16 border-b border-border px-8 flex items-center justify-between sticky top-0 bg-white/90 backdrop-blur-md z-10">
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="p-1.5 text-grey-500 hover:text-black rounded hover:bg-grey-100 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <h1 className="text-sm font-medium text-black">New Engineering Project</h1>
          </div>
        </header>

        <div className="p-8 max-w-3xl mx-auto space-y-8">
          <div>
            <div className="text-xs font-mono text-grey-500 tracking-wider uppercase mb-2">
              NATURAL-LANGUAGE SPECIFICATION
            </div>
            <h2 className="font-serif text-3xl font-normal text-black mb-3">
              Describe the application you want to build.
            </h2>
            <p className="text-sm text-grey-600 font-light leading-relaxed">
              Our autonomous AI engineering team will analyze requirements, design
              architecture, generate dependency-aware tasks, and produce verified source code.
            </p>
          </div>

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 text-red-700 text-xs rounded-md">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-xs font-mono uppercase tracking-wider text-grey-700 mb-2">
                Project Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Student Management Platform"
                required
                className="w-full px-4 py-2.5 text-sm bg-grey-50 border border-border rounded-md focus:outline-none focus:border-black text-black"
              />
            </div>

            <div>
              <label className="block text-xs font-mono uppercase tracking-wider text-grey-700 mb-2">
                Application Requirements
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={6}
                placeholder="Describe features, user roles, authentication requirements, and core entities in natural language..."
                required
                className="w-full px-4 py-3 text-sm bg-grey-50 border border-border rounded-md focus:outline-none focus:border-black text-black leading-relaxed resize-y"
              />
            </div>

            <div className="pt-2 flex items-center justify-between">
              <Link
                href="/dashboard"
                className="text-xs font-medium text-grey-500 hover:text-black transition-colors"
              >
                Cancel
              </Link>
              <button
                type="submit"
                disabled={isSubmitting}
                className="inline-flex items-center gap-2 bg-black text-white hover:bg-grey-800 disabled:bg-grey-400 text-xs font-medium px-6 py-3 rounded-md transition-all shadow-sm"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Initializing Engine...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Launch Engineering Pipeline</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Prompt Suggestions */}
          <div className="pt-6 border-t border-border space-y-3">
            <div className="flex items-center gap-2 text-xs font-mono text-grey-500 uppercase">
              <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
              <span>Or choose a reference template:</span>
            </div>
            <div className="grid grid-cols-1 gap-2.5">
              {samplePrompts.map((s, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelectSample(s)}
                  className="text-left p-3.5 bg-grey-50 hover:bg-grey-100 border border-border rounded-md text-xs transition-colors group"
                >
                  <div className="font-medium text-black mb-1 group-hover:underline">
                    {s.name}
                  </div>
                  <div className="text-grey-600 font-light line-clamp-1">
                    {s.prompt}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
