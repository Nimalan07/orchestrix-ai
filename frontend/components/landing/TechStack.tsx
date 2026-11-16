"use client";

export default function TechStack() {
  const stack = [
    {
      category: "Backend Framework",
      techs: ["Python 3.13", "FastAPI", "Pydantic v2", "Uvicorn"],
    },
    {
      category: "AI & Multi-Agent",
      techs: ["LangChain", "LangGraph", "Ollama", "Qwen2.5-Coder (7B)"],
    },
    {
      category: "Database & ORM",
      techs: ["PostgreSQL 18", "SQLAlchemy 2.x", "Alembic Migrations"],
    },
    {
      category: "Frontend & UI",
      techs: ["Next.js 14 (App Router)", "TypeScript", "Tailwind CSS", "React Flow"],
    },
    {
      category: "Execution & QA",
      techs: ["Docker Containers", "Pytest 8.x", "Local Process Sandbox"],
    },
    {
      category: "Infrastructure",
      techs: ["Docker Compose", "Git / GitHub", "REST APIs"],
    },
  ];

  return (
    <section id="technology" className="py-24 bg-grey-50/50 border-b border-border">
      <div className="max-w-7xl mx-auto px-6">
        <div className="max-w-3xl mx-auto text-center mb-16">
          <div className="text-xs font-mono text-grey-500 tracking-widest uppercase mb-3">
            TECHNICAL FOUNDATION
          </div>
          <h2 className="font-serif text-3xl sm:text-4xl md:text-5xl font-normal text-black mb-4">
            Built with modern engineering technologies.
          </h2>
          <p className="text-grey-600 text-base sm:text-lg font-light leading-relaxed">
            Engineered using industry-standard protocols, typed contracts, and enterprise databases.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {stack.map((item, idx) => (
            <div
              key={idx}
              className="p-6 bg-white border border-border rounded-lg"
            >
              <h3 className="text-xs font-mono uppercase tracking-wider text-grey-500 mb-4">
                {item.category}
              </h3>
              <div className="flex flex-wrap gap-2">
                {item.techs.map((t, tidx) => (
                  <span
                    key={tidx}
                    className="inline-flex items-center text-xs font-medium px-2.5 py-1 rounded bg-grey-100 text-grey-800 border border-border/80"
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
