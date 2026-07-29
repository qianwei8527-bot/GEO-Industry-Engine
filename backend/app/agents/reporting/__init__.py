"""
GEO-Industry-Engine Agent Report Generator
Sprint 2.2: 将 Agent 原始输出转化为用户可读的战略报告
"""
from typing import Any
from dataclasses import dataclass, field
import datetime

@dataclass
class StrategicReport:
    """企业 GEO 战略分析报告 - 面向企业决策者的商业语言"""
    company_name: str = ""
    generated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    
    # GEO 身份摘要
    geo_identity: dict = field(default_factory=dict)
    
    # 六维度分析
    visibility_assessment: dict = field(default_factory=dict)
    trust_assessment: dict = field(default_factory=dict)
    capability_profile: dict = field(default_factory=dict)
    relationship_network: dict = field(default_factory=dict)
    evidence_foundation: dict = field(default_factory=dict)
    event_timeline: dict = field(default_factory=dict)
    
    # 决策层
    competitive_position: dict = field(default_factory=dict)
    opportunities: list = field(default_factory=list)
    risks: list = field(default_factory=list)
    
    # 行动层
    strategic_recommendations: list = field(default_factory=list)
    ninety_day_plan: list = field(default_factory=list)
    
    # 元数据
    data_sources: list = field(default_factory=list)
    confidence_note: str = ""


