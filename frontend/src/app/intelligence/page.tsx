import { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: '产业情报 | GEO Industry Engine',
  description: 'GEO产业竞争情报、机会发现与风险预警',
}

export default function IntelligencePage() {
  return (
    <div className='max-w-7xl mx-auto px-4 py-8'>
      <h1 className='text-2xl font-bold mb-2'>产业情报</h1>
      <p className='text-slate-500 mb-8'>Industry Intelligence Center — 竞争情报、机会发现、风险预警</p>

      <div className='grid grid-cols-1 md:grid-cols-3 gap-6 mb-8'>
        {/* 竞争情报 */}
        <div className='border rounded-lg p-6 hover:shadow-md transition-shadow'>
          <div className='text-lg font-semibold mb-2'>竞争情报</div>
          <p className='text-sm text-slate-500 mb-4'>竞品变化、企业位置变化、竞争格局、市场份额变化、能力变化</p>
          <Link href='/intelligence/competitors' className='text-sm text-blue-600 hover:underline'>
            查看竞争对手分析 →
          </Link>
        </div>

        {/* 机会情报 */}
        <div className='border rounded-lg p-6 hover:shadow-md transition-shadow'>
          <div className='text-lg font-semibold mb-2'>机会情报</div>
          <p className='text-sm text-slate-500 mb-4'>行业趋势、新兴赛道、产业空白、能力缺口、潜在合作、新市场机会</p>
          <Link href='/intelligence/opportunities' className='text-sm text-blue-600 hover:underline'>
            发现产业机会 →
          </Link>
        </div>

        {/* 风险情报 */}
        <div className='border rounded-lg p-6 hover:shadow-md transition-shadow'>
          <div className='text-lg font-semibold mb-2'>风险情报</div>
          <p className='text-sm text-slate-500 mb-4'>行业风险、技术风险、政策风险、竞争风险、GEO表现退化风险</p>
          <Link href='/intelligence/risks' className='text-sm text-blue-600 hover:underline'>
            查看风险预警 →
          </Link>
        </div>
      </div>

      {/* 快捷入口 */}
      <div className='border-t pt-6'>
        <h2 className='text-lg font-semibold mb-4'>快捷分析</h2>
        <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
          <div className='border rounded p-4'>
            <div className='text-sm font-medium'>行业趋势速览</div>
            <p className='text-xs text-slate-400 mt-1'>当前 GEO 产业热门方向与增长指标</p>
          </div>
          <div className='border rounded p-4'>
            <div className='text-sm font-medium'>企业GEO表现对比</div>
            <p className='text-xs text-slate-400 mt-1'>同业企业AI可见度与排名变化</p>
          </div>
          <div className='border rounded p-4'>
            <div className='text-sm font-medium'>潜在机会扫描</div>
            <p className='text-xs text-slate-400 mt-1'>基于产业空白的自动机会识别</p>
          </div>
          <div className='border rounded p-4'>
            <div className='text-sm font-medium'>风险监控面板</div>
            <p className='text-xs text-slate-400 mt-1'>持续监控企业GEO表现与行业变化</p>
          </div>
        </div>

          {/* 关联系统 */}
          <div className='border-t mt-6 pt-3 mb-4'>
            <div className='text-xs text-slate-400 mb-2'>相关功能:</div>
            <div className='flex flex-wrap gap-2'>
              <Link href='/detection' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>受影响实体</Link>
              <Link href='/navigation' className='text-xs px-2 py-1 bg-blue-50 rounded hover:bg-blue-100'>行业趋势地图</Link>
            </div>
          </div>

      </div>
    </div>
  )
}
