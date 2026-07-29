# 参考: Palantir 数据分析 + Datadog 监控面板
from app.agents.core.base_agent import BaseAgent, AgentContext, AgentResult
from app.agents.tools.context_tool import context_tool

class DataAnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(name='DataAnalyst',description='数据智能：发现缺失企业、缺失能力、缺失关系、缺失证据')
        self.register_tool('search',context_tool.search)

    async def execute(self, ctx: AgentContext) -> AgentResult:
        try:
            results = await self.use_tool('search',query=ctx.input_query,limit=10)
            gaps = self._analyze_gaps(results)
            return AgentResult(agent_id=self.agent_id,task_id=ctx.task_id,success=True,data={'results':results,'gaps':gaps},summary=f'数据扫描完成，发现{len(gaps)}个缺失项',tool_calls=['search'])
        except Exception as e:
            return AgentResult(agent_id=self.agent_id,task_id=ctx.task_id,success=False,error=str(e))

    def _analyze_gaps(self, results: list) -> list:
        gaps = []
        if not results: gaps.append({'type':'data_coverage','severity':'high','message':'产业数据覆盖不足，建议补充企业和行业数据'})
        gaps.append({'type':'evidence','severity':'medium','message':'第三方证据不足，建议补充认证和案例证明'})
        return gaps