class ReportGenerator:
    """将 Context Engine + Decision Engine 原始输出编译为战略报告"""
    
    @staticmethod
    def generate(company_context, decision_result) -> StrategicReport:
        profile = company_context.company
        scoring = company_context.scoring
        
        report = StrategicReport(
            company_name=profile.name,
            geo_identity={
                "geo_id": profile.geo_id or "未分配",
                "entity_type": profile.entity_type or "company",
                "is_verified": profile.is_verified,
                "industry": profile.description[:80] if profile.description else "未填写",
            },
            visibility_assessment=ReportGenerator._build_visibility(decision_result),
            trust_assessment=ReportGenerator._build_trust(company_context),
            capability_profile=ReportGenerator._build_capability(company_context),
            relationship_network=ReportGenerator._build_relationships(company_context),
            evidence_foundation=ReportGenerator._build_evidence(company_context),
            event_timeline=ReportGenerator._build_events(company_context),
            competitive_position=ReportGenerator._build_competitive(decision_result),
            opportunities=ReportGenerator._build_opportunities(decision_result),
            risks=ReportGenerator._build_risks(decision_result),
            strategic_recommendations=ReportGenerator._build_recommendations(decision_result),
            ninety_day_plan=ReportGenerator._build_plan(decision_result, scoring),
            data_sources=["Context Engine", "Decision Engine", "GEO Knowledge Graph"],
            confidence_note=f"基于 {company_context.evidence_count if hasattr(company_context, 'evidence_count') else len(company_context.evidence)} 条证据生成",
        )
        return report
    
    @staticmethod
    def _build_visibility(decision) -> dict:
        scores = decision.get("scores", {})
        vis = scores.get("visibility", {})
        return {
            "score": vis.get("score", 0) if isinstance(vis, dict) else getattr(vis, "score", 0),
            "level": vis.get("level", "N/A") if isinstance(vis, dict) else getattr(vis, "level", "N/A"),
            "interpretation": ReportGenerator._interpret_visibility(vis.get("score", 0) if isinstance(vis, dict) else getattr(vis, "score", 0)),
        }
    
    @staticmethod
    def _build_trust(ctx) -> dict:
        s = ctx.scoring
        return {
            "score": s.trust_score,
            "level": "A" if s.trust_score >= 80 else "B" if s.trust_score >= 60 else "C" if s.trust_score >= 40 else "D",
            "evidence_count": len(ctx.evidence),
            "certified": any(hasattr(e, 'verified') and e.verified for e in ctx.evidence),
            "interpretation": ReportGenerator._interpret_trust(s.trust_score),
        }
    
    @staticmethod
    def _build_capability(ctx) -> dict:
        caps = ctx.capabilities
        return {
            "count": len(caps),
            "items": [{"name": c.name, "level": c.level, "category": c.category} for c in caps],
            "strongest": [c.name for c in caps if c.level >= 3] if caps else [],
            "gaps": "能力数量偏少" if len(caps) < 3 else "能力布局较完整",
        }
    
    @staticmethod
    def _build_relationships(ctx) -> dict:
        rels = ctx.relationships
        return {
            "count": len(rels),
            "partners": [r.target_name for r in rels if r.relation_type == "partner"][:5],
            "network_density": "稀疏" if len(rels) < 3 else "一般" if len(rels) < 8 else "密集",
        }
    
    @staticmethod
    def _build_evidence(ctx) -> dict:
        ev = ctx.evidence
        return {
            "count": len(ev),
            "avg_confidence": round(sum(e.confidence_level for e in ev) / len(ev), 2) if ev else 0,
            "verified_count": sum(1 for e in ev if hasattr(e, 'verified') and e.verified),
        }
    
    @staticmethod
    def _build_events(ctx) -> dict:
        evts = ctx.events
        return {
            "count": len(evts),
            "recent": [{"title": e.title, "date": str(e.event_date), "type": e.event_type} for e in evts[:5]],
        }
    
    @staticmethod
    def _build_competitive(decision) -> dict:
        scores = decision.get("scores", {})
        cp = scores.get("competitive_position", {})
        cg = scores.get("company_growth", {})
        return {
            "position_score": cp.get("score", 0) if isinstance(cp, dict) else getattr(cp, "score", 0),
            "growth_score": cg.get("score", 0) if isinstance(cg, dict) else getattr(cg, "score", 0),
        }
    
    @staticmethod
    def _build_opportunities(decision) -> dict:
        recs = decision.get("recommendations", [])
        ops = [r for r in recs if isinstance(r, dict) and r.get("type") == "opportunity"]
        return ops[:5] if ops else [{"title": "暂无识别到的机会", "description": "补充更多企业数据以发现机会"}]
    
    @staticmethod
    def _build_risks(decision) -> dict:
        recs = decision.get("recommendations", [])
        risks = [r for r in recs if isinstance(r, dict) and r.get("type") == "risk"]
        return risks[:5] if risks else [{"title": "暂无预警风险", "description": "补充竞品和行业数据以进行风险扫描"}]
    
    @staticmethod
    def _build_recommendations(decision) -> list:
        recs = decision.get("recommendations", [])
        return recs[:5] if recs else []
    
    @staticmethod
    def _build_plan(decision, scoring) -> list:
        overall = decision.get("overall", 0)
        recs = decision.get("recommendations", [])
        plan = []
        for i, r in enumerate(recs[:4]):
            plan.append({
                "phase": f"第{i+1}阶段 (第{(i)*30+1}-{(i+1)*30}天)",
                "action": r.get("title", "") if isinstance(r, dict) else str(r),
                "expected_impact": r.get("description", "") if isinstance(r, dict) else "",
            })
        if not plan:
            plan = [
                {"phase": "第1阶段 (1-30天)", "action": "完善企业基础信息", "expected_impact": "提升实体质量评分"},
                {"phase": "第2阶段 (31-60天)", "action": "积累第三方证据", "expected_impact": "提升信任评分"},
                {"phase": "第3阶段 (61-90天)", "action": "扩展产业合作关系", "expected_impact": "提升关系网络密度"},
            ]
        return plan
    
    @staticmethod
    def _interpret_visibility(score) -> str:
        if score >= 80: return "企业在AI搜索引擎中具有很高的可见度，用户通过AI工具能频繁发现该企业"
        if score >= 60: return "企业AI可见度良好，在主流AI平台上有一定曝光，但仍有提升空间"
        if score >= 40: return "企业AI可见度偏低，建议加强结构化数据和权威内容建设"
        return "企业目前在AI搜索生态中几乎不可见，需要从基础信息建设开始"

    @staticmethod
    def _interpret_trust(score) -> str:
        if score >= 80: return "企业可信度很高，拥有充分的第三方证据支撑"
        if score >= 60: return "企业可信度较好，建议补充行业认证和权威引用"
        if score >= 40: return "企业可信度一般，证据数量偏少或来源权威度不足"
        return "企业可信度偏低，缺乏第三方验证信息"
