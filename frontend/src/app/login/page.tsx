'use client';
import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";

export default function LoginPage() {
  const router = useRouter();
  const [account, setAccount] = useState("qianwei");
  const [password, setPassword] = useState("123456");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ account, password }),
      });
      if (!res.ok) throw new Error("账号或密码不正确");
      const data = await res.json();
      localStorage.setItem("geo_token", data.access_token);
      router.push("/realm");
    } catch (e: any) {
      setError(e.message || "登录失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-sm mx-auto px-4 py-20">
      <h1 className="text-2xl font-bold text-center text-gray-900 mb-8">{'登录 · 域主看板'}</h1>
      <form className="space-y-4" onSubmit={handleSubmit}>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">账号</label>
          <input type="text" value={account} onChange={(e) => setAccount(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">{'密码'}</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400" required />
        </div>
        {error && <p className="text-sm text-rose-600">{error}</p>}
        <button type="submit" disabled={loading}
          className="w-full bg-blue-600 text-white py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-60">
          {loading ? '登录中...' : '登录'}
        </button>
      </form>
      <p className="text-center text-sm text-gray-500 mt-4">{'还没有账号？'} <Link href="/register" className="text-blue-600 hover:underline">{'注册'}</Link></p>
      <div className='border-t mt-4 pt-3'>
        <div className='text-xs text-slate-400 mb-2'>GEO产业生态</div>
        <div className='flex flex-wrap gap-2'>
          <Link href='/detection' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>检测中心</Link>
          <Link href='/realm' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>域主看板</Link>
          <Link href='/realm/80860de4-5ded-41a3-8a20-f549aab68f5b/explore' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>域主工作台</Link>
        </div>
      </div>
    </div>
  );
}
