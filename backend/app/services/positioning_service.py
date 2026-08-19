"""V10.6-R2 local positioning draft engine.

Deterministic, explainable and configurable. It never fabricates market
share, industry rank or percentile. Final positioning belongs to the owner.
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Dict, List

import yaml


def _load_positioning_config() -> Dict:
    p = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "config", "universe", "positioning.yaml",
    )
    if os.path.exists(p):
        raw = open(p, encoding="utf-8").read()
        data = yaml.safe_load(raw) or {}
        data["config_hash"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        return data
    return {"version": "1.0.0", "config_hash": "missing", "business_stages": []}


def _field(fields: List[Dict], key: str) -> Dict:
    return next((f for f in fields if f.get("key") == key), {})


def _value(fields: List[Dict], key: str) -> str:
    value = _field(fields, key).get("value")
    return "" if value in (None, "待补充") else str(value).strip()


def _known(fields: List[Dict], key: str) -> bool:
    field = _field(fields, key)
    return field.get("status") not in ("unknown", None) and bool(_value(fields, key))


class PositioningService:
    def __init__(self):
        self.config = _load_positioning_config()

    def generate(self, fields: List[Dict]) -> Dict:
        industry = _value(fields, "industry_track")
        brand = _value(fields, "brand_name") or _value(fields, "enterprise_entity")
        customer = _value(fields, "target_customer")
        region = _value(fields, "service_region")
        product = _value(fields, "product_service")
        channels = _value(fields, "existing_channels")
        problem = _value(fields, "client_problem")
        conversion = _value(fields, "conversion_goals")
        stage_raw = _value(fields, "business_stage")
        advantages = _value(fields, "advantages")
        gaps = _value(fields, "gaps")
        risks = _value(fields, "risks")

        stage = self._resolve_stage(stage_raw, problem, product, customer)
        unknowns = [
            key for key in ("industry_track", "target_customer", "service_region", "existing_channels", "business_stage")
            if not _known(fields, key)
        ]
        facts = [
            {"key": key, "label": _field(fields, key).get("label"), "value": _value(fields, key)}
            for key in ("brand_name", "enterprise_entity", "product_service", "client_problem", "target_customer", "service_region")
            if _known(fields, key)
        ]
        inferred = [
            {"key": key, "value": _value(fields, key)}
            for key in ("existing_channels", "conversion_goals", "business_stage")
            if _field(fields, key).get("status") == "inferred" and _value(fields, key)
        ]

        priority = gaps or unknowns[0] if gaps or unknowns else "客户档案已确认，可进入项目与计划"
        industry_position = {
            "industry_track": industry or "待补充",
            "industry_chain_role": "待补充",
            "target_customer": customer or "待补充",
            "product_capability_position": product or "待补充",
            "service_region": region or "待补充",
            "existing_channels": channels or "待补充",
            "confirmed_facts": facts,
            "inferred_items": inferred,
            "unknown_items": unknowns,
            "basis": [
                "本地规则模板",
                "仅使用已标记 observed/inferred 的字段",
                "未提供真实行业基准时不输出排名或百分位",
            ],
            "rule_version": str(self.config.get("version", "1.0.0")),
            "config_hash": self.config.get("config_hash"),
        }
        business_position = {
            "current_stage": stage,
            "client_product_clarity": "partial" if not customer or not product else "clear",
            "evidence_completeness": "partial" if unknowns else "ready",
            "channel_maturity": "unknown" if not channels else "observed",
            "geo_baseline": "待补充",
            "conversion_funnel_status": "unknown" if not conversion else "observed",
            "advantages": advantages or "待补充",
            "key_gaps": gaps or unknowns or ["待补充"],
            "risks": risks or ["待补充"],
            "next_stage_entry": self._next_stage_entry(stage, unknowns),
        }
        conclusion = {
            "who_we_are": brand or "待补充",
            "serve_who": customer or "待补充",
            "in_region": region or "待补充",
            "solve_problem": problem or "待补充",
            "provide": product or "待补充",
            "evidence_basis": len(facts),
            "current_stage": stage,
            "main_gap": gaps or (unknowns[0] if unknowns else "无"),
            "priority_direction": priority,
        }
        payload = {
            "industry_position": industry_position,
            "business_position": business_position,
            "conclusion": conclusion,
            "rule_version": str(self.config.get("version", "1.0.0")),
            "config_hash": self.config.get("config_hash"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        hash_payload = {key: value for key, value in payload.items() if key != "generated_at"}
        payload["positioning_hash"] = hashlib.sha256(
            json.dumps(hash_payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()[:32]
        return payload

    def _resolve_stage(self, stage_raw: str, problem: str, product: str, customer: str) -> str:
        if stage_raw:
            return stage_raw
        if any(token in (problem or "") for token in ("从零", "新公司", "无渠道")):
            return "入场准备期"
        if product and customer:
            return "初步验证期"
        return "待补充"

    def _next_stage_entry(self, stage: str, unknowns: List[str]) -> str:
        if unknowns:
            return f"补齐 {unknowns[0]} 后进入下一阶段判断"
        if stage == "入场准备期":
            return "建立真实试点并完成首轮验证"
        return "基于真实结果确认后进入下一阶段"


def get_positioning_service() -> PositioningService:
    return PositioningService()
