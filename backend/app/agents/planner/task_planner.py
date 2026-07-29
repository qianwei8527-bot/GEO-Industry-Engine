# 参考: CrewAI Task Planner + LangChain Plan-and-Execute
from typing import List, Dict
from app.agents.core.base_agent import AgentContext

class TaskPlanner:
    def plan(self, ctx: AgentContext) -> List[Dict]:
        steps = []
        steps.append({'step':1,'action':'call_context_engine','params':ctx.params,'description':'获取产业上下文数据'})
        steps.append({'step':2,'action':'execute_agent','agent':ctx.intent,'params':ctx.params,'description':f'执行{ctx.intent}分析'})
        steps.append({'step':3,'action':'compile_results','description':'整合分析结果并生成报告'})
        return steps

task_planner = TaskPlanner()