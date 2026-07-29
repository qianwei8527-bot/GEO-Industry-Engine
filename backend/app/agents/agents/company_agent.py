# GEO-Industry-Engine Company Intelligence Agent
# Sprint 2.2: 输出结构化战略报告，非原始 JSON dump
from app.agents.core.base_agent import BaseAgent, AgentContext, AgentResult
from app.agents.tools.context_tool import context_tool
from app.agents.tools.decision_tool import decision_tool
from app.agents.reporting import ReportGenerator

class CompanyIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="CompanyIntelligence", description="企业画像：优势分析、短板发现、竞争定位、战略路线图")
        self.register_tool("get_company_context", context_tool.get_company_context)
        self.register_tool("get_geo_score", decision_tool.get_geo_score)

    async def execute(self, ctx: AgentContext) -> AgentResult:
        try:
            cid = ctx.params.get("company_id")
            if not cid:
                return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error="缺少 company_id 参数")

            # Step 1: 获取企业上下文
            context = await self.use_tool("get_company_context", company_id=cid)
            if isinstance(context, dict) and context.get("error"):
                return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error=context["error"])

            # Step 2: 获取决策评分
            score = await self.use_tool("get_geo_score", company_id=cid)
            if isinstance(score, dict) and score.get("error"):
                return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error=score["error"])

            # Step 3: 生成战略报告
            report = ReportGenerator.generate(context, score)

            return AgentResult(
                agent_id=self.agent_id,
                task_id=ctx.task_id,
                success=True,
                data={
                    "report": {
                        "company_name": report.company_name,
                        "geo_identity": report.geo_identity,
                        "geo_score": {
                            "overall": score.get("overall", 0),
                            "weights_source": score.get("weights_source", ""),
                        },
                        "visibility": report.visibility_assessment,
                        "trust": report.trust_assessment,
                        "capability": report.capability_profile,
                        "relationships": report.relationship_network,
                        "evidence": report.evidence_foundation,
                        "events": report.event_timeline,
                        "competitive_position": report.competitive_position,
                        "opportunities": report.opportunities,
                        "risks": report.risks,
                        "recommendations": report.strategic_recommendations,
                        "ninety_day_plan": report.ninety_day_plan,
                        "confidence_note": report.confidence_note,
                    },
                    "raw_context": context,
                    "raw_decision": score,
                },
                summary=f"GEO战略报告: {report.company_name} | 总分 {score.get('overall', 0)} | 机会 {len(report.opportunities)} 风险 {len(report.risks)}",
                tool_calls=["get_company_context", "get_geo_score", "ReportGenerator"],
            )
        except Exception as e:
            return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error=str(e))
