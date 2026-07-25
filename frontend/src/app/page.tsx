import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">GEO-Industry-Engine</h1>
          <nav className="flex gap-6 text-sm text-gray-600">
            <a href="#" className="hover:text-blue-600">AI增长中心</a>
            <a href="#" className="hover:text-blue-600">产业导航</a>
            <a href="#" className="hover:text-blue-600">交易市场</a>
            <a href="#" className="hover:text-blue-600">数据中心</a>
          </nav>
          <div className="flex gap-3">
            <Link href="/login" className="text-sm text-gray-600 hover:text-blue-600 px-3 py-1.5">登录</Link>
            <Link href="/register" className="text-sm bg-blue-600 text-white px-4 py-1.5 rounded-lg hover:bg-blue-700">注册</Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="flex-1 flex flex-col items-center justify-center px-4 py-20 text-center">
        <div className="max-w-3xl">
          <h2 className="text-5xl font-bold tracking-tight text-gray-900 mb-4">
            AI时代企业增长基础设施
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            GEO产业引擎 · 让每一家企业、每一个个体在AI搜索时代被看见、被理解、被选择
          </p>
          <div className="flex gap-4 justify-center">
            <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden">
              <input type="text" placeholder="输入企业域名或姓名，免费检测GEO评分" className="px-4 py-2.5 w-80 text-sm outline-none" />
              <button className="bg-blue-600 text-white px-6 py-2.5 text-sm font-medium hover:bg-blue-700">检测</button>
            </div>
          </div>
        </div>
      </section>

      {/* Core Systems */}
      <section className="border-t border-gray-200 py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              { title: "AI增长中心", desc: "企业/个人AI检测、GEO评分、曝光分析、内容优化" },
              { title: "产业导航", desc: "五张MECE产业地图，定位、学习、发现商业价值" },
              { title: "交易市场", desc: "服务、工具、数据、知识、人才开放交易平台" },
              { title: "数据中心", desc: "行业数据库、企业数据库、GEO指数、知识图谱" },
            ].map((item) => (
              <div key={item.title} className="border border-gray-200 rounded-lg p-6 hover:border-blue-300 transition-colors">
                <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-sm text-gray-600">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-8 text-center text-sm text-gray-500">
        GEO-Industry-Engine &copy; 2026
      </footer>
    </div>
  );
}
