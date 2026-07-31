# GEO-Industry-Engine Data Analyst Agent - P0-C citations
from app.agents.core.base_agent import BaseAgent, AgentContext, AgentResult
from app.agents.tools.context_tool import context_tool

class DataAnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(name='DataAnalyst', description='Data intelligence: discover missing companies, capabilities, relationships, evidence')
        self.register_tool('search', context_tool.search)

    async def execute(self, ctx: AgentContext) -> AgentResult:
        try:
            results = await self.use_tool('search', query=ctx.input_query, limit=10)
            gaps = self._analyze_gaps(results)

            result = AgentResult(
                agent_id=self.agent_id, task_id=ctx.task_id, success=True,
                data={'results': results, 'gaps': gaps},
                summary=f'Data scan complete, found {len(gaps)} gaps',
                tool_calls=['search']
            )
            # P0-C: citations
            result.add_citation(source="ContextEngine", id="search",
                                field="entities, capabilities",
                                description=f"Search results for: {ctx.input_query}")
            return result
        except Exception as e:
            return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error=str(e))

    def _analyze_gaps(self, results: list) -> list:
        gaps = []
        if not results:
            gaps.append({'type': 'data_coverage', 'severity': 'high',
                         'message': 'Industry data coverage insufficient, recommend supplementing company and industry data'})
        gaps.append({'type': 'evidence', 'severity': 'medium',
                     'message': 'Third-party evidence insufficient, recommend supplementing certifications and case studies'})
        return gaps
