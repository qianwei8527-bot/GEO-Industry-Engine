# GEO-Industry-Engine Company Intelligence Agent
# Sprint 2.2 + P0-C: structured strategic report with mandatory citations
from app.agents.core.base_agent import BaseAgent, AgentContext, AgentResult
from app.agents.tools.context_tool import context_tool
from app.agents.tools.decision_tool import decision_tool
from app.agents.reporting import ReportGenerator


class CompanyIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="CompanyIntelligence", description="Enterprise profile: strengths, gaps, competitive positioning, strategic roadmap")
        self.register_tool("get_company_context", context_tool.get_company_context)
        self.register_tool("get_geo_score", decision_tool.get_geo_score)

    async def execute(self, ctx: AgentContext) -> AgentResult:
        try:
            cid = ctx.params.get("company_id")
            if not cid:
                return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error="Missing company_id parameter")

            # Step 1: Get company context
            context = await self.use_tool("get_company_context", company_id=cid)
            if isinstance(context, dict) and context.get("error"):
                return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error=context["error"])

            # Step 2: Get decision scores
            score = await self.use_tool("get_geo_score", company_id=cid)
            if isinstance(score, dict) and score.get("error"):
                return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error=score["error"])

            # Step 3: Generate strategic report
            report = ReportGenerator.generate(context, score)

            result = AgentResult(
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
                summary=f"GEO Strategic Report: {report.company_name} | Overall {score.get('overall', 0)} | {len(report.opportunities)} chances {len(report.risks)} risks",
                tool_calls=["get_company_context", "get_geo_score", "ReportGenerator"],
            )

            # P0-C: Add mandatory citations
            result.add_citation(source="Entity", id=cid, field="name, description, entity_type, is_verified",
                                description="Company profile data from knowledge graph")
            result.add_citation(source="DecisionEngine", id=cid, field="scores",
                                description="GEO scoring from Decision Engine (visibility, trust, capability, competitive_position)")
            result.add_citation(source="Evidence", id=cid, field="evidence_count, confidence_levels",
                                description=f"Evidence foundation: {report.evidence_foundation.get('count', 0)} records")
            result.add_citation(source="ContextEngine", id=cid, field="capabilities, relationships, events",
                                description=f"Context: {report.capability_profile.get('count', 0)} capabilities, {report.relationship_network.get('count', 0)} relationships")

            return result

        except Exception as e:
            return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error=str(e))
