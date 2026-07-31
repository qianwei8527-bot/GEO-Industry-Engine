# GEO-Industry-Engine Industry Analyst Agent - P0-C citations
from app.agents.core.base_agent import BaseAgent, AgentContext, AgentResult
from app.agents.tools.context_tool import context_tool
from app.agents.tools.decision_tool import decision_tool

class IndustryAnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(name='IndustryAnalyst', description='Industry analysis: trends, competitive structure, opportunity identification')
        self.register_tool('get_industry_context', context_tool.get_industry_context)
        self.register_tool('search', context_tool.search)

    async def execute(self, ctx: AgentContext) -> AgentResult:
        try:
            industry_id = ctx.params.get('industry_id')
            context = await self.use_tool('get_industry_context', industry_id=industry_id)

            result = AgentResult(
                agent_id=self.agent_id, task_id=ctx.task_id, success=True,
                data=context,
                summary=f'Industry analysis complete: {len(str(context))} chars',
                tool_calls=['get_industry_context']
            )
            # P0-C: citations
            result.add_citation(source="ContextEngine", id=industry_id or "unknown",
                                field="industry entities, capabilities, relationships",
                                description="Industry context data from knowledge graph")
            return result
        except Exception as e:
            return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error=str(e))
