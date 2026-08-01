'use client';

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Building2, Wrench, User, TrendingUp, Landmark, Bot, Search, ArrowRight, Sparkles, MapPin, Star } from "lucide-react";

const ROLES = [
  {
    id: "企业",
    icon: Building2,
    label: "企业",
    subtitle: "了解我的产业位置 · 发现增长机会",
    description: "查看你的企业 GEO 评分、竞争位置、能力画像，发现与同行企业的差距和连接机会。",
    color: "from-blue-500/20 to-blue-600/10 border-blue-500/30 hover:border-blue-400",
    iconColor: "text-blue-400",
  },
  {
    id: "服务商",
    icon: Wrench,
    label: "服务商",
    subtitle: "展示我的能力 · 连接产业需求",
    description: "展示你的服务能力，匹配企业需求，积累信誉记录，提升产业可见度。",
    color: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/30 hover:border-emerald-400",
    iconColor: "text-emerald-400",
  },
  {
    id: "人才",
    icon: User,
    label: "人才",
    subtitle: "定位我的能力 · 发现成长路径",
    description: "了解你的技能在产业中的位置，发现学习路径和职业机会。",
    color: "from-purple-500/20 to-purple-600/10 border-purple-500/30 hover:border-purple-400",
    iconColor: "text-purple-400",
  },
  {
    id: "投资者",
    icon: TrendingUp,
    label: "投资者",
    subtitle: "发现未来产业机会 · 追踪成长企业",
    description: "观察产业动态，发现高成长企业，追踪 GEO 评分变化趋势。",
    color: "from-amber-500/20 to-amber-600/10 border-amber-500/30 hover:border-amber-400",
    iconColor: "text-amber-400",
  },
  {
    id: "政府",
    icon: Landmark,
    label: "政府/机构",
    subtitle: "观察产业发展 · 制定政策依据",
    description: "了解区域内产业结构，追踪产业演化趋势，发现关键节点企业。",
    color: "from-red-500/20 to-red-600/10 border-red-500/30 hover:border-red-400",
    iconColor: "text-red-400",
  },
];

