import { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: '企业GEO对比 | GEO Industry Engine',
  description: '企业GEO对比',
}

export default function Page() {
  return (
    <div className='max-w-7xl mx-auto px-4 py-8'>
      <h1 className='text-2xl font-bold mb-2'>企业GEO对比</h1>
      <p className='text-slate-500 mb-8'>此页面为架构设计占位，将在开发阶段实现完整功能。</p>

      <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mb-6'>
        <div className='border rounded-lg p-4'>
          <div className='text-sm font-medium mb-1'>页面功能</div>
          <p className='text-xs text-slate-500'>此页面详细设计参见 docs/06-10_页面互联映射.md</p>
        </div>
        <div className='border rounded-lg p-4'>
          <div className='text-sm font-medium mb-1'>关联系统</div>
          <p className='text-xs text-slate-500'>系统关联设计参见 docs/06-11_系统关联架构设计.md</p>
        </div>
      </div>

      <div className='border-t pt-4'>
        <div className='text-xs text-slate-400 mb-2'>相关功能:</div>
        <div className='flex flex-wrap gap-2'>
          <Link href='/detection' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>检测中心</Link>
          <Link href='/certification' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>认证中心</Link>
          <Link href='/navigation' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>产业导航</Link>
          <Link href='/assets' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>数据资产</Link>
          <Link href='/marketplace' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>交易市场</Link>
          <Link href='/intelligence' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>产业情报</Link>
        </div>
      </div>
    </div>
  )
}
