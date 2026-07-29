'use client';
import { useState } from 'react';
import Link from 'next/link';

export default function RegisterPage() {
  return (
    <div className="max-w-sm mx-auto px-4 py-20">
      <h1 className="text-2xl font-bold text-center text-gray-900 mb-8">{'注册 GEO 账户'}</h1>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">{'昵称'}</label>
          <input type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input type="email" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">{'密码'}</label>
          <input type="password" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400" />
        </div>
        <button className="w-full bg-blue-600 text-white py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700">{'注册'}</button>
        <p className="text-center text-sm text-gray-500">{'已有账号？'} <Link href="/login" className="text-blue-600 hover:underline">{'登录'}</Link></p>
          {/* GEO Ecosystem */}
          <div className='border-t mt-4 pt-3'>
            <div className='text-xs text-slate-400 mb-2'>GEO产业生态:</div>
            <div className='flex flex-wrap gap-2'>
              <Link href='/detection' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>检测中心</Link>
              <Link href='/navigation' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>产业导航</Link>
            </div>
          </div>
      </div>
    </div>
  );
}
