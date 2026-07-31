'use client';
import { Suspense } from 'react';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { useSearchParams } from 'next/navigation';
import { Save, RefreshCw, FileText } from 'lucide-react';

function ConfigPageInner() {
  const searchParams = useSearchParams();
  const [categories, setCategories] = useState<Record<string,string[]>>({});
  const [selectedCat, setSelectedCat] = useState('');
  const [selectedFile, setSelectedFile] = useState('');
  const [yamlContent, setYamlContent] = useState('');
  const [yamlStr, setYamlStr] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.admin.listConfigs().then(d=>setCategories(d as any)).catch(()=>{});
    const cat = searchParams.get('cat');
    const file = searchParams.get('file');
    if (cat && file) { setSelectedCat(cat); setSelectedFile(file); }
  }, [searchParams]);

  useEffect(() => {
    if (selectedCat && selectedFile) {
      fetch('http://127.0.0.1:8080/api/v1/admin/configs/' + selectedCat + '/' + selectedFile)
        .then(r=>r.json())
        .then(d => { setYamlContent(d); setYamlStr(jsToYaml(d)); })
        .catch(()=>{});
    }
  }, [selectedCat, selectedFile]);

  function jsToYaml(obj: any, indent = ''): string {
    if (obj === null || obj === undefined) return 'null';
    if (typeof obj !== 'object') {
      if (typeof obj === 'string') return JSON.stringify(obj);
      return String(obj);
    }
    if (Array.isArray(obj)) {
      if (obj.length === 0) return '[]';
      return obj.map((item: any) => {
        if (typeof item === 'object' && item !== null && !Array.isArray(item)) {
          const entries = Object.entries(item);
          return indent + '- ' + entries[0]?.[0] + ': ' + JSON.stringify(entries[0]?.[1]);
        }
        return indent + '- ' + JSON.stringify(item);
      }).join('\n');
    }
    const entries = Object.entries(obj);
    if (entries.length === 0) return '{}';
    return entries.map(([k,v]) => {
      if (typeof v === 'object' && v !== null && !Array.isArray(v)) {
        return indent + k + ':\n' + jsToYaml(v, indent + '  ');
      }
      if (Array.isArray(v)) {
        return indent + k + ':\n' + jsToYaml(v, indent + '  ');
      }
      return indent + k + ': ' + (typeof v === 'string' ? JSON.stringify(v) : String(v));
    }).join('\n');
  }

  async function handleSave() {
    setSaving(true); setSaved(false);
    try {
      const parsed = parseSimpleYaml(yamlStr);
      await fetch('http://127.0.0.1:8080/api/v1/admin/configs/' + selectedCat + '/' + selectedFile, {
        method: 'PUT', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ data: parsed }),
      });
      setSaved(true);
    } catch(e) {}
    setSaving(false);
  }

  function parseSimpleYaml(yaml: string): any {
    try { return JSON.parse(yaml); } catch {}
    const result: any = {};
    let currentKey = '';
    for (const line of yaml.split('\n')) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const match = trimmed.match(/^(\w[\w_]*):\s*(.*)$/);
      if (match) {
        const key = match[1]; let val: any = match[2].trim();
        if (val === 'true') val = true; else if (val === 'false') val = false;
        else if (/^\d+\.?\d*$/.test(val)) val = Number(val);
        else if (val.startsWith('"') && val.endsWith('"')) val = val.slice(1,-1);
        result[key] = val;
        currentKey = key;
      }
    }
    return result;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-900 mb-2">配置管理</h1>
      <p className="text-sm text-slate-500 mb-6">编辑 YAML 配置文件，修改后即时热加载生效。修改权重参数无需重启服务。</p>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Category/File Selector */}
        <div className="md:col-span-1 space-y-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-700 mb-3">配置分类</h3>
            {Object.entries(categories).map(([cat, files]) => (
              <button key={cat} onClick={() => { setSelectedCat(cat); setSelectedFile(''); }}
                className={`block w-full text-left px-3 py-2 rounded-lg text-sm mb-1 transition-colors ${
                  selectedCat === cat ? 'bg-blue-50 text-blue-700 font-medium' : 'text-slate-600 hover:bg-slate-50'
                }`}>
                <span className="capitalize">{cat}</span>
                <span className="text-xs text-slate-400 ml-2">({files.length})</span>
              </button>
            ))}
          </div>
          {selectedCat && (
            <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
              <h3 className="text-sm font-semibold text-slate-700 mb-3">文件列表</h3>
              {categories[selectedCat]?.map(f => {
                const name = f.replace('.yaml','');
                return (
                  <button key={f} onClick={() => setSelectedFile(name)}
                    className={`block w-full text-left px-3 py-2 rounded-lg text-sm mb-1 transition-colors ${
                      selectedFile === name ? 'bg-blue-50 text-blue-700 font-medium' : 'text-slate-600 hover:bg-slate-50'
                    }`}>
                    <FileText className="w-3.5 h-3.5 inline mr-2 text-slate-400" />
                    {name}.yaml
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Editor */}
        <div className="md:col-span-2">
          {selectedCat && selectedFile ? (
            <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
              <div className="flex items-center justify-between p-4 border-b border-slate-100 bg-slate-50">
                <div>
                  <span className="text-sm font-semibold text-slate-700">{selectedCat}/{selectedFile}.yaml</span>
                  <span className="text-xs text-slate-400 ml-2">YAML Configuration</span>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => setSaved(false)} className="flex items-center gap-1 px-3 py-1.5 text-xs text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200">
                    <RefreshCw className="w-3 h-3" /> 重置
                  </button>
                  <button onClick={handleSave} disabled={saving}
                    className="flex items-center gap-1 px-4 py-1.5 text-xs text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50">
                    <Save className="w-3 h-3" /> {saving ? '保存中...' : '保存'}
                  </button>
                </div>
              </div>
              <div className="p-4">
                <textarea value={yamlStr} onChange={e => { setYamlStr(e.target.value); setSaved(false); }}
                  className="w-full min-h-[400px] font-mono text-sm p-4 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
                  placeholder="点击左侧文件加载配置..." />
                {saved && <div className="mt-3 text-sm text-green-600 font-medium">已保存 - 配置将在下次请求时生效</div>}
              </div>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center shadow-sm">
              <FileText className="w-12 h-12 text-slate-300 mx-auto mb-4" />
              <p className="text-slate-500">选择左侧分类和文件开始编辑</p>
              <p className="text-xs text-slate-400 mt-1">支持 6 个分类共 {Object.values(categories).reduce((s,f)=>s+f.length,0)} 个 YAML 配置文件</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


export default function AdminConfigPage() { return <Suspense fallback={<div className='text-slate-400'>加载中...</div>}><ConfigPageInner /></Suspense>; }
