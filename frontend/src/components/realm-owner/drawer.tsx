"use client";

import { useEffect, useRef } from "react";
import type { ReactNode } from "react";
import { X } from "lucide-react";

interface DrawerProps {
  open: boolean;
  title: string;
  description?: string;
  onClose: () => void;
  children: ReactNode;
  footer?: ReactNode;
  widthClass?: string;
}

export default function RealmDrawer({
  open,
  title,
  description,
  onClose,
  children,
  footer,
  widthClass = "max-w-lg",
}: DrawerProps) {
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    closeRef.current?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", onKey);
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end" role="presentation">
      <button
        type="button"
        aria-label="关闭抽屉"
        className="absolute inset-0 bg-slate-900/30 backdrop-blur-[1px] cursor-default"
        onClick={onClose}
      />
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="realm-drawer-title"
        className={`relative z-10 h-full w-full ${widthClass} bg-white border-l border-slate-200 shadow-xl flex flex-col`}
      >
        <header className="flex items-start justify-between gap-4 px-5 py-4 border-b border-slate-200">
          <div className="min-w-0">
            <h2 id="realm-drawer-title" className="text-base font-semibold text-slate-900 truncate">
              {title}
            </h2>
            {description && <p className="mt-1 text-xs text-slate-500">{description}</p>}
          </div>
          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            aria-label="关闭"
            className="shrink-0 inline-flex items-center justify-center w-8 h-8 rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
          >
            <X className="w-4 h-4" />
          </button>
        </header>
        <div className="flex-1 overflow-y-auto px-5 py-4">{children}</div>
        {footer && <footer className="border-t border-slate-200 px-5 py-4">{footer}</footer>}
      </section>
    </div>
  );
}