export default function IdentityPage() {
  const router = useRouter();
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleRoleSelect = (roleId: string) => {
    setSelectedRole(roleId);
    setSearchQuery("");
    setResults([]);
  };

  const handleSearch = async () => {
    if (!searchQuery.trim() || !selectedRole) return;
    setLoading(true);
    try {
      const typeMap: Record<string, string> = { "企业": "company", "服务商": "provider" };
      const entityType = typeMap[selectedRole] || "company";
      let url = entityType === "company"
        ? "http://localhost:8080/api/v1/companies?limit=10"
        : "http://localhost:8080/api/v1/providers?limit=10";
      const res = await fetch(url);
      const data = await res.json();
      const filtered = (Array.isArray(data) ? data : []).filter(
        (item: any) => item.name?.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setResults(filtered);
    } catch (err) {
      console.error("Search error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleEnterUniverse = async (entityId: string, entityName: string) => {
    try {
      const profileRes = await fetch("http://localhost:8080/api/v1/universe/identity/profile/" + entityId);
      const profileData = await profileRes.json();
      if (profileData.status === "inferred") {
        await fetch("http://localhost:8080/api/v1/universe/identity/profile", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ entity_id: entityId, identity_type: selectedRole, display_name: entityName, growth_stage: "Entry" }),
        });
        await fetch("http://localhost:8080/api/v1/universe/identity/snapshot", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ entity_id: entityId, snapshot_type: "manual", change_summary: "首次进入 GEO Universe，身份：" + selectedRole }),
        });
      }
      if (selectedRole === "企业") router.push("/company/" + entityId);
      else if (selectedRole === "服务商") router.push("/marketplace/provider/" + entityId);
      else router.push("/intelligence/" + entityId);
    } catch (err) {
      console.error("Enter universe error:", err);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl" />
      </div>
      <div className="relative z-10 max-w-5xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 text-sm text-gray-400 mb-4 bg-white/5 rounded-full px-4 py-1.5 border border-white/5">
            <Sparkles className="w-4 h-4 text-blue-400" />
            GEO Universe Identity Layer
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-white via-blue-100 to-white bg-clip-text text-transparent">
            我是谁？
          </h1>
          <p className="text-gray-400 text-lg max-w-xl mx-auto">
            选择你的身份，进入 GEO Universe。每一个身份都是一个宇宙中心，从这里展开你的产业之旅。
          </p>
        </div>
        {!selectedRole ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 max-w-4xl mx-auto">
            {ROLES.map((role) => (
              <button key={role.id} onClick={() => handleRoleSelect(role.id)}
                className={"relative group p-6 rounded-xl border bg-gradient-to-br " + role.color + " backdrop-blur-sm transition-all duration-300 text-left hover:scale-[1.02]"}
              >
                <role.icon className={"w-10 h-10 mb-4 " + role.iconColor} />
                <h3 className="text-lg font-semibold mb-1">{role.label}</h3>
                <p className="text-sm text-gray-400 mb-3">{role.subtitle}</p>
                <p className="text-xs text-gray-500 leading-relaxed opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  {role.description}
                </p>
                <ArrowRight className="absolute bottom-4 right-4 w-4 h-4 text-gray-600 group-hover:text-white transition-colors" />
              </button>
            ))}
            <div className="md:col-span-3 flex justify-center">
              <div className="relative group p-6 rounded-xl border border-gray-700/50 bg-gradient-to-br from-gray-500/10 to-gray-600/5 backdrop-blur-sm max-w-sm w-full text-left">
                <Bot className="w-10 h-10 mb-4 text-gray-400" />
                <h3 className="text-lg font-semibold mb-1">AI Agent</h3>
                <p className="text-sm text-gray-400">作为 AI 观察者进入 Universe</p>
                <p className="text-xs text-gray-600 mt-3">即将开放</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-2xl mx-auto">
            <button onClick={() => setSelectedRole(null)} className="text-sm text-gray-500 hover:text-gray-300 mb-6 flex items-center gap-1">
              <ArrowRight className="w-4 h-4 rotate-180" /> 重新选择身份
            </button>
            <div className="flex items-center gap-3 mb-8 p-4 rounded-xl bg-white/5 border border-white/10">
              {(() => { const r = ROLES.find(r => r.id === selectedRole); if (!r) return null;
                const Icon = r.icon;
                return (<><Icon className={"w-8 h-8 " + r.iconColor} /><div><div className="font-semibold">以 <span className={r.iconColor}>{r.label}</span> 身份进入</div><div className="text-sm text-gray-500">{r.subtitle}</div></div></>);
              })()}
            </div>
            <div className="flex gap-3 mb-8">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  placeholder={selectedRole === "企业" ? "输入企业名称..." : "输入名称搜索..."}
                  className="w-full pl-12 pr-4 py-4 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-blue-500/50 text-white placeholder-gray-500 transition-all" autoFocus />
              </div>
              <button onClick={handleSearch} disabled={loading || !searchQuery.trim()}
                className="px-6 py-4 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 rounded-xl font-medium transition-all flex items-center gap-2">
                {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <><Search className="w-4 h-4" /> 搜索</>}
              </button>
            </div>
            {results.length > 0 && (
              <div className="space-y-3">
                {results.map((item: any) => (
                  <button key={item.id} onClick={() => handleEnterUniverse(item.id, item.name)}
                    className="w-full p-5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/[0.08] hover:border-blue-500/30 transition-all text-left flex items-center justify-between group">
                    <div>
                      <div className="font-medium text-lg">{item.name}</div>
                      <div className="text-sm text-gray-500 mt-1">{item.industry_name || "未分类"} · {item.company_size || "规模未知"}</div>
                      {item.geo_score != null && <div className="flex items-center gap-2 mt-2"><Star className="w-3.5 h-3.5 text-amber-400" /><span className="text-xs text-gray-400">GEO Score: {item.geo_score}</span></div>}
                    </div>
                    <ArrowRight className="w-5 h-5 text-gray-600 group-hover:text-blue-400 group-hover:translate-x-1 transition-all" />
                  </button>
                ))}
              </div>
            )}
            {results.length === 0 && searchQuery && !loading && (
              <div className="text-center py-12 text-gray-500">
                <MapPin className="w-12 h-12 mx-auto mb-4 text-gray-700" />
                <p>未找到 &quot;{searchQuery}&quot;</p>
                <p className="text-sm mt-2">尝试其他关键词，或确认企业已录入系统</p>
              </div>
            )}
          </div>
        )}
        <div className="text-center mt-20 text-xs text-gray-600">
          <p>GEO Universe · Identity Layer v1.0 · Sprint 5.1</p>
          <p className="mt-1">每个节点都是宇宙中心 · 五种视角观察一个宇宙</p>
        </div>
      </div>
    </div>
  );
}
