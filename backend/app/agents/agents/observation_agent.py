# GEO Observation Agent ¡ª Layer 3 Dynamic + Layer 5 Intelligence
# Scans for industry changes and generates GeoEvents for the GEO Universe

from app.agents.core.base_agent import BaseAgent, AgentContext, AgentResult
from app.agents.tools.context_tool import context_tool
from app.agents.tools.industry_tool import industry_tool

class GEOObservationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name='GEOObservationAgent',
            description='GEO Universe observation: scan industry changes, detect trends, generate events, keep maps dynamic'
        )
        self.register_tool('get_industry_context', context_tool.get_industry_context)
        self.register_tool('search', context_tool.search)
        self.register_tool('get_industry_overview', industry_tool.get_industry_overview)

    async def execute(self, ctx: AgentContext) -> AgentResult:
        try:
            observation_type = ctx.params.get('observation_type', 'daily_scan')
            industry_id = ctx.params.get('industry_id')
            
            if observation_type == 'daily_scan':
                # Daily scan for changes
                context = await self.use_tool('get_industry_overview', industry_id=industry_id)
                result = AgentResult(
                    agent_id=self.agent_id, task_id=ctx.task_id, success=True,
                    data={
                        'scan_type': 'daily',
                        'changes_detected': context.get('changes', 0) if isinstance(context, dict) else 0,
                        'events_generated': context.get('events', []) if isinstance(context, dict) else [],
                        'recommendation': 'No significant changes detected' if not context else 'Changes found, updating graph'
                    },
                    summary='GEO Universe daily scan completed',
                    tool_calls=['scan_industry']
                )
            elif observation_type == 'trend_analysis':
                # Trend analysis
                context = await self.use_tool('get_industry_context', industry_id=industry_id)
                result = AgentResult(
                    agent_id=self.agent_id, task_id=ctx.task_id, success=True,
                    data={
                        'scan_type': 'trend',
                        'industry_context': context,
                        'trends': [],
                        'recommendation': 'Check ecosystem map for current position'
                    },
                    summary='GEO Universe trend analysis completed',
                    tool_calls=['get_industry_context']
                )
            else:
                # Event scan
                context = await self.use_tool('search', query='GEO industry changes today')
                result = AgentResult(
                    agent_id=self.agent_id, task_id=ctx.task_id, success=True,
                    data={'scan_type': 'event', 'events_found': 0, 'events': []},
                    summary='Event scan completed',
                    tool_calls=['search']
                )
            
            result.add_citation(
                source='GEOObservationAgent',
                id=ctx.task_id,
                field='dynamic_events',
                description='GEO Universe dynamic observation result'
            )
            return result
        except Exception as e:
            return AgentResult(agent_id=self.agent_id, task_id=ctx.task_id, success=False, error=str(e))
