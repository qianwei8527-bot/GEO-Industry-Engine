'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Compass, Shield, Map, Database, ShoppingCart, Search } from 'lucide-react';

const navItems = [
  { name: '检测中心', path: '/detection', icon: Search },
  { name: '认证中心', path: '/certification', icon: Shield },
  { name: '产业导航', path: '/navigation', icon: Compass },
  { name: '数据资产中心', path: '/assets', icon: Database },
  { name: '交易市场', path: '/marketplace', icon: ShoppingCart },
];

export default function Header() {
  const pathname = usePathname();
  return (
    <header className="border-b border-gray-200 bg-white sticky top-0 z-20">
      <div className="max-w-7xl mx-auto px-4 py-2.5 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <Map className="w-5 h-5 text-blue-600" />
          <span className="font-bold text-gray-900">GEO产业引擎</span>
        </Link>
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = pathname.startsWith(item.path);
            return (
              <Link key={item.path} href={item.path}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors ${active ? 'bg-blue-50 text-blue-600 font-medium' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'}`}
              >
                <Icon className="w-3.5 h-3.5" />
                {item.name}
              </Link>
            );
          })}
        </nav>
        <div className="flex items-center gap-2">
          <Link href="/login" className="text-sm text-gray-600 hover:text-gray-900 px-3 py-1.5">{'登录'}</Link>
          <Link href="/register" className="text-sm bg-blue-600 text-white px-4 py-1.5 rounded-lg hover:bg-blue-700">{'注册'}</Link>
        </div>
      </div>
    </header>
  );
}
