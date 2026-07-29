'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Sliders, Building2, Factory, ShieldCheck, Activity, ChevronRight } from 'lucide-react';
import { useState } from 'react';

const sidebarItems = [
  { href: '/admin', label: '仪表盘', icon: LayoutDashboard },
  { href: '/admin/config', label: '配置管理', icon: Sliders },
  { href: '/admin/companies', label: '企业管理', icon: Building2 },
  { href: '/admin/industries', label: '行业管理', icon: Factory },
  { href: '/admin/certifications', label: '认证审核', icon: ShieldCheck },
  { href: '/admin/health', label: '系统监控', icon: Activity },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className={`${collapsed ? 'w-16' : 'w-56'} bg-slate-900 text-white flex flex-col transition-all duration-200 border-r border-slate-700`}>
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          {!collapsed && <span className="font-bold text-sm tracking-wide">GEO 控制台</span>}
          <button onClick={() => setCollapsed(!collapsed)} className="p-1 rounded hover:bg-slate-700 text-slate-400">
            <ChevronRight className={`w-4 h-4 transition-transform ${collapsed ? '' : 'rotate-180'}`} />
          </button>
        </div>
        <nav className="flex-1 py-2">
          {sidebarItems.map(item => {
            const active = pathname === item.href || (item.href !== '/admin' && pathname.startsWith(item.href));
            return (
              <Link key={item.href} href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 mx-2 rounded-lg text-sm transition-colors ${
                  active ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>
        <div className="p-3 border-t border-slate-700 text-xs text-slate-500">
          {!collapsed && <span>GEO-IE v1.0</span>}
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <div className="p-6 max-w-7xl">
          {children}
        </div>
      </main>
    </div>
  );
}
