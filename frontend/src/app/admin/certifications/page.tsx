'use client';
import { ShieldCheck, Search } from 'lucide-react';

export default function AdminCertificationsPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">认证审核</h1>
        <p className="text-sm text-slate-500 mt-1">AI初筛 + 人工复审双重机制</p>
      </div>
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
          <div className="text-3xl font-bold text-amber-500">0</div>
          <div className="text-sm text-slate-500 mt-1">待审核</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
          <div className="text-3xl font-bold text-green-500">0</div>
          <div className="text-sm text-slate-500 mt-1">已通过</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
          <div className="text-3xl font-bold text-red-400">0</div>
          <div className="text-sm text-slate-500 mt-1">已驳回</div>
        </div>
      </div>
      <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center shadow-sm">
        <ShieldCheck className="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p className="text-slate-500">认证审核工作流已设计</p>
        <p className="text-xs text-slate-400 mt-2 max-w-md mx-auto">
          流程: 企业提交申请 → AI初筛（格式/完整度/违规检查）→ 人工复审核AI标记项 → 通过/驳回/补充材料
        </p>
      </div>
    </div>
  );
}
