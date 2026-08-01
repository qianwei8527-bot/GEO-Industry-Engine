import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "GEO Universe - 产业认知与连接基础设施",
  description: "每一个节点，都是自身宇宙的中心。",
};

const NAV_ITEMS = [
  { href: "/universe/home", label: "Home", icon: "●" },
  { href: "/universe/3d", label: "3D", icon: "◆" },
  { href: "/universe/connections", label: "Connections", icon: "◈" },
  { href: "/universe/growth", label: "Growth", icon: "▲" },
  { href: "/universe/opportunities", label: "Opportunities", icon: "★" },
];

export default function UniverseLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-950">
      <nav className="sticky top-0 z-50 border-b border-slate-800/60 bg-slate-950/80 backdrop-blur">
        <div className="max-w-[1440px] mx-auto px-6 h-14 flex items-center gap-6">
          <Link href="/universe/home" className="flex items-center gap-2 text-white font-semibold">
            <span className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center text-xs">G</span>
            Universe
          </Link>
          <div className="flex items-center gap-1">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="px-3 py-1.5 rounded-lg text-sm text-slate-400 hover:text-white hover:bg-slate-800 transition"
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </nav>
      {children}
    </div>
  );
}
