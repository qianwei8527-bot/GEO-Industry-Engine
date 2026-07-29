# 参考: CB Insights 行业分析 Agent + LinkedIn 产业洞察
from app.agents.core.base_agent import BaseAgent, AgentContext, AgentResult
from app.agents.tools.context_tool import context_tool
from app.agents.tools.decision_tool import decision_tool

class IndustryAnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(name='IndustryAnalyst' ,description='行业分析：产业趋势、竞争结构、机会识别')
        self.register_tool('get_industry_context', context_tool.get_industry_context)
        self.register_tool('search', context_tool.search)

    async def execute(self, ctx: AgentContext) -> AgentResult:
        try:
            industry_id = ctx.params.get('industry_id')
            context = await self.use_tool('get_industry_context', industry_id=industry_id)
            return AgentResult(agent_id=self.agent_id,task_id=ctx.task_id,success=True,data=context,summary=f'行业分析完成: {len(context.get(chr(34)+chr(34),[]))}条数据',tool_calls=['get_industry_context'])
        except Exception as e:
            return AgentResult(agent_id=self.agent_id,task_id=ctx.task_id,success=False,error=str(e))