"use client";

import {
  AlertCircle,
  AlertTriangle,
  Clock,
  Info,
  Loader2,
  Lock,
  RefreshCw,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

export type ModuleStateVariant =
  | "loading"
  | "empty"
  | "blocked"
  | "error"
  | "stale"
  | "forbidden"
  | "no-permission"
  | "partial";

interface ModuleStateProps {
  variant: ModuleStateVariant;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  errorRef?: string | null;
  icon?: LucideIcon;
  compact?: boolean;
}

const VARIANT_META: Record<ModuleStateVariant, { icon: LucideIcon; className: string }> = {
  loading: { icon: Loader2, className: "text-slate-400" },
  empty: { icon: Info, className: "text-slate-400" },
  blocked: { icon: Lock, className: "text-amber-600" },
  error: { icon: AlertCircle, className: "text-rose-600" },
  stale: { icon: Clock, className: "text-amber-600" },
  forbidden: { icon: Lock, className: "text-rose-600" },
  "no-permission": { icon: Lock, className: "text-rose-600" },
  partial: { icon: AlertTriangle, className: "text-amber-600" },
};

export default function ModuleState({
  variant,
  title,
  description,
  actionLabel,
  onAction,
  errorRef,
  icon,
  compact = false,
}: ModuleStateProps) {
  const meta = VARIANT_META[variant];
  const Icon = icon || meta.icon;

  if (variant === "loading") {
    return (
      <div className="p-4" role="status" aria-label="加载中">
        <div className="space-y-3">
          <div className="h-4 w-1/3 rounded bg-slate-200 animate-pulse" />
          <div className="h-8 w-full rounded bg-slate-100 animate-pulse" />
          <div className="h-8 w-full rounded bg-slate-100 animate-pulse" />
          <div className="h-8 w-2/3 rounded bg-slate-100 animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div
      className={`flex flex-col items-start gap-2 rounded-lg border p-4 ${
        compact ? "border-slate-200 bg-slate-50" : "border-slate-200 bg-white"
      }`}
      role="status"
    >
      <div className={`flex items-center gap-2 text-sm font-medium ${meta.className}`}>
        <Icon className="w-4 h-4" aria-hidden="true" />
        <span>{title}</span>
      </div>
      {description && <p className="text-xs leading-5 text-slate-600">{description}</p>}
      {errorRef && <p className="text-[11px] text-slate-400">错误引用：{errorRef}</p>}
      {actionLabel && onAction && (
        <button
          type="button"
          onClick={onAction}
          className="mt-1 inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
        >
          {variant === "error" || variant === "stale" ? (
            <RefreshCw className="w-3.5 h-3.5" aria-hidden="true" />
          ) : null}
          {actionLabel}
        </button>
      )}
    </div>
  );
}
