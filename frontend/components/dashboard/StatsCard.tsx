"use client";

import { LucideIcon } from "lucide-react";

interface StatsCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
}

export default function StatsCard({
  label,
  value,
  subtitle,
  icon: Icon,
}: StatsCardProps) {
  return (
    <div className="p-6 bg-white border border-border rounded-lg shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs font-mono text-grey-500 uppercase tracking-wider">
          {label}
        </span>
        <div className="p-2 bg-grey-50 rounded border border-border text-black">
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="text-3xl font-serif text-black font-normal mb-1">
        {value}
      </div>
      {subtitle && (
        <div className="text-xs text-grey-500 font-light">
          {subtitle}
        </div>
      )}
    </div>
  );
}
