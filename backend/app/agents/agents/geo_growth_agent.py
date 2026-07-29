# 参考: HubSpot 增长引擎 + Ahrefs SEO优化建议
from app.agents.core.base_agent import BaseAgent, AgentContext, AgentResult
from app.agents.tools.context_tool import context_tool
from app.agents.tools.decision_tool import decision_tool

class GEOGrowthAgent(BaseAgent):
    def __init__(self):
        super().__init__(name='GEOGrowth',description='GEO增长：优化路径、内容策略、AI搜索增长建议')
        self.register_tool('get_company_context',context_tool.get_company_context)
        self.register_tool('get_opportunity',decision_tool.get_opportunity)
        self.register_tool('get_roadmap',decision_tool.get_roadmap)

    async def execute(self, ctx: AgentContext) -> AgentResult:
        try:
            cid = ctx.params.get('company_id')
            context = await self.use_tool('get_company_context',company_id=cid)
            opp = await self.use_tool('get_opportunity',company_id=cid)
            roadmap = await self.use_tool('get_roadmap',company_id=cid)
            data = {'context':context,'opportunities':opp,'roadmap':roadmap}
            return AgentResult(agent_id=self.agent_id,task_id=ctx.task_id,success=True,data=data,summary='GEO增长方案已生成',tool_calls=['get_company_context','get_opportunity','get_roadmap'])
        except Exception as e:
            return AgentResult(agent_id=self.agent_id,task_id=ctx.task_id,success=False,error=str(e))