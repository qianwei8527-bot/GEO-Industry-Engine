'use client';
import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Award } from 'lucide-react';

export default function ApplyPage() {
  const router = useRouter();
  const [form, setForm] = useState({ name: '', type: 'enterprise', contact: '', description: '' });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <Award className="w-12 h-12 text-green-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{'申请已提交'}</h2>
        <p className="text-gray-500 mb-6">{'我们将在工作日内完成审核'}</p>
        <button onClick={() => router.push('/certification')} className="text-blue-600 underline text-sm">{'返回认证中心'}</button>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">{'申请 GEO 认证'}</h1>
      <p className="text-sm text-gray-500 mb-8">{'提交身份信息和能力证据，建立你的 GEO 信用身份'}</p>
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">{'认证类型'}</label>
          <select value={form.type} onChange={(e) => setForm({...form, type: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400">
            <option value="enterprise">{'企业认证'}</option>
            <option value="individual">{'个人认证'}</option>
            <option value="service">{'服务商认证'}</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">{'名称'}</label>
          <input type="text" value={form.name} onChange={(e) => setForm({...form, name: e.target.value})} required className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400" placeholder={'企业名称 / 姓名 / 服务商名称'} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">{'联系方式'}</label>
          <input type="text" value={form.contact} onChange={(e) => setForm({...form, contact: e.target.value})} required className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400" placeholder="Email / 电话" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">{'能力说明'}</label>
          <textarea value={form.description} onChange={(e) => setForm({...form, description: e.target.value})} rows={4} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400" placeholder={'请描述您的专业能力、技术或服务内容'} />

          {/* GEO Ecosystem Links */}
          <div className='border-t mt-6 pt-3 mb-4'>
            <div className='text-xs text-slate-400 mb-2'>相关功能:</div>
            <div className='flex flex-wrap gap-2'>
              <Link href='/certification' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>认证中心</Link>
              <Link href='/detection' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>检测中心</Link>
              <Link href='/assets' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>补充证据</Link>
            </div>
          </div>

        </div>
        <button type="submit" className="w-full bg-blue-600 text-white py-3 rounded-xl text-sm font-medium hover:bg-blue-700">{'提交申请'}</button>
      </form>
    </div>
  );
}
