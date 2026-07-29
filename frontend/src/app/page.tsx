"use client";

import Link from "next/link";

const systems = [
  { num: "01", name: "检测中心", desc: "认识自己在 AI 时代的位置", tag: "个人/企业/机构", href: "/detection" },
  { num: "02", name: "认证中心", desc: "证明自己值得被信任", tag: "信用体系", href: "/certification" },
  { num: "03", name: "产业导航", desc: "找到产业中的位置和方向", tag: "生态地图", href: "/navigation" },
  { num: "04", name: "数据资产中心", desc: "沉淀产业知识，积累数字资产", tag: "资产管理", href: "/assets" },
  { num: "05", name: "交易市场", desc: "产生商业连接，完成价值闭环", tag: "连接器", href: "/marketplace" },
  { num: "06", name: "产业情报", desc: "发现机会、识别风险、竞争分析", tag: "智能感知", href: "/intelligence" },
];

const roles = [
  { role: "企业", q: "我的AI可见度如何？", href: "/detection" },
  { role: "个人", q: "我的职业竞争力？", href: "/certification" },
  { role: "服务商", q: "如何获得客户？", href: "/marketplace" },
  { role: "投资机构", q: "哪里有投资机会？", href: "/navigation" },
  { role: "政府/园区", q: "区域产业怎么发展？", href: "/navigation" },
  { role: "研究机构", q: "行业趋势如何？", href: "/assets" },
];

export default function Home() {
  return (
    <>
      {/* Hero + Flywheel */}
      <section className="bg-gradient-to-b from-blue-50 to-white py-16 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <p className="text-blue-600 font-medium text-sm mb-3">
            GEO 产业生态基础设施
          </p>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4 leading-tight">
            发现你在 GEO 产业中的位置
          </h1>
          <p className="text-lg text-gray-600 mb-6 max-w-2xl mx-auto">
            了解你的机会 · 识别你的风险 · 规划你的未来
          </p>

          {/* Flywheel SVG */}
          <div className="flex justify-center mb-8">
            <svg width="480" height="240" viewBox="0 0 480 240" className="w-full max-w-lg">
              <defs>
                <marker id="arrow" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
                  <path d="M0,0 L8,3 L0,6 Z" fill="#3b82f6" />
                </marker>
                <style>{`
                  @keyframes pulse1 { 0%,100% { opacity: 0.6 } 50% { opacity: 1 } }
                  @keyframes pulse2 { 0%,100% { opacity: 0.6 } 50% { opacity: 1 } }
                  @keyframes pulse3 { 0%,100% { opacity: 0.6 } 50% { opacity: 1 } }
                  @keyframes pulse4 { 0%,100% { opacity: 0.6 } 50% { opacity: 1 } }
                  @keyframes pulse5 { 0%,100% { opacity: 0.6 } 50% { opacity: 1 } }
                  .f1 { animation: pulse1 3s infinite }
                  .f2 { animation: pulse2 3s infinite 0.6s }
                  .f3 { animation: pulse3 3s infinite 1.2s }
                  .f4 { animation: pulse4 3s infinite 1.8s }
                  .f5 { animation: pulse5 3s infinite 2.4s }
                `}</style>
              </defs>
              {/* Arrows forming a pentagon flywheel */}
              <g stroke="#3b82f6" strokeWidth="1.5" fill="none" markerEnd="url(#arrow)">
                <line x1="240" y1="30"  x2="400" y2="85"  className="f1" />
                <line x1="400" y1="85"  x2="365" y2="195" className="f2" />
                <line x1="365" y1="195" x2="115" y2="195" className="f3" />
                <line x1="115" y1="195" x2="80"  y2="85"  className="f4" />
                <line x1="80"  y1="85"  x2="240" y2="30"  className="f5" />
              </g>
              {/* Nodes */}
              <g textAnchor="middle" fontSize="11" fill="#374151">
                <circle cx="240" cy="22" r="14" fill="#dbeafe" stroke="#3b82f6" strokeWidth="1.5" />
                <text x="240" y="26" fontWeight="bold">数据</text>

                <circle cx="414" cy="88" r="14" fill="#dbeafe" stroke="#3b82f6" strokeWidth="1.5" />
                <text x="414" y="92" fontWeight="bold">认知</text>

                <circle cx="370" cy="210" r="14" fill="#dbeafe" stroke="#3b82f6" strokeWidth="1.5" />
                <text x="370" y="214" fontWeight="bold">信任</text>

                <circle cx="110" cy="210" r="14" fill="#dbeafe" stroke="#3b82f6" strokeWidth="1.5" />
                <text x="110" y="214" fontWeight="bold">连接</text>

                <circle cx="66" cy="88" r="14" fill="#dbeafe" stroke="#3b82f6" strokeWidth="1.5" />
                <text x="66" y="92" fontWeight="bold">交易</text>
              </g>
            </svg>
          </div>

          {/* Search bar */}
          <div className="flex items-center justify-center gap-2 max-w-xl mx-auto">
            <input
              type="text"
              placeholder="输入企业、个人或品牌名称，免费检测"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-sm outline-none focus:border-blue-400"
            />
            <Link
              href="/detection"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-blue-700 whitespace-nowrap"
            >
              开始GEO产业评估
            </Link>
          </div>
        </div>
      </section>

      {/* Six Systems */}
      <section className="py-12 px-4">
        <div className="max-w-5xl mx-auto">
          <h3 className="text-xl font-bold text-center text-gray-900 mb-2">六大系统</h3>
          <p className="text-gray-500 text-center text-sm mb-8">
            数据 → 认知 → 信任 → 连接 → 交易 → 数据反哺
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {systems.map((s) => (
              <Link key={s.num} href={s.href}>
                <div className="border border-gray-200 rounded-xl p-5 hover:border-blue-300 hover:shadow-md transition-all bg-white h-full">
                  <span className="text-xs text-blue-500 font-mono bg-blue-50 px-2 py-0.5 rounded">
                    {s.num}
                  </span>
                  <span className="text-xs text-gray-400 ml-2">{s.tag}</span>
                  <h4 className="font-semibold text-gray-900 mt-2 mb-1">{s.name}</h4>
                  <p className="text-sm text-gray-500">{s.desc}</p>
                </div>
              </Link>
            ))}
          </div>
          <p className="text-center mt-6 text-sm text-gray-400">
            飞轮闭合：交易市场产生的数据反哺回检测中心，越用越聪明
          </p>
        </div>
      </section>

      {/* Role-based Entry */}
      <section className="py-12 px-4 bg-gray-50">
        <div className="max-w-5xl mx-auto">
          <h3 className="text-xl font-bold text-center text-gray-900 mb-6">
            按角色进入
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {roles.map((r) => (
              <Link key={r.role} href={r.href}>
                <div className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:bg-blue-50 transition-all bg-white text-center">
                  <div className="font-semibold text-gray-900 text-sm">{r.role}</div>
                  <div className="text-xs text-gray-400 mt-1">{r.q}</div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
