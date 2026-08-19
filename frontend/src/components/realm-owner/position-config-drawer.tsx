"use client";

import { useState } from "react";
import { Loader2, MapPin, Save } from "lucide-react";
import RealmDrawer from "./drawer";
import type { MapNodeDefinition } from "@/lib/realm-owner/config";
import type { RealmOwnerHomeViewModel } from "@/lib/realm-owner/types";

interface PositionConfigDrawerProps {
  open: boolean;
  onClose: () => void;
  realmName: string;
  nodes: MapNodeDefinition[];
  current: RealmOwnerHomeViewModel["map"]["ownerPosition"];
  onSaveDraft: (nodeId: string) => void;
}

export default function PositionConfigDrawer({
  open,
  onClose,
  realmName,
  nodes,
  current,
  onSaveDraft,
}: PositionConfigDrawerProps) {
  const [selected, setSelected] = useState(current.nodeIds[0] || "");
  const [binding, setBinding] = useState("");
  const [sourceNote, setSourceNote] = useState("");
  const [saving, setSaving] = useState(false);

  function save() {
    if (!selected) return;
    setSaving(true);
    window.setTimeout(() => {
      onSaveDraft(selected);
      setSaving(false);
      onClose();
    }, 250);
  }

  return (
    <RealmDrawer
      open={open}
      onClose={onClose}
      title="确认我的位置"
      description={`为 ${realmName} 选择当前能力域点；草稿不会写入生产状态。`}
      footer={
        <div className="flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            取消
          </button>
          <button
            type="button"
            onClick={save}
            disabled={!selected || saving}
            className="inline-flex items-center gap-2 rounded-lg bg-teal-700 px-3 py-2 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-60"
          >
            {saving ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Save className="h-4 w-4" aria-hidden="true" />}
            保存为草稿
          </button>
        </div>
      }
    >
      <div className="space-y-4">
        <fieldset>
          <legend className="text-xs font-medium text-slate-700">当前能力域点</legend>
          <div className="mt-2 grid grid-cols-2 gap-2">
            {nodes.map((node, index) => (
              <label
                key={node.id}
                className={`flex items-center gap-2 rounded-lg border px-2.5 py-2 text-xs font-medium cursor-pointer ${
                  selected === node.id ? "border-teal-600 bg-teal-50 text-teal-800" : "border-slate-200 bg-white text-slate-600 hover:border-slate-300"
                }`}
              >
                <input
                  type="radio"
                  name="position-node"
                  value={node.id}
                  checked={selected === node.id}
                  onChange={() => setSelected(node.id)}
                  className="h-3.5 w-3.5 text-teal-600 focus:ring-teal-500"
                />
                <span className="truncate">{index + 1}. {node.label}</span>
              </label>
            ))}
          </div>
        </fieldset>

        <div>
          <label htmlFor="position-binding" className="block text-xs font-medium text-slate-700">绑定企业、品牌、产品或团队</label>
          <input
            id="position-binding"
            value={binding}
            onChange={(event) => setBinding(event.target.value)}
            placeholder="填写真实主体名称"
            className="mt-1.5 w-full rounded-lg border border-slate-300 bg-slate-50 px-2.5 py-2 text-sm focus:border-teal-600 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-100"
          />
        </div>

        <div>
          <label htmlFor="position-source" className="block text-xs font-medium text-slate-700">来源或 Evidence 说明</label>
          <textarea
            id="position-source"
            value={sourceNote}
            onChange={(event) => setSourceNote(event.target.value)}
            rows={3}
            placeholder="记录来源；不会自动验证"
            className="mt-1.5 w-full rounded-lg border border-slate-300 bg-slate-50 px-2.5 py-2 text-sm focus:border-teal-600 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-100"
          />
        </div>

        <div className="flex items-start gap-2 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2.5">
          <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-blue-600" aria-hidden="true" />
          <p className="text-[11px] leading-5 text-blue-700">
            当前没有位置 API，草稿只保存在本会话。confirmed 需要后端位置状态机与域主审批。
          </p>
        </div>
      </div>
    </RealmDrawer>
  );
}