'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Compass, Crosshair, Map, TrendingUp, Lightbulb, Link2 } from 'lucide-react';

const nodeNavItems = [
  { name: '身份', path: '/universe/identity', icon: Crosshair, question: '我是谁？' },
  { name: '导航', path: '/universe/navigation', icon: Map, question: '我在哪？' },
  { name: '成长', path: '/universe/growth', icon: TrendingUp, question: '如何变化？' },
  { name: '机会', path: '/universe/opportunities', icon: Lightbulb, question: '去哪里？' },
  { name: '连接', path: '/universe/connections', icon: Link2, question: '连接谁？' },
];

export default function Header() {
  const pathname = usePathname();

  // Hide on admin routes — admin has its own layout
  if (pathname.startsWith('/admin')) return null;

  // Node-facing header for /universe/* routes
  if (pathname.startsWith('/universe')) {
    return (
      <header className="border-b border-slate-800 bg-slate-950 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 py-2.5 flex items-center justify-between">
          <Link href="/universe/navigation" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:shadow-blue-500/40 transition-shadow">
              <Compass className="w-4.5 h-4.5 text-white" />
            </div>
            <div className="flex flex-col leading-tight">
              <span className="font-bold text-white text-sm">GEO Universe</span>
              <span className="text-[10px] text-slate-500">产业认知与连接基础设施</span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-0.5">
            {nodeNavItems.map((item) => {
              const Icon = item.icon;
              const active = pathname === item.path || pathname.startsWith(item.path);
              return (
                <Link key={item.path} href={item.path}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-all ${
                    active
                      ? 'bg-slate-800 text-white font-medium'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                  title={item.question}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center gap-2">
            <Link href="/admin" className="text-xs text-slate-600 hover:text-slate-400 px-3 py-1.5 rounded-lg hover:bg-slate-800/50 transition-all">
              控制台
            </Link>
          </div>
        </div>
      </header>
    );
  }

  // Default header for non-universe pages (landing, login, etc.)
  return (
    <header className="border-b border-slate-200 bg-white sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 py-2.5 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Compass className="w-4.5 h-4.5 text-white" />
          </div>
          <span className="font-bold text-gray-900 text-sm">GEO Universe</span>
        </Link>
        <div className="flex items-center gap-2">
          <Link href="/universe/navigation" className="text-sm text-blue-600 hover:text-blue-700 font-medium px-4 py-1.5 rounded-lg hover:bg-blue-50 transition-all">
            进入宇宙
          </Link>
        </div>
      </div>
    </header>
  );
